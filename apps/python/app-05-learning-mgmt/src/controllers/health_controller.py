from flask import jsonify

from src.config.db_mongo import QuizDocumentStore
from src.config.kafka_client import event_publisher


def health():
    return jsonify({"status": "ok", "storage": "sqlite-fallback", "document_store": QuizDocumentStore().describe(), "broker": event_publisher.broker})
