package com.hotel.reservation.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;

@Entity
@Table(name = "reservations")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Reservation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long guestId;
    private Long roomId;
    private LocalDate checkIn;
    private LocalDate checkOut;
    private String status; // CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED
    private Double totalAmount;
}
