import { AnalyticsEventProducer } from "../mq/AnalyticsEventProducer";
import { WidgetRepository } from "../repositories/WidgetRepository";

interface CreateWidgetInput {
  title: string;
  type: string;
  value: string;
}

export class WidgetService {
  constructor(
    private readonly widgets: WidgetRepository,
    private readonly events: AnalyticsEventProducer
  ) {}

  listWidgets(userId: number) {
    return this.widgets.findByUserId(userId);
  }

  createWidget(userId: number, input: CreateWidgetInput) {
    const widget = this.widgets.save({ userId, ...input });
    this.events.publish("widget.created", { widgetId: widget.id, userId });
    return widget;
  }
}
