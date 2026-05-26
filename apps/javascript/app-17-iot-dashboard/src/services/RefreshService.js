const axios = require('axios');

class RefreshService {
  async refreshStatus(statusUrl) {
    const response = await axios.get(statusUrl);
    return response.data;
  }
}

module.exports = { RefreshService };
