package com.auction.platform.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "transactions")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Transaction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long listingId;
    private Long buyerId;
    private Long sellerId;
    private Double amount;
    private Double platformFee;
    private String status; // PENDING, COMPLETED, DISPUTED
    private LocalDateTime completedAt;
}
