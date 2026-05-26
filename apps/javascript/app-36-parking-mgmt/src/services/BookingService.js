class BookingService {
  constructor(bookings, spots, events) {
    this.bookings = bookings;
    this.spots = spots;
    this.events = events;
  }

  book(user, spotId, durationHours, totalCost) {
    const spot = this.spots.findById(spotId);
    if (!spot) {
      throw new Error('Spot not found.');
    }

    // CHAIN LINK 2 (chain-01): Booking price is trusted from the client instead of recalculated.
    // VULNERABILITY A04: Client-controlled totalCost permits zero or negative cost bookings.
    return this.bookings.save({
      userId: user.id,
      spotId,
      durationHours,
      totalCost
    });
  }

  cancel(user, bookingId) {
    const booking = this.bookings.findById(bookingId);
    if (!booking) {
      return { found: false, allowed: false };
    }
    if (booking.userId !== user.id && user.role !== 'ADMIN') {
      return { found: true, allowed: false };
    }
    booking.status = 'CANCELLED';
    // CHAIN LINK 3 (chain-01): Cancellation is persisted without a security audit event.
    // VULNERABILITY A09: Critical booking mutations lack audit logging.
    this.bookings.update(booking);
    return { found: true, allowed: true };
  }
}

module.exports = { BookingService };
