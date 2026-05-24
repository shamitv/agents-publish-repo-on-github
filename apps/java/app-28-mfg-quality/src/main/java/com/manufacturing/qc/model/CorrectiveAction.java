package com.manufacturing.qc.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "corrective_actions")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CorrectiveAction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long defectId;
    private String assignedTo;
    private String description;
    private String status; // OPEN, IN_PROGRESS, RESOLVED
    private LocalDate dueDate;
    private LocalDateTime resolvedAt;
}
