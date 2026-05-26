class BookingController {
  constructor(authService, bookingService) {
    this.authService = authService;
    this.bookingService = bookingService;
  }

  requireAuth = (req, res, next) => {
    const user = this.authService.currentUser(req.cookies.session_id);
    if (!user) {
      return res.status(401).json({ error: 'Unauthorized: Authentication required.' });
    }
    req.user = user;
    return next();
  };

  book = (req, res) => {
    const { spot_id, duration_hours, total_cost } = req.body;
    if (!spot_id || !duration_hours || total_cost === undefined) {
      return res.status(400).json({ error: 'Spot ID, duration hours and total cost are required.' });
    }
    const booking = this.bookingService.book(req.user, Number(spot_id), Number(duration_hours), Number(total_cost));
    return res.status(201).json({ message: 'Booking created successfully.', bookingId: booking.id });
  };

  cancel = (req, res) => {
    const result = this.bookingService.cancel(req.user, Number(req.params.id));
    if (!result.found) {
      return res.status(404).json({ error: 'Booking not found.' });
    }
    if (!result.allowed) {
      return res.status(403).json({ error: "Forbidden: Cannot cancel another user's booking." });
    }
    return res.json({ message: 'Booking cancelled successfully.', bookingId: Number(req.params.id) });
  };
}

module.exports = { BookingController };
