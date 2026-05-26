const axios = require('axios');

class RefreshService {
  async refreshStatus(statusUrl) {
    // CHAIN LINK 2 (chain-01): Device refresh fetches caller-controlled URLs server-side.
    // VULNERABILITY A10: HTTP SSRF reaches internal device/debug endpoints.
    const response = await axios.get(statusUrl);
    return response.data;
  }
}

module.exports = { RefreshService };
