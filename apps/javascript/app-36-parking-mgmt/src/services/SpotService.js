class SpotService {
  constructor(spots, searchClient, events) {
    this.spots = spots;
    this.searchClient = searchClient;
    this.events = events;
  }

  createSpot(input) {
    const spot = this.spots.save(input);
    this.events.publish('security.audit.spot.created', { spotId: spot.id, spotNumber: spot.spotNumber });
    console.log(`[SECURITY AUDIT] New parking spot ${spot.spotNumber} registered at ${new Date().toISOString()}`);
    return spot;
  }

  search(rawQuery) {
    return this.searchClient.searchByQueryString(rawQuery);
  }

  findById(id) {
    return this.spots.findById(id);
  }
}

module.exports = { SpotService };
