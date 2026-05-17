package com.airline.dto;

import com.airline.model.Flight;
import lombok.Builder;
import lombok.Data;
import java.math.BigDecimal;
import java.time.format.DateTimeFormatter;

@Data
@Builder
public class FlightSearchResult {
    private Long id;
    private String flightNumber;
    private String airline;
    private String origin;
    private String destination;
    private String departureTime;
    private String arrivalTime;
    private BigDecimal price;
    private Integer availableSeats;

    public static FlightSearchResult fromEntity(Flight f) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
        return FlightSearchResult.builder()
                .id(f.getId())
                .flightNumber(f.getFlightNumber())
                .airline(f.getAirline())
                .origin(f.getOrigin())
                .destination(f.getDestination())
                .departureTime(f.getDepartureTime().format(formatter))
                .arrivalTime(f.getArrivalTime().format(formatter))
                .price(f.getPrice())
                .availableSeats(f.getAvailableSeats())
                .build();
    }
}
