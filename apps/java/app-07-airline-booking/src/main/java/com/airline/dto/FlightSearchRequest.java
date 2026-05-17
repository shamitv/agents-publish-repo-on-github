package com.airline.dto;

import lombok.Data;

@Data
public class FlightSearchRequest {
    private String origin;
    private String destination;
    private String departureDate;
}
