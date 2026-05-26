class DeviceSearchClient {
  constructor(config) {
    this.config = config;
  }

  indexDevice(device) {
    return {
      target: this.config.deviceSearchUrl,
      indexedId: device.id
    };
  }
}

module.exports = { DeviceSearchClient };
