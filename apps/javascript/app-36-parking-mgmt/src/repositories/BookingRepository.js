class BookingRepository {
  constructor(store) {
    this.store = store;
  }

  save(input) {
    const booking = {
      id: this.store.nextBookingId(),
      status: 'ACTIVE',
      ...input
    };
    this.store.bookings.push(booking);
    return booking;
  }

  findById(id) {
    return this.store.bookings.find((booking) => booking.id === id);
  }

  update(booking) {
    const index = this.store.bookings.findIndex((candidate) => candidate.id === booking.id);
    if (index >= 0) {
      this.store.bookings[index] = booking;
    }
    return booking;
  }
}

module.exports = { BookingRepository };
