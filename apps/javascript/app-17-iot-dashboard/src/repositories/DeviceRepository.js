class DeviceRepository {
  constructor(store) {
    this.store = store;
  }

  findById(id) {
    return this.store.devices.find((device) => device.id === id);
  }

  findAll() {
    return [...this.store.devices];
  }
}

module.exports = { DeviceRepository };
