package com.hotel.reservation.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;

@Entity
@Table(name = "room_rates")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoomRate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String roomType;
    private String season; // SPRING, SUMMER, AUTUMN, WINTER
    private Double nightlyRate;
    private LocalDate effectiveFrom;
    private LocalDate effectiveTo;
}
