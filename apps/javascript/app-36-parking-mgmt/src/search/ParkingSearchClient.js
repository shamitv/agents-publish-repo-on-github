class ParkingSearchClient {
  constructor(config, spots) {
    this.config = config;
    this.spots = spots;
  }

  searchByQueryString(rawQuery) {
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
