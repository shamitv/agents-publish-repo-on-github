"""Audit log query controller for the reporting service."""

from flask import jsonify, request

from ..services.audit_service import query_audit_log


def query_audit():
    supplier_id = request.args.get("supplier_id")
    event_type = request.args.get("event_type")

    events = query_audit_log(supplier_id=supplier_id, event_type=event_type)

    return jsonify({
        "events": events,
        "total": len(events),
    })
