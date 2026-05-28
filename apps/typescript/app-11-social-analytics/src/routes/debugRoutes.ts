import { Router } from "express";
import { DebugController } from "../controllers/DebugController";

export function createDebugRoutes(controller: DebugController) {
  const router = Router();
  router.get("/config", controller.getConfig);
  router.get("/headers", controller.getHeaders);
  return router;
}
