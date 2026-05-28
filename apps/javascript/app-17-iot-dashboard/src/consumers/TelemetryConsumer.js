class TelemetryConsumer {
  constructor(kafkaConsumer, telemetryRepository, esClient) {
    this.consumer = kafkaConsumer;
    this.telemetryRepository = telemetryRepository;
    this.esClient = esClient;
    this.running = false;
  }

  async start() {
    this.running = true;
    await this.consumer.subscribe({ topics: ['iot-telemetry', 'iot-commands', 'iot-configs'], fromBeginning: false });

    await this.consumer.run({
      eachMessage: async ({ topic, message }) => {
        await this.processMessage(topic, JSON.parse(message.value.toString()));
      }
    });

    console.log('TelemetryConsumer started');
  }

  async processMessage(topic, payload) {
    switch (topic) {
      case 'iot-telemetry':
        await this.telemetryRepository.insertTelemetry(
          payload.device_id,
          payload.temperature,
          payload.humidity
        );
        break;

      case 'iot-commands':
        if (this.esClient) {
          await this.esClient.index({
            index: 'iot-device-logs',
            body: {
              device_id: payload.device_id,
              event_type: 'command',
              message: `Command executed: ${payload.command}`,
              timestamp: new Date().toISOString()
            }
          });
        }
        break;

      // VULNERABILITY A08: Consumer executes device rule scripts via eval() on untrusted input.
      case 'iot-configs':
        if (payload.ruleScript) {
          eval(payload.ruleScript);
        }
        // VULNERABILITY A09: No audit trail recorded for device command/telemetry event processing.
        break;

      default:
        break;
    }
  }

  async shutdown() {
    this.running = false;
    await this.consumer.disconnect();
  }
}

module.exports = { TelemetryConsumer };
