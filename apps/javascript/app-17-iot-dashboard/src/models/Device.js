class Device {
  constructor(id, name, status, deviceSecret) {
    this.id = id;
    this.name = name;
    this.status = status;
    this.deviceSecret = deviceSecret;
  }
}

module.exports = { Device };
