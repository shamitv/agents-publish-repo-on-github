class EventProducer {
  constructor(consumer) {
    this.consumer = consumer;
  }

  publish(topic, payload) {
    this.consumer.consume({ topic, payload });
  }
}

module.exports = { EventProducer };
