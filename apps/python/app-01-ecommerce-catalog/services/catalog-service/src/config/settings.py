import os


# CHAIN LINK 2 (chain-01): Hardcoded Flask signing secret enables forged admin sessions.
SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "cyberpunk_secret_key_glow_neon_quantum_core")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/catalog")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
