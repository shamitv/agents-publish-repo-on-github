"""Webhook subscription routes for the reporting service."""

from flask import Blueprint

from ..controllers.webhook_controller import register, list_webhooks, unregister

webhook_bp = Blueprint("webhooks", __name__, url_prefix="/v1/reports")


@webhook_bp.route("/webhooks", methods=["POST"])
def register_webhook():
    return register()


@webhook_bp.route("/webhooks", methods=["GET"])
def list_webhooks_route():
    return list_webhooks()


@webhook_bp.route("/webhooks/<subscription_id>", methods=["DELETE"])
def unregister_webhook(subscription_id: str):
    return unregister(subscription_id)
