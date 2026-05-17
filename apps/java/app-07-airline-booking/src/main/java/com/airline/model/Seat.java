package com.airline.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "seats")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Seat {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "flight_id", nullable = false)
    private Flight flight;

    @Column(nullable = false, length = 10)
    private String seatNumber;

    @Column(nullable = false)
    private String seatClass; // ECONOMY, BUSINESS, FIRST

    @Builder.Default
    private Boolean isAvailable = true;
}
