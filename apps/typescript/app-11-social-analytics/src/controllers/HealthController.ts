import { Request, Response } from "express";

export class HealthController {
  health = (_req: Request, res: Response) => {
    return res.json({ status: "ok" });
  };
}
