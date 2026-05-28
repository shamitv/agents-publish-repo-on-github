package com.airline.dto;

import lombok.Data;

@Data
public class SeatHoldRequest {
    private Long flightId;
    private Long seatId;
}
