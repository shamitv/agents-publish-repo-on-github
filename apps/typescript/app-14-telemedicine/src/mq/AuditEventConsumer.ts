export interface AuditEvent {
  topic: string;
  payload: Record<string, unknown>;
}

export class AuditEventConsumer {
  private readonly events: AuditEvent[] = [];

  consume(event: AuditEvent) {
    this.events.push(event);
  }

  recentEvents() {
    return [...this.events].slice(-10);
  }
}
