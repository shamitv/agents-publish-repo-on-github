const express = require('express');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const { appConfig } = require('./config/appConfig');
const { InMemoryStore } = require('./db/InMemoryStore');
const { SessionCache } = require('./cache/SessionCache');
const { UserRepository } = require('./repositories/UserRepository');
const { DeviceRepository } = require('./repositories/DeviceRepository');
const { PgDeviceRepository } = require('./repositories/PgDeviceRepository');
const { TelemetryRepository } = require('./repositories/TelemetryRepository');
const { EventConsumer } = require('./mq/EventConsumer');
const { EventProducer } = require('./mq/EventProducer');
const { DeviceSearchClient } = require('./search/DeviceSearchClient');
const { AuthService } = require('./services/AuthService');
const { DeviceService } = require('./services/DeviceService');
const { RefreshService } = require('./services/RefreshService');
const { TelemetryService } = require('./services/TelemetryService');
const { TelemetryQueryService } = require('./services/TelemetryQueryService');
const { AuthController } = require('./controllers/AuthController');
const { DeviceController } = require('./controllers/DeviceController');
const { HealthController } = require('./controllers/HealthController');
const { InternalTelemetryController } = require('./controllers/InternalTelemetryController');
const { createAuthRoutes } = require('./routes/authRoutes');
const { createDeviceRoutes } = require('./routes/deviceRoutes');
const { createHealthRoutes } = require('./routes/healthRoutes');
const { createInternalRoutes } = require('./routes/internalRoutes');

function createApp() {
  const app = express();
  app.use(express.json());
  app.use(cookieParser());
  app.use(cors({ origin: true, credentials: true }));

  const store = new InMemoryStore();
  const sessions = new SessionCache();
  const users = new UserRepository(store);
  const devices = new DeviceRepository(store);
  const events = new EventProducer(new EventConsumer());
  const search = new DeviceSearchClient(appConfig);
  const authService = new AuthService(users, sessions, events);
  const deviceService = new DeviceService(devices, search, events);
  const refreshService = new RefreshService();
  const telemetryService = new TelemetryService(devices, appConfig);

  const pgDevices = new PgDeviceRepository();
  const telemetryRepo = new TelemetryRepository();
  const telemetryQueryService = new TelemetryQueryService(telemetryRepo);

  const authController = new AuthController(authService);
  const deviceController = new DeviceController(authService, deviceService, refreshService, telemetryQueryService);
  const telemetryController = new InternalTelemetryController(telemetryService);

  app.use('/api/auth', createAuthRoutes(authController));
  app.use('/api/devices', createDeviceRoutes(deviceController));
  app.use('/api/internal', createInternalRoutes(telemetryController));
  app.use('/api/health', createHealthRoutes(new HealthController()));

  return app;
}

module.exports = { createApp };
