package com.auction.platform.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "listings")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Listing {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long sellerId;
    private String title;
    private String description;
    private String category;
    private Double startingPrice;
    private Double reservePrice;
    private String status; // ACTIVE, ENDED, CANCELLED
    private LocalDateTime endTime;
}
