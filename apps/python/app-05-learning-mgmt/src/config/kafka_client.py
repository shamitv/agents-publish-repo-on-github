from kafka import KafkaProducer, KafkaConsumer

from src.config.settings import KAFKA_BROKER


class EventPublisher:
    def __init__(self, broker=KAFKA_BROKER):
        self.broker = broker
        self.events = []
        self._producer = None

    def _get_producer(self):
        if self._producer is None:
            try:
                self._producer = KafkaProducer(
                    bootstrap_servers=self.broker,
                    max_block_ms=5000,
                    request_timeout_ms=5000,
                )
            except Exception:
                self._producer = None
        return self._producer

    def publish(self, topic, payload):
        event = {"topic": topic, "payload": payload}
        self.events.append(event)
        producer = self._get_producer()
        if producer:
            try:
                import json
                future = producer.send(topic, value=json.dumps(payload).encode("utf-8"))
                future.get(timeout=5)
            except Exception:
                pass
        return event


def create_consumer(topic, group_id="lms-group"):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=KAFKA_BROKER,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=1000,
        )
        return consumer
    except Exception:
        return None


event_publisher = EventPublisher()
