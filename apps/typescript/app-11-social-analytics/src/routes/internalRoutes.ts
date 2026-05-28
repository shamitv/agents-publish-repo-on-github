import { Router } from "express";
import { InternalSearchController } from "../controllers/InternalSearchController";

export function createInternalRoutes(controller: InternalSearchController) {
  const router = Router();
  router.get("/admin", controller.adminSearch);
  return router;
}
