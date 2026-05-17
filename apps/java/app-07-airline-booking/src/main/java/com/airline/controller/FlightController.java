package com.airline.controller;

import com.airline.dto.FlightSearchResult;
import com.airline.model.Flight;
import com.airline.model.Seat;
import com.airline.service.FlightService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/flights")
public class FlightController {

    @Autowired
    private FlightService flightService;

    @GetMapping("/search")
    public ResponseEntity<List<FlightSearchResult>> search(
            @RequestParam String origin,
            @RequestParam String destination,
            @RequestParam String date) {
        
        List<Flight> flights = flightService.searchFlights(origin, destination, date);
        List<FlightSearchResult> results = flights.stream()
                .map(FlightSearchResult::fromEntity)
                .collect(Collectors.toList());
        return ResponseEntity.ok(results);
    }

    @GetMapping("/{id}/seats")
    public ResponseEntity<List<Seat>> getSeats(@PathVariable Long id) {
        return ResponseEntity.ok(flightService.getFlightSeats(id));
    }

    @GetMapping
    @PreAuthorize("hasRole('AIRLINE_STAFF')")
    public ResponseEntity<List<Flight>> listAll() {
        return ResponseEntity.ok(flightService.getAllFlights());
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasRole('AIRLINE_STAFF')")
    public ResponseEntity<Flight> updateFlight(@PathVariable Long id, @RequestBody Map<String, Object> payload) {
        return flightService.getFlightById(id).map(flight -> {
            flight.setFlightNumber((String) payload.get("flightNumber"));
            flight.setAirline((String) payload.get("airline"));
            flight.setPrice(new BigDecimal(payload.get("price").toString()));
            Flight saved = flightService.saveFlight(flight);
            return ResponseEntity.ok(saved);
        }).orElse(ResponseEntity.notFound().build());
    }
}
