package com.energy.billing.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDate;

@Entity
@Table(name = "meters")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Meter {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long customerId;
    private String meterSerial;
    private String meterType; // ELECTRIC, GAS, WATER
    private LocalDate installedAt;
    private LocalDate lastReadingDate;
}
