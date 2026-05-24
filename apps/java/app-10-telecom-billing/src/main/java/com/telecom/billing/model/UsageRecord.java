package com.telecom.billing.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "usage_records")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UsageRecord {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long customerId;
    private String usageType; // DATA, VOICE, SMS
    private Double quantity;
    private LocalDateTime recordedAt;
}
