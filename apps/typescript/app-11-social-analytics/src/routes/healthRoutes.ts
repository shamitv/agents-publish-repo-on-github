import { Router } from "express";
import { HealthController } from "../controllers/HealthController";

export function createHealthRoutes(controller: HealthController) {
  const router = Router();
  router.get("/", controller.health);
  return router;
}
