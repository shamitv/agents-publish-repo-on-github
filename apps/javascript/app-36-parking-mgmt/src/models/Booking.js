class Booking {
  constructor(id, userId, spotId, durationHours, totalCost, status = 'ACTIVE') {
    this.id = id;
    this.userId = userId;
    this.spotId = spotId;
    this.durationHours = durationHours;
    this.totalCost = totalCost;
    this.status = status;
  }
}

module.exports = { Booking };
