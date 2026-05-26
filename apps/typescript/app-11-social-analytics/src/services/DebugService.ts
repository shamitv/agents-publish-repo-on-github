import { AppConfig } from "../config/appConfig";

export class DebugService {
  constructor(private readonly config: AppConfig) {}

  exposedConfig() {
    return {
      nodeEnv: process.env.NODE_ENV ?? "development",
      databaseUrl: this.config.databaseUrl,
      redisUrl: this.config.redisUrl,
      kafkaBrokers: this.config.kafkaBrokers,
      elasticsearchUrl: this.config.elasticsearchUrl,
      internalSearchUrl: this.config.internalSearchUrl,
      internalSearchToken: this.config.internalSearchToken,
      reportingApiKey: this.config.reportingApiKey
    };
  }
}
