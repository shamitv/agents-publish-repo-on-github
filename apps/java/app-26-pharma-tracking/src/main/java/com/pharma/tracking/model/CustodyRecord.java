package com.pharma.tracking.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "custody_records")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CustodyRecord {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long batchId;
    private String fromEntity;
    private String toEntity;
    private LocalDateTime transferredAt;
    private String signatureHash;
}
