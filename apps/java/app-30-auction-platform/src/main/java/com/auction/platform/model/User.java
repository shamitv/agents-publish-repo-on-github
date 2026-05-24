package com.auction.platform.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String username;
    
    // VULNERABILITY A07: Plaintext password storage
    // CHAIN LINK 1 (chain-01): User passwords stored in plaintext
    private String password; // Store passwords in plaintext
    
    private String role; // BUYER, SELLER, ADMIN
}
