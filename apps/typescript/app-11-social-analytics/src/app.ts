import path from "path";
import cookieParser from "cookie-parser";
import cors from "cors";
import express, { Request, Response, NextFunction } from "express";
import { appConfig } from "./config/appConfig";
import { SessionCache } from "./cache/SessionCache";
import { UserRepository } from "./repositories/UserRepository";
import { WidgetRepository } from "./repositories/WidgetRepository";
import { DashboardRepository } from "./repositories/DashboardRepository";
import { AnalyticsRepository } from "./repositories/AnalyticsRepository";
import { AnalyticsEventConsumer } from "./mq/AnalyticsEventConsumer";
import { AnalyticsEventProducer } from "./mq/AnalyticsEventProducer";
import { InternalSearchClient } from "./search/InternalSearchClient";
import { AuthService } from "./services/AuthService";
import { ConfigService } from "./services/ConfigService";
import { DebugService } from "./services/DebugService";
import { InternalSearchService } from "./services/InternalSearchService";
import { PreviewService } from "./services/PreviewService";
import { WidgetService } from "./services/WidgetService";
import { AuthController } from "./controllers/AuthController";
import { ConfigController } from "./controllers/ConfigController";
import { DashboardController } from "./controllers/DashboardController";
import { DebugController } from "./controllers/DebugController";
import { HealthController } from "./controllers/HealthController";
import { InternalSearchController } from "./controllers/InternalSearchController";
import { PreviewController } from "./controllers/PreviewController";
import { WidgetController } from "./controllers/WidgetController";
import { createAuthRoutes } from "./routes/authRoutes";
import { createConfigRoutes } from "./routes/configRoutes";
import { createDashboardRoutes } from "./routes/dashboardRoutes";
import { createDebugRoutes } from "./routes/debugRoutes";
import { createHealthRoutes } from "./routes/healthRoutes";
import { createInternalRoutes } from "./routes/internalRoutes";
import { createPreviewRoutes } from "./routes/previewRoutes";
import { createWidgetRoutes } from "./routes/widgetRoutes";

function asyncHandler(fn: (req: Request, res: Response, next: NextFunction) => Promise<void>) {
  return (req: Request, res: Response, next: NextFunction) => fn(req, res, next).catch(next);
}

export function createApp() {
  const app = express();
  app.use(cors({ origin: true, credentials: true }));
  app.use(express.json());
  app.use(cookieParser());
  app.use(express.static(path.join(__dirname, "..", "public")));

  const sessionCache = new SessionCache();
  const userRepository = new UserRepository();
  const widgetRepository = new WidgetRepository();
  const dashboardRepository = new DashboardRepository();
  const analyticsRepository = new AnalyticsRepository();
  const eventConsumer = new AnalyticsEventConsumer();
  const eventProducer = new AnalyticsEventProducer(eventConsumer);
  const internalSearchClient = new InternalSearchClient(appConfig);

  const authService = new AuthService(userRepository, sessionCache, eventProducer);
  const configService = new ConfigService();
  const widgetService = new WidgetService(widgetRepository, eventProducer);
  const previewService = new PreviewService();
  const debugService = new DebugService(appConfig);
  const internalSearchService = new InternalSearchService(internalSearchClient);

  app.use("/api/auth", createAuthRoutes(new AuthController(authService)));
  app.use("/api/config", createConfigRoutes(new ConfigController(configService)));
  app.use("/api/dashboards", createDashboardRoutes(new DashboardController(dashboardRepository, authService)));
  app.use("/api/widgets", createWidgetRoutes(new WidgetController(widgetService, authService)));
  app.use("/api/preview", createPreviewRoutes(new PreviewController(previewService)));
  app.use("/api/debug", createDebugRoutes(new DebugController(debugService)));
  app.use("/api/health", createHealthRoutes(new HealthController()));
  app.use("/internal/search", createInternalRoutes(new InternalSearchController(internalSearchService)));

  app.get("/", (_req, res) => {
    res.sendFile(path.join(__dirname, "..", "public", "index.html"));
  });

  return app;
}
