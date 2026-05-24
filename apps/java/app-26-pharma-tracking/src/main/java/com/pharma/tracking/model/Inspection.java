package com.pharma.tracking.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "inspections")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Inspection {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long batchId;
    private Long inspectorId;
    private String result; // PASS, FAIL
    private String notes;
    private LocalDateTime inspectedAt;
}
