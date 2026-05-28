export interface AnalyticsEvent {
  topic: string;
  payload: Record<string, unknown>;
}

export class AnalyticsEventConsumer {
  private readonly events: AnalyticsEvent[] = [];

  consume(event: AnalyticsEvent) {
    this.events.push(event);
  }

  recentEvents() {
    return [...this.events].slice(-10);
  }
}
