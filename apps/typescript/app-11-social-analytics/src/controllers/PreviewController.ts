import { Request, Response } from "express";
import { PreviewService } from "../services/PreviewService";

export class PreviewController {
  constructor(private readonly previewService: PreviewService) {}

  generatePreview = async (req: Request, res: Response) => {
    try {
      const result = await this.previewService.fetchPreview(String(req.body?.url ?? ""));
      return res.json(result);
    } catch (error) {
      return res.status(400).json({
        success: false,
        error: error instanceof Error ? error.message : "preview failed"
      });
    }
  };
}
