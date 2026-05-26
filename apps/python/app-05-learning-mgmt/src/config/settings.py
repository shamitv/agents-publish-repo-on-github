import os


SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "lms_secret_key_quantum_learn_2026")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/lms")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
