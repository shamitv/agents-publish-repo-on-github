package com.pharma.tracking.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.io.Serializable;
import java.time.LocalDate;

@Entity
@Table(name = "batches")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Batch implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long drugId;
    private String lotNumber;
    private LocalDate manufactureDate;
    private LocalDate expiryDate;
    private Integer quantity;
    private String status; // IN_TRANSIT, DELIVERED, RECALLED
}
