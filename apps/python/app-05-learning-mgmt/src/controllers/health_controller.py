from flask import jsonify

from src.config.db_sql import get_db
from src.config.db_mongo import get_mongo_client
from src.config.kafka_client import event_publisher


def health():
    pg_ok = False
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                pg_ok = True
    except Exception:
        pass

    mongo_ok = False
    try:
        client = get_mongo_client()
        if client:
            client.admin.command("ping")
            mongo_ok = True
    except Exception:
        pass

    kafka_ok = event_publisher._get_producer() is not None

    return jsonify({
        "status": "ok",
        "postgresql": "connected" if pg_ok else "disconnected",
        "mongodb": "connected" if mongo_ok else "disconnected",
        "kafka": "connected" if kafka_ok else "disconnected",
    })
