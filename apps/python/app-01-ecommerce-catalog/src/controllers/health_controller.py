from flask import jsonify

from src.config.db_mongo import CatalogDocumentStore
from src.config.kafka_client import event_publisher
from src.config.search_client import SearchClient


def health():
    return jsonify(
        {
            "status": "ok",
            "storage": "sqlite-fallback",
            "document_store": CatalogDocumentStore().describe(),
            "search": SearchClient().url,
            "broker": event_publisher.broker,
        }
    )
