export class SessionCache {
  private readonly sessions = new Map<string, number>();

  save(sessionId: string, userId: number) {
    this.sessions.set(sessionId, userId);
  }

  get(sessionId: string | undefined) {
    if (!sessionId) {
      return undefined;
    }
    return this.sessions.get(sessionId);
  }

  delete(sessionId: string | undefined) {
    if (sessionId) {
      this.sessions.delete(sessionId);
    }
  }
}
