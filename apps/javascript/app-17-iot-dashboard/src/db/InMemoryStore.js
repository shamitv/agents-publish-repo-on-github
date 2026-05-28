const bcrypt = require('bcryptjs');

class InMemoryStore {
  constructor() {
    const salt = bcrypt.genSaltSync(10);
    this.users = [
      { id: 1, username: 'alice_owner', passwordHash: bcrypt.hashSync('alice123', salt), role: 'CUSTOMER' },
      { id: 2, username: 'admin_iot', passwordHash: bcrypt.hashSync('adminSecureIoT2026!', salt), role: 'ADMIN' }
    ];
    this.devices = [
      // VULNERABILITY A02: Device access tokens are stored as plaintext fields.
      { id: 1, name: 'Smart Thermostat', status: 'ONLINE', deviceSecret: 'IOT-DEV-KEY-THERMO-1122' },
      { id: 2, name: 'Security Gateway', status: 'ONLINE', deviceSecret: 'IOT-DEV-KEY-GATEWAY-8877' }
    ];
  }

  nextUserId() {
    return Math.max(...this.users.map((user) => user.id), 0) + 1;
  }
}

module.exports = { InMemoryStore };
