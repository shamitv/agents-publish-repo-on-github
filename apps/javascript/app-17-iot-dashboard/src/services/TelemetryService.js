class TelemetryService {
  constructor(devices, config) {
    this.devices = devices;
    this.config = config;
  }

  internalTelemetry(token) {
    if (!token || token !== this.config.telemetryToken) {
      return undefined;
    }
    // CHAIN LINK 3 (chain-01): Internal telemetry returns plaintext device tokens.
    // VULNERABILITY A02: Device secrets are stored and returned in plaintext.
    return {
      system: 'Internal Telemetry Service',
      version: 'v2.1',
      device_keys: this.devices.findAll()
    };
  }
}

module.exports = { TelemetryService };
