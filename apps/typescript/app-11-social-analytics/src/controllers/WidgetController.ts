import { Request, Response } from "express";
import { AuthService } from "../services/AuthService";
import { WidgetService } from "../services/WidgetService";

export class WidgetController {
  constructor(
    private readonly widgetService: WidgetService,
    private readonly authService: AuthService
  ) {}

  list = (req: Request, res: Response) => {
    const user = this.authService.currentUser(req.cookies?.sessionId);
    return res.json(this.widgetService.listWidgets(user?.id ?? 1));
  };

  create = (req: Request, res: Response) => {
    const user = this.authService.currentUser(req.cookies?.sessionId);
    const widget = this.widgetService.createWidget(user?.id ?? 1, {
      title: String(req.body?.title ?? "Untitled"),
      type: String(req.body?.type ?? "metric"),
      value: String(req.body?.value ?? "0")
    });
    return res.status(201).json(widget);
  };
}
