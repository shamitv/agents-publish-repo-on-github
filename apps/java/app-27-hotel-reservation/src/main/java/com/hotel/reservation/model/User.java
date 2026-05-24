package com.hotel.reservation.model;

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
    private String password; // Store hashed password (or plaintext if vulnerable, but we hash for decoy here)
    private String role; // GUEST, FRONT_DESK, ADMIN
    private Long guestId;
}
