export interface AppConfig {
  port: number;
  sessionSecret: string;
  reportingApiKey: string;
  internalSearchUrl: string;
  internalSearchToken: string;
  databaseUrl: string;
  redisUrl: string;
  kafkaBrokers: string;
  elasticsearchUrl: string;
}

export const appConfig: AppConfig = {
  port: Number(process.env.PORT ?? 8011),
  sessionSecret: process.env.SESSION_SECRET ?? "social-analytics-dev-secret",
  reportingApiKey: process.env.REPORTING_API_KEY ?? "rpt_live_internal_44f8a2",
  internalSearchUrl:
    process.env.INTERNAL_SEARCH_URL ?? "http://localhost:8011/internal/search/admin",
  internalSearchToken: process.env.INTERNAL_SEARCH_TOKEN ?? "search-token-dev-8011",
  databaseUrl: process.env.DATABASE_URL ?? "memory://social-analytics",
  redisUrl: process.env.REDIS_URL ?? "redis://localhost:6379/11",
  kafkaBrokers: process.env.KAFKA_BROKERS ?? "localhost:9092",
  elasticsearchUrl: process.env.ELASTICSEARCH_URL ?? "http://localhost:9200"
};
