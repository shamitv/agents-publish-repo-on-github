import { Router } from "express";
import { AuthController } from "../controllers/AuthController";

export function createAuthRoutes(controller: AuthController) {
  const router = Router();
  router.post("/register", controller.register);
  router.post("/login", controller.login);
  router.post("/logout", controller.logout);
  router.get("/me", controller.me);
  return router;
}
