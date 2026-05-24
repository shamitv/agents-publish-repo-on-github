package com.manufacturing.qc.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "defects")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Defect {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long inspectionId;
    private String defectType;
    private String severity; // MINOR, MAJOR, CRITICAL
    private String description;
    private String status; // OPEN, RESOLVED
}
