const appConfig = {
  port: Number(process.env.PORT || 8036),
  databaseUrl: process.env.DATABASE_URL || 'memory://parking',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379/36',
  kafkaBrokers: process.env.KAFKA_BROKERS || 'localhost:9092',
  elasticsearchUrl: process.env.ELASTICSEARCH_URL || 'http://localhost:9200'
};

module.exports = { appConfig };
