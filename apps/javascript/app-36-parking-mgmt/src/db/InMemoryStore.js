const bcrypt = require('bcryptjs');

class InMemoryStore {
  constructor() {
    const salt = bcrypt.genSaltSync(10);
    this.users = [
      { id: 1, username: 'alice_driver', passwordHash: bcrypt.hashSync('driver123', salt), role: 'CUSTOMER' },
      { id: 2, username: 'bob_driver', passwordHash: bcrypt.hashSync('driver456', salt), role: 'CUSTOMER' },
      { id: 3, username: 'admin_attendant', passwordHash: bcrypt.hashSync('attendant2026Secure!', salt), role: 'ADMIN' }
    ];
    this.spots = [
      { id: 1, spotNumber: 'A-101', type: 'Standard', priceRate: 5.0 },
      { id: 2, spotNumber: 'B-201', type: 'Premium', priceRate: 12.0 }
    ];
    this.bookings = [
      { id: 1, userId: 1, spotId: 1, durationHours: 2, totalCost: 10.0, status: 'ACTIVE' }
    ];
  }

  nextUserId() {
    return Math.max(...this.users.map((user) => user.id), 0) + 1;
  }

  nextSpotId() {
    return Math.max(...this.spots.map((spot) => spot.id), 0) + 1;
  }

  nextBookingId() {
    return Math.max(...this.bookings.map((booking) => booking.id), 0) + 1;
  }
}

module.exports = { InMemoryStore };
