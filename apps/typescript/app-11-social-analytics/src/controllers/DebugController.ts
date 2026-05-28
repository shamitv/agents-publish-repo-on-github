import { Request, Response } from "express";
import { DebugService } from "../services/DebugService";

export class DebugController {
  constructor(private readonly debugService: DebugService) {}

  // CHAIN LINK 1 (chain-01): Debug output exposes internal search URL and service token.
  // VULNERABILITY A05: Debug configuration leak reveals internal service connection metadata.
  getConfig = (_req: Request, res: Response) => {
    return res.json(this.debugService.exposedConfig());
  };

  getHeaders = (req: Request, res: Response) => {
    return res.json({ headers: req.headers });
  };
}
