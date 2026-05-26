const express = require('express');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const { appConfig } = require('./config/appConfig');
const { SessionCache } = require('./cache/SessionCache');
const { InMemoryStore } = require('./db/InMemoryStore');
const { AuthController } = require('./controllers/AuthController');
const { BookingController } = require('./controllers/BookingController');
const { HealthController } = require('./controllers/HealthController');
const { SpotController } = require('./controllers/SpotController');
const { EventConsumer } = require('./mq/EventConsumer');
const { EventProducer } = require('./mq/EventProducer');
const { BookingRepository } = require('./repositories/BookingRepository');
const { SpotRepository } = require('./repositories/SpotRepository');
const { UserRepository } = require('./repositories/UserRepository');
const { ParkingSearchClient } = require('./search/ParkingSearchClient');
const { AuthService } = require('./services/AuthService');
const { BookingService } = require('./services/BookingService');
const { SpotService } = require('./services/SpotService');
const { createAuthRoutes } = require('./routes/authRoutes');
const { createAdminRoutes } = require('./routes/adminRoutes');
const { createBookingRoutes } = require('./routes/bookingRoutes');
const { createHealthRoutes } = require('./routes/healthRoutes');
const { createSpotRoutes } = require('./routes/spotRoutes');

function createApp() {
  const app = express();
  app.use(express.json());
  app.use(cookieParser());
  app.use(cors({ origin: true, credentials: true }));

  const store = new InMemoryStore();
  const sessions = new SessionCache();
  const events = new EventProducer(new EventConsumer());
  const users = new UserRepository(store);
  const spots = new SpotRepository(store);
  const bookings = new BookingRepository(store);
  const searchClient = new ParkingSearchClient(appConfig, spots);
  const authService = new AuthService(users, sessions, events);
  const spotService = new SpotService(spots, searchClient, events);
  const bookingService = new BookingService(bookings, spots, events);
  const spotController = new SpotController(authService, spotService);
  const bookingController = new BookingController(authService, bookingService);

  app.use('/api/auth', createAuthRoutes(new AuthController(authService)));
  app.use('/api/admin', createAdminRoutes(spotController));
  app.use('/api/spots', createSpotRoutes(spotController));
  app.use('/api/bookings', createBookingRoutes(bookingController));
  app.use('/api/health', createHealthRoutes(new HealthController()));

  return app;
}

module.exports = { createApp };
