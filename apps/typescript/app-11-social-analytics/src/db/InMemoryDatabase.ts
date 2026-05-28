import { User } from "../models/User";
import { Widget } from "../models/Widget";

export class InMemoryDatabase {
  readonly users: User[] = [
    { id: 1, username: "alice", password: "alice123", displayName: "Alice Analyst" },
    { id: 2, username: "bob", password: "bob123", displayName: "Bob Brand" }
  ];

  readonly widgets: Widget[] = [
    { id: 1, userId: 1, title: "Follower Growth", type: "metric", value: "18.4%" },
    { id: 2, userId: 1, title: "Engagement Rate", type: "metric", value: "7.9%" },
    { id: 3, userId: 2, title: "Campaign Reach", type: "metric", value: "1.2M" }
  ];

  nextWidgetId() {
    return Math.max(...this.widgets.map((widget) => widget.id), 0) + 1;
  }
}
