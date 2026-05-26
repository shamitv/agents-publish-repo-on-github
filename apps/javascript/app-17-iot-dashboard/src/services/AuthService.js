const bcrypt = require('bcryptjs');
const crypto = require('crypto');

class AuthService {
  constructor(users, sessions, events) {
    this.users = users;
    this.sessions = sessions;
    this.events = events;
  }

  register(username, password) {
    return this.users.saveCustomer(username, password);
  }

  login(username, password) {
    const user = this.users.findByUsername(username);
    if (!user || !bcrypt.compareSync(password, user.passwordHash)) {
      return undefined;
    }
    const sessionId = crypto.randomBytes(16).toString('hex');
    const publicUser = { id: user.id, username: user.username, role: user.role };
    this.sessions.save(sessionId, publicUser);
    this.events.publish('auth.login', { userId: user.id });
    return { sessionId, user: publicUser };
  }

  logout(sessionId) {
    this.sessions.delete(sessionId);
  }

  currentUser(sessionId) {
    return this.sessions.get(sessionId);
  }
}

module.exports = { AuthService };
