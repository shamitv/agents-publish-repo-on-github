import pickle
import threading

from src.config.kafka_client import create_consumer


class ImportListener:
    def load_course(self, raw_bytes):
        # VULNERABILITY A08: Untrusted pickle payload is deserialized without class restrictions.
        return pickle.loads(raw_bytes)

    def start_consumer(self):
        consumer = create_consumer("course-imports", "import-group")
        if consumer is None:
            return
        def poll():
            for msg in consumer:
                try:
                    raw_bytes = msg.value
                    self.load_course(raw_bytes)
                except Exception:
                    pass
        t = threading.Thread(target=poll, daemon=True)
        t.start()
