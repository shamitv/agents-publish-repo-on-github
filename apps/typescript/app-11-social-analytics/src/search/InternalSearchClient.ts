import { AppConfig } from "../config/appConfig";

export class InternalSearchClient {
  constructor(private readonly config: AppConfig) {}

  internalAdminUrl(query: string) {
    const url = new URL(this.config.internalSearchUrl);
    url.searchParams.set("token", this.config.internalSearchToken);
    url.searchParams.set("q", query);
    return url.toString();
  }
}
