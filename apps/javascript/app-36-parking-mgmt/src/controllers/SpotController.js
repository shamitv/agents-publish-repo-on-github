class SpotController {
  constructor(authService, spotService) {
    this.authService = authService;
    this.spotService = spotService;
  }

  requireAuth = (req, res, next) => {
    const user = this.authService.currentUser(req.cookies.session_id);
    if (!user) {
      return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
    }
    req.user = user;
    return next();
  };

  create = (req, res) => {
    if (req.user.role !== 'ADMIN') {
      return res.status(403).json({ error: 'Forbidden: Admin access only.' });
    }
    const spot = this.spotService.createSpot(req.body);
    return res.status(201).json({ message: 'Spot registered.', spotId: spot.id });
  };

  search = (req, res) => {
    return res.json(this.spotService.search(String(req.query.q || '')));
  };

  detail = (req, res) => {
    const spot = this.spotService.findById(Number(req.params.id));
    if (!spot) {
      return res.status(404).json({ error: 'Spot not found.' });
    }
    return res.json(spot);
  };
}

module.exports = { SpotController };
