const bcrypt = require('bcryptjs');

class UserRepository {
  constructor(store) {
    this.store = store;
  }

  findByUsername(username) {
    return this.store.users.find((user) => user.username === username);
  }

  saveCustomer(username, password) {
    if (this.findByUsername(username)) {
      throw new Error('duplicate user');
    }
    const user = {
      id: this.store.nextUserId(),
      username,
      passwordHash: bcrypt.hashSync(password, bcrypt.genSaltSync(10)),
      role: 'CUSTOMER'
    };
    this.store.users.push(user);
    return user;
  }
}

module.exports = { UserRepository };
