class SessionCache {
  constructor() {
    this.sessions = new Map();
  }

  save(sessionId, user) {
    this.sessions.set(sessionId, user);
  }

  get(sessionId) {
    return sessionId ? this.sessions.get(sessionId) : undefined;
  }

  delete(sessionId) {
    if (sessionId) {
      this.sessions.delete(sessionId);
    }
  }
}

module.exports = { SessionCache };
