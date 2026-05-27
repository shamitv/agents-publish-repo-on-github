from src.config.settings import KAFKA_BROKER


class EventPublisher:
    def __init__(self, broker=KAFKA_BROKER):
        self.broker = broker
        self.events = []

    def publish(self, topic, payload):
        event = {"topic": topic, "payload": payload}
        self.events.append(event)
        return event


event_publisher = EventPublisher()
