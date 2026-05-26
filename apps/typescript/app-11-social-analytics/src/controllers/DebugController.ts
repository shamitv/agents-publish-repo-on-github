import { Request, Response } from "express";
import { DebugService } from "../services/DebugService";

export class DebugController {
  constructor(private readonly debugService: DebugService) {}

  getConfig = (_req: Request, res: Response) => {
    return res.json(this.debugService.exposedConfig());
  };

  getHeaders = (req: Request, res: Response) => {
    return res.json({ headers: req.headers });
  };
}
