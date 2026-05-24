package com.energy.billing.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "invoices")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Invoice {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long customerId;
    private String billingPeriod;
    private Double totalKwh;
    private Double totalAmount;
    private String status; // DRAFT, SENT, PAID, OVERDUE
    private LocalDateTime generatedAt;
}
