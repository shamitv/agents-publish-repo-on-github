class EventConsumer {
  constructor() {
    this.events = [];
  }

  consume(event) {
    this.events.push(event);
  }
}

module.exports = { EventConsumer };
