class SpotRepository {
  constructor(store) {
    this.store = store;
  }

  save(input) {
    const spot = {
      id: this.store.nextSpotId(),
      spotNumber: input.spot_number,
      type: input.type,
      priceRate: Number(input.price_rate)
    };
    this.store.spots.push(spot);
    return spot;
  }

  findById(id) {
    return this.store.spots.find((spot) => spot.id === id);
  }

  findAll() {
    return [...this.store.spots];
  }
}

module.exports = { SpotRepository };
