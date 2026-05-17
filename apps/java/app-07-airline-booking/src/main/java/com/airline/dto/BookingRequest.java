package com.airline.dto;

import lombok.Data;

@Data
public class BookingRequest {
    private Long flightId;
    private Long seatId;
}
