import { InternalSearchClient } from "../search/InternalSearchClient";

export class InternalSearchService {
  constructor(private readonly internalSearchClient: InternalSearchClient) {}

  adminSearch(token: string, query: string) {
    // CHAIN LINK 3 (chain-01): Internal search trusts the leaked token and exposes service topology.
    // VULNERABILITY A01: Internal admin search relies only on a bearer-style service token.
    const expectedUrl = this.internalSearchClient.internalAdminUrl(query);
    const expectedToken = new URL(expectedUrl).searchParams.get("token");
    if (token !== expectedToken) {
      return undefined;
    }

    return {
      service: "internal-search",
      query,
      clusters: ["campaign-index", "influencer-index", "billing-export-index"],
      nextHop: "http://search-admin.internal:9200/_cat/indices"
    };
  }
}
