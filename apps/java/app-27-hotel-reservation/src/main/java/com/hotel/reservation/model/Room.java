package com.hotel.reservation.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "rooms")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Room {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String roomNumber;
    private Integer floor;
    private String type; // SINGLE, DOUBLE, SUITE, PENTHOUSE
    private String status; // AVAILABLE, OCCUPIED, MAINTENANCE
    private String amenities;
}
