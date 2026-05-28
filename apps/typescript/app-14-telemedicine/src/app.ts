import cookieParser from "cookie-parser";
import cors from "cors";
import express from "express";
import { Pool } from "pg";
import Redis from "ioredis";
import { Kafka } from "kafkajs";
import { AppointmentCache } from "./cache/AppointmentCache";
import { appConfig } from "./config/appConfig";
import { getPool } from "./config/db";
import { getRedis } from "./config/redis";
import { getKafka, getProducer, ensureTopics } from "./config/kafka";
import { AuthController } from "./controllers/AuthController";
import { AppointmentController } from "./controllers/AppointmentController";
import { HealthController } from "./controllers/HealthController";
import { AuditEventProducer } from "./mq/AuditEventProducer";
import { AppointmentRepository } from "./repositories/AppointmentRepository";
import { UserRepository } from "./repositories/UserRepository";
import { PatientSearchClient } from "./search/PatientSearchClient";
import { AppointmentService } from "./services/AppointmentService";
import { AuthService } from "./services/AuthService";
import { ScheduleValidator } from "./services/ScheduleValidator";
import { TokenService } from "./services/TokenService";
import { PrescriptionConsumer } from "./consumers/PrescriptionConsumer";
import { NotificationConsumer } from "./consumers/NotificationConsumer";
import { createAppointmentRoutes } from "./routes/appointmentRoutes";
import { createAuthRoutes } from "./routes/authRoutes";
import { createHealthRoutes } from "./routes/healthRoutes";

export interface AppContext {
  pool: Pool;
  redis: Redis;
  kafka: Kafka;
  prescriptionConsumer: PrescriptionConsumer;
  notificationConsumer: NotificationConsumer;
}

export async function createApp(): Promise<{ app: express.Express; ctx: AppContext }> {
  const app = express();
  app.use(cors({ origin: true, credentials: true }));
  app.use(express.json());
  app.use(cookieParser());

  const pool: Pool = getPool();
  const redis: Redis = getRedis();
  const kafka: Kafka = getKafka();

  await ensureTopics();
  const producer = await getProducer();

  const prescriptionConsumer = new PrescriptionConsumer(pool, kafka);
  const notificationConsumer = new NotificationConsumer(kafka);

  const users = new UserRepository(pool);
  const appointments = new AppointmentRepository(pool);
  const cache = new AppointmentCache(redis);
  const auditProducer = new AuditEventProducer(producer);
  const patientSearchClient = new PatientSearchClient(appConfig);
  const tokenService = new TokenService(appConfig);
  const scheduleValidator = new ScheduleValidator(pool);
  const authService = new AuthService(users, tokenService, auditProducer, redis);
  const appointmentService = new AppointmentService(
    appointments,
    cache,
    patientSearchClient,
    auditProducer
  );
  const appointmentController = new AppointmentController(
    appointmentService,
    authService,
    scheduleValidator
  );

  app.use("/api/auth", createAuthRoutes(new AuthController(authService)));
  app.use("/api/appointments", createAppointmentRoutes(appointmentController));
  app.use("/api/health", createHealthRoutes(new HealthController()));

  return { app, ctx: { pool, redis, kafka, prescriptionConsumer, notificationConsumer } };
}
