package com.energy.billing.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "customers")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Customer {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String accountNumber;
    private String name;
    private String email;
    private String address;
    private String serviceType; // RESIDENTIAL, COMMERCIAL, INDUSTRIAL
    private String status; // ACTIVE, INACTIVE
}
