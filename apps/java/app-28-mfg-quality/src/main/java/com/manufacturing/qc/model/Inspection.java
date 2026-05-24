package com.manufacturing.qc.model;

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
    private Long productId;
    private Long inspectorId;
    private String result; // PASS, FAIL, CONDITIONAL
    private String notes;
    private LocalDateTime inspectedAt;
}
