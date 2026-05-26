class ParkingSearchClient {
  constructor(config, spots) {
    this.config = config;
    this.spots = spots;
  }

  searchByQueryString(rawQuery) {
    // CHAIN LINK 1 (chain-01): User input is embedded directly in Elasticsearch query_string syntax.
    // VULNERABILITY A03: Elasticsearch query injection can broaden spot searches and reveal pricing.
    const elasticsearchQuery = {
      index: 'parking-spots',
      endpoint: this.config.elasticsearchUrl,
      body: {
        query: {
          query_string: {
            query: `type:${rawQuery}`
          }
        }
      }
    };

    if (rawQuery.includes('*') || rawQuery.toLowerCase().includes('or')) {
      return { elasticsearchQuery, hits: this.spots.findAll() };
    }

    return {
      elasticsearchQuery,
      hits: this.spots.findAll().filter((spot) =>
        spot.type.toLowerCase().includes(rawQuery.toLowerCase())
      )
    };
  }
}

module.exports = { ParkingSearchClient };
