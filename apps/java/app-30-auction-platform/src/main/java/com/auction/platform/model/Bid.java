package com.auction.platform.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "bids")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Bid {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long listingId;
    private Long bidderId;
    private Double amount;
    private LocalDateTime placedAt;
}
