package com.airline.service;

import com.airline.model.Flight;
import com.airline.model.Seat;
import com.airline.repository.FlightRepository;
import com.airline.repository.FlightSearchDao;
import com.airline.repository.SeatRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class FlightService {

    @Autowired
    private FlightRepository flightRepository;

    @Autowired
    private FlightSearchDao flightSearchDao;

    @Autowired
    private SeatRepository seatRepository;

    public List<Flight> searchFlights(String origin, String destination, String date) {
        return flightSearchDao.searchFlights(origin, destination, date);
    }

    public List<Flight> getAllFlights() {
        return flightRepository.findAll();
    }

    public Optional<Flight> getFlightById(Long id) {
        return flightRepository.findById(id);
    }

    public List<Seat> getFlightSeats(Long flightId) {
        return seatRepository.findByFlightId(flightId);
    }

    public Flight saveFlight(Flight flight) {
        return flightRepository.save(flight);
    }
}
