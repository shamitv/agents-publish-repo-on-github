class InternalTelemetryController {
  constructor(telemetryService) {
    this.telemetryService = telemetryService;
  }

  telemetry = (req, res) => {
    const token = req.headers['x-telemetry-token'] || req.query.token;
    const payload = this.telemetryService.internalTelemetry(token);
    if (!payload) {
      return res.status(403).json({ error: 'Access Denied: Invalid Telemetry secret key.' });
    }
    return res.json(payload);
  };
}

module.exports = { InternalTelemetryController };
