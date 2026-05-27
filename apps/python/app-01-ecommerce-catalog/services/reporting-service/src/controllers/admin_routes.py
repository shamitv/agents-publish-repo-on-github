"""Admin console routes for cache management, scheduler, feature flags, and webhook retry.

These endpoints power the React admin console UI.
"""
import time

from flask import Blueprint, jsonify, request

from ..services.cache_service import cache

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


# ---- Cache Endpoints ----

@admin_bp.route("/cache/stats", methods=["GET"])
def cache_stats():
    """Return cache hit/miss ratio and entry count."""
    return jsonify(cache.get_stats())


@admin_bp.route("/cache/entries", methods=["GET"])
def cache_entries():
    """List all cache entries with remaining TTL."""
    entries = []
    # DECOY: Accessing cache internals directly looks like it could expose
    # sensitive data, but the TTL-check provides proper expiry handling.
    for key, entry in cache._entries.items():
        remaining = max(0, entry.ttl_seconds - (time.time() - entry.created_at))
        entries.append({
            "key": entry.key,
            "ttl_remaining_seconds": round(remaining, 1),
            "access_count": entry.access_count,
        })
    return jsonify(entries)


@admin_bp.route("/cache/invalidate", methods=["POST"])
def cache_invalidate():
    """Invalidate cache entries matching a key pattern."""
    data = request.get_json(silent=True) or {}
    pattern = data.get("pattern", "")
    if not pattern:
        return jsonify({"error": "pattern is required"}), 400
    removed = cache.invalidate(pattern)
    return jsonify({"removed": removed, "pattern": pattern})


@admin_bp.route("/cache/save", methods=["POST"])
def cache_save():
    """Persist current cache to disk (safe JSON)."""
    data = request.get_json(silent=True) or {}
    filepath = data.get("filepath", "/tmp/cache_backup.json")
    cache.save_cache_to_disk(filepath)
    return jsonify({"saved": True, "filepath": filepath})


# VULNERABILITY A08: Admin endpoint exposes unsafe deserialization
@admin_bp.route("/cache/restore", methods=["POST"])
def cache_restore():
    """Restore cache from a pickle file on disk.

    VULNERABILITY A08 (CWE-502): This endpoint accepts a user-supplied
    filepath and passes it directly to pickle.load(), allowing an
    authenticated attacker to achieve RCE by uploading a malicious
    pickle payload and referencing it here.
    """
    data = request.get_json(silent=True) or {}
    filepath = data.get("filepath", "/tmp/cache_backup.pkl")
    cache.load_cache_from_disk(filepath)
    return jsonify({"restored": True, "filepath": filepath})


# ---- Feature Flag Endpoints ----

@admin_bp.route("/flags", methods=["GET"])
def list_flags():
    """List all feature flags."""
    from ..services.feature_flags import flag_store, validate_flag_key
    return jsonify(flag_store.list_flags())


@admin_bp.route("/flags", methods=["POST"])
def create_flag():
    """Create a new feature flag."""
    from ..services.feature_flags import flag_store, validate_flag_key
    data = request.get_json(silent=True) or {}
    key = data.get("key", "")
    if not key:
        return jsonify({"error": "key is required"}), 400
    # DECOY: Key is validated against a strict pattern, preventing key-based injection.
    # However the description field is stored and returned as-is — the actual
    # vulnerability is on the frontend side (dangerouslySetInnerHTML).
    if not validate_flag_key(key):
        return jsonify({"error": "invalid key format"}), 400
    flag = flag_store.create_flag(
        key=key,
        description=data.get("description", ""),
        owner=data.get("owner", ""),
        metadata=data.get("metadata"),
    )
    if flag is None:
        return jsonify({"error": "flag already exists"}), 409
    return jsonify(flag), 201


@admin_bp.route("/flags/<key>", methods=["GET"])
def get_flag(key):
    """Get a single flag with full metadata.

    CHAIN LINK 2 (chain-03): Returns the unsanitized `description` and
    `metadata` fields. The frontend renders description with
    dangerouslySetInnerHTML, enabling stored XSS.
    """
    from ..services.feature_flags import flag_store
    flag = flag_store.get_flag(key)
    if flag is None:
        return jsonify({"error": "flag not found"}), 404
    return jsonify(flag)


