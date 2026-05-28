import { InMemoryDatabase } from "../db/InMemoryDatabase";
import { Widget } from "../models/Widget";

export class WidgetRepository {
  constructor(private readonly database: InMemoryDatabase) {}

  findByUserId(userId: number) {
    return this.database.widgets.filter((widget) => widget.userId === userId);
  }

  save(widget: Omit<Widget, "id">) {
    const saved = { ...widget, id: this.database.nextWidgetId() };
    this.database.widgets.push(saved);
    return saved;
  }
}
