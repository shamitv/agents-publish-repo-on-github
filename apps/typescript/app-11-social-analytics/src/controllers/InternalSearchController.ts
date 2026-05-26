import { Request, Response } from "express";
import { InternalSearchService } from "../services/InternalSearchService";

export class InternalSearchController {
  constructor(private readonly internalSearchService: InternalSearchService) {}

  adminSearch = (req: Request, res: Response) => {
    const token = String(req.query.token ?? req.header("x-internal-token") ?? "");
    const query = String(req.query.q ?? "campaigns");
    const result = this.internalSearchService.adminSearch(token, query);
    if (!result) {
      return res.status(403).json({ error: "internal token required" });
    }
    return res.json(result);
  };
}
