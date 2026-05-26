import { AnalyticsEventConsumer } from "./AnalyticsEventConsumer";

export class AnalyticsEventProducer {
  constructor(private readonly consumer: AnalyticsEventConsumer) {}

  publish(topic: string, payload: Record<string, unknown>) {
    this.consumer.consume({ topic, payload });
  }
}
