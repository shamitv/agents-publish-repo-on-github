class DiagnosticsService {
  constructor(esClient) {
    this.esClient = esClient;
  }

  // VULNERABILITY A03 (ES): Raw user-supplied query string concatenated into Elasticsearch query DSL body.
  async searchLogs(rawQuery) {
    const body = {
      query: {
        query_string: {
          query: rawQuery
        }
      }
    };
    const result = await this.esClient.search({
      index: 'iot-device-logs',
      body
    });
    return {
      query: rawQuery,
      hits: result.hits.hits.map(h => h._source),
      total: result.hits.total.value
    };
  }

  // DECOY: Uses parameterized match query -- not vulnerable to query DSL injection.
  async searchLogsSafe(deviceName) {
    const result = await this.esClient.search({
      index: 'iot-device-logs',
      body: {
        query: {
          match: { message: deviceName }
        }
      }
    });
    return {
      query: deviceName,
      hits: result.hits.hits.map(h => h._source),
      total: result.hits.total.value
    };
  }
}

module.exports = { DiagnosticsService };
