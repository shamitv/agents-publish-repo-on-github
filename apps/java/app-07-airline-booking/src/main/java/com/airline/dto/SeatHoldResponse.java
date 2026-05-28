package com.airline.dto;

import com.airline.model.SeatHold;
import lombok.*;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SeatHoldResponse {
    private String holdRef;
    private String passengerEmail;
    private Long flightId;
    private String flightNumber;
    private Long seatId;
    private String seatNumber;
    private String status;
    private String paymentState;
    private LocalDateTime expiresAt;

    public static SeatHoldResponse fromEntity(SeatHold hold) {
        return SeatHoldResponse.builder()
                .holdRef(hold.getHoldRef())
                .passengerEmail(hold.getPassenger().getEmail())
                .flightId(hold.getFlight().getId())
                .flightNumber(hold.getFlight().getFlightNumber())
                .seatId(hold.getSeat().getId())
                .seatNumber(hold.getSeat().getSeatNumber())
                .status(hold.getStatus())
                .paymentState(hold.getPaymentState())
                .expiresAt(hold.getExpiresAt())
                .build();
    }
}
