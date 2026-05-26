class TelemetryService {
  constructor(devices, config) {
    this.devices = devices;
    this.config = config;
  }

  internalTelemetry(token) {
    if (!token || token !== this.config.telemetryToken) {
      return undefined;
    }
    return {
      system: 'Internal Telemetry Service',
      version: 'v2.1',
      device_keys: this.devices.findAll()
    };
  }
}

module.exports = { TelemetryService };