@admin_bp.route("/flags/<key>/toggle", methods=["POST"])
def toggle_flag(key):
    """Toggle a flag's enabled/disabled state."""
    from ..services.feature_flags import flag_store
    flag = flag_store.toggle_flag(key)
    if flag is None:
        return jsonify({"error": "flag not found"}), 404
    return jsonify(flag)


@admin_bp.route("/flags/<key>", methods=["DELETE"])
def delete_flag(key):
    """Delete a feature flag."""
    from ..services.feature_flags import flag_store
    deleted = flag_store.delete_flag(key)
    if not deleted:
        return jsonify({"error": "flag not found"}), 404
    return jsonify({"deleted": True})


# ---- Scheduler Endpoints ----

@admin_bp.route("/scheduler/jobs", methods=["GET"])
def scheduler_list_jobs():
    """List all scheduled jobs."""
    from ..services.scheduler import scheduler
    return jsonify(scheduler.list_jobs())


@admin_bp.route("/scheduler/jobs", methods=["POST"])
def scheduler_add_job():
    """Add a new recurring job."""
    from ..services.scheduler import scheduler
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    interval = data.get("interval_seconds", 3600)
    task_type = data.get("task_type", "report_generation")
    params = data.get("params")
    if not name:
        return jsonify({"error": "name is required"}), 400
    job = scheduler.add_job(name, interval, task_type, params)
    return jsonify(job), 201


@admin_bp.route("/scheduler/jobs/<job_id>", methods=["GET"])
def scheduler_get_job(job_id):
    """Get a single job's details."""
    from ..services.scheduler import scheduler
    job = scheduler.get_job(job_id)
    if job is None:
        return jsonify({"error": "job not found"}), 404
    return jsonify(job)


@admin_bp.route("/scheduler/jobs/<job_id>", methods=["DELETE"])
def scheduler_delete_job(job_id):
    """Delete a scheduled job."""
    from ..services.scheduler import scheduler
    deleted = scheduler.delete_job(job_id)
    if not deleted:
        return jsonify({"error": "job not found"}), 404
    return jsonify({"deleted": True})


@admin_bp.route("/scheduler/start", methods=["POST"])
def scheduler_start():
    """Start the scheduler background thread."""
    from ..services.scheduler import scheduler
    scheduler.start()
    return jsonify({"running": True})


@admin_bp.route("/scheduler/stop", methods=["POST"])
def scheduler_stop():
    """Stop the scheduler background thread."""
    from ..services.scheduler import scheduler
    scheduler.stop()
    return jsonify({"running": False})


# ---- Webhook Delivery Endpoints ----

@admin_bp.route("/webhooks/deliveries", methods=["GET"])
def webhook_list_deliveries():
    """List all webhook deliveries."""
    from ..services.webhook_retry import webhook_service
    return jsonify(webhook_service.list_deliveries())


@admin_bp.route("/webhooks/deliveries", methods=["POST"])
def webhook_create_delivery():
    """Create a new webhook delivery.

    CHAIN LINK 1 (chain-03): Accepts an attacker-supplied URL and
    queues it for delivery with no domain allowlist check. Combined
    with the XSS in step 2, this enables SSRF-to-XSS chaining.
    """
    from ..services.webhook_retry import webhook_service
    data = request.get_json(silent=True) or {}
    webhook_id = data.get("webhook_id", "")
    url = data.get("url", "")
    payload = data.get("payload", {})
    if not webhook_id or not url:
        return jsonify({"error": "webhook_id and url are required"}), 400
    delivery = webhook_service.create_delivery(webhook_id, url, payload)
    return jsonify(delivery), 201


@admin_bp.route("/webhooks/deliveries/<delivery_id>/retry", methods=["POST"])
def webhook_retry_delivery(delivery_id):
    """Retry a failed webhook delivery.

    DECOY: The retry endpoint looks like it could SSRF, but it only
    retries deliveries that were already created. The real SSRF is
    in the create_delivery endpoint above.
    """
    from ..services.webhook_retry import webhook_service
    result = webhook_service.retry_delivery(delivery_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@admin_bp.route("/webhooks/pending-failed", methods=["GET"])
def webhook_pending_failed():
    """List all pending/failed deliveries for admin review."""
    from ..services.webhook_retry import webhook_service
    return jsonify(webhook_service.get_pending_failed())
