import { AuditEventConsumer } from "./AuditEventConsumer";

export class AuditEventProducer {
  constructor(private readonly consumer: AuditEventConsumer) {}

  publish(topic: string, payload: Record<string, unknown>) {
    this.consumer.consume({ topic, payload });
  }
}
