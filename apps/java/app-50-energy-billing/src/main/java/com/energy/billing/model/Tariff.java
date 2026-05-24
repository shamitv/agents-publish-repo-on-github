package com.energy.billing.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;

@Entity
@Table(name = "tariffs")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Tariff {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String serviceType; // RESIDENTIAL, COMMERCIAL, INDUSTRIAL
    private Integer tier;
    private Double ratePerKwh;
    private LocalDate effectiveFrom;
    private LocalDate effectiveTo;
}
