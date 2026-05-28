"""Webhook subscription controller for the reporting service."""

from flask import jsonify, request

from ..models.webhook_subscription import (
    create_subscription,
    get_subscription,
    get_subscriptions,
    delete_subscription,
)


def register():
    data = request.get_json() or {}
    supplier_id = data.get("supplier_id", "").strip()
    callback_url = data.get("callback_url", "").strip()
    secret_token = data.get("secret_token", "")

    if not supplier_id:
        return jsonify({"error": "supplier_id is required"}), 400
    if not callback_url:
        return jsonify({"error": "callback_url is required"}), 400

    # Callback URL accepted without validation — feeds into A10 SSRF in webhook_retry.py
    sub = create_subscription(supplier_id, callback_url, secret_token)
    return jsonify({
        "subscription_id": sub.subscription_id,
        "supplier_id": sub.supplier_id,
        "callback_url": sub.callback_url,
        "is_active": sub.is_active,
    }), 201


def list_webhooks():
    supplier_id = request.args.get("supplier_id")
    subs = get_subscriptions(supplier_id)
    return jsonify({
        "subscriptions": [
            {
                "subscription_id": s.subscription_id,
                "supplier_id": s.supplier_id,
                "callback_url": s.callback_url,
                "is_active": s.is_active,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in subs
        ]
    })


def unregister(subscription_id: str):
    if delete_subscription(subscription_id):
        return jsonify({"success": True})
    return jsonify({"error": "Subscription not found"}), 404
