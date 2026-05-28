const appConfig = {
  port: Number(process.env.PORT || 8017),
  telemetryUrl: process.env.TELEMETRY_URL || 'http://localhost:8017/api/internal/telemetry',
  telemetryToken: process.env.TELEMETRY_TOKEN || 'INTERNAL-SECRET-TELEMETRY-TOKEN-2026',
  databaseUrl: process.env.DATABASE_URL || 'memory://iot-dashboard',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379/17',
  kafkaBrokers: process.env.KAFKA_BROKERS || 'localhost:9092',
  deviceSearchUrl: process.env.DEVICE_SEARCH_URL || 'http://localhost:9200/iot-devices'
};

module.exports = { appConfig };
