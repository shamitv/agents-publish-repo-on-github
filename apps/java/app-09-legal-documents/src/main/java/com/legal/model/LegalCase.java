package com.legal.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "legal_cases")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LegalCase {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 150)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false, length = 50)
    private String clientOwner; // Mapped to the client username

    @Column(nullable = false, length = 20)
    @Builder.Default
    private String status = "ACTIVE"; // ACTIVE, CLOSED

    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}
