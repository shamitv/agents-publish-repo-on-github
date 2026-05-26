class DeviceController {
  constructor(authService, deviceService, refreshService) {
    this.authService = authService;
    this.deviceService = deviceService;
    this.refreshService = refreshService;
  }

  requireAuth = (req, res, next) => {
    const user = this.authService.currentUser(req.cookies.session_id);
    if (!user) {
      return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
    }
    req.user = user;
    return next();
  };

  runCommand = (req, res) => {
    const { deviceId, command } = req.body;
    if (!deviceId || !command) {
      return res.status(400).json({ error: 'Device ID and command are required.' });
    }
    if (typeof command !== 'string' || command.length > 200) {
      return res.status(400).json({ error: 'Invalid command payload format.' });
    }

    try {
      const result = this.deviceService.runCommand(Number(deviceId), command);
      return res.json(result);
    } catch (err) {
      return res.status(err.statusCode || 500).json(this.deviceService.commandError(err));
    }
  };

  refresh = async (req, res) => {
    const { statusUrl } = req.body;
    if (!statusUrl) {
      return res.status(400).json({ error: 'Status URL is required.' });
    }
    try {
      const data = await this.refreshService.refreshStatus(statusUrl);
      return res.json({ message: 'Device status updated.', data });
    } catch (err) {
      return res.status(500).json({ error: 'Failed to retrieve device status.', details: err.message });
    }
  };

  detail = (req, res) => {
    const device = this.deviceService.getPublicDevice(Number(req.params.id));
    if (!device) {
      return res.status(404).json({ error: 'Device not found.' });
    }
    return res.json(device);
  };
}

module.exports = { DeviceController };
