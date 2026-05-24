package com.telecom.billing.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "customers")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Customer {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private String email;
    private String phone;
    private String username;
    private String passwordHash;
    private String role; // CUSTOMER, ADMIN
    private Long planId;
    private String accountStatus; // ACTIVE, SUSPENDED
    private Double balance;
    private LocalDateTime createdAt;
}
