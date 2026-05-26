import { Router } from "express";
import { PreviewController } from "../controllers/PreviewController";

export function createPreviewRoutes(controller: PreviewController) {
  const router = Router();
  router.post("/", controller.generatePreview);
  return router;
}
