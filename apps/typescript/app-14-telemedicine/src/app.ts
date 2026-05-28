import cookieParser from "cookie-parser";
import cors from "cors";
import express from "express";
import { Pool } from "pg";
import { AppointmentCache } from "./cache/AppointmentCache";
import { appConfig } from "./config/appConfig";
import { getPool } from "./config/db";
import { AuthController } from "./controllers/AuthController";
import { AppointmentController } from "./controllers/AppointmentController";
import { HealthController } from "./controllers/HealthController";
import { AuditEventConsumer } from "./mq/AuditEventConsumer";
import { AuditEventProducer } from "./mq/AuditEventProducer";
import { AppointmentRepository } from "./repositories/AppointmentRepository";
import { UserRepository } from "./repositories/UserRepository";
import { PatientSearchClient } from "./search/PatientSearchClient";
import { AppointmentService } from "./services/AppointmentService";
import { AuthService } from "./services/AuthService";
import { TokenService } from "./services/TokenService";
import { createAppointmentRoutes } from "./routes/appointmentRoutes";
import { createAuthRoutes } from "./routes/authRoutes";
import { createHealthRoutes } from "./routes/healthRoutes";

export function createApp() {
  const app = express();
  app.use(cors({ origin: true, credentials: true }));
  app.use(express.json());
  app.use(cookieParser());

  const pool: Pool = getPool();
  const users = new UserRepository(pool);
  const appointments = new AppointmentRepository(pool);
  const cache = new AppointmentCache();
  const auditConsumer = new AuditEventConsumer();
  const auditProducer = new AuditEventProducer(auditConsumer);
  const patientSearchClient = new PatientSearchClient(appConfig);
  const tokenService = new TokenService(appConfig);
  const authService = new AuthService(users, tokenService, auditProducer);
  const appointmentService = new AppointmentService(
    appointments,
    cache,
    patientSearchClient,
    auditProducer
  );

  app.use("/api/auth", createAuthRoutes(new AuthController(authService)));
  app.use(
    "/api/appointments",
    createAppointmentRoutes(new AppointmentController(appointmentService, authService))
  );
  app.use("/api/health", createHealthRoutes(new HealthController()));

  return app;
}
