package com.legal.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "legal_documents")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Document {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "case_id", nullable = false)
    private Long caseId;

    @Column(nullable = false, length = 150)
    private String title;

    @Column(nullable = false, length = 150)
    private String filename;

    // Planted Vulnerability A02: Storing highly sensitive legal documents in cleartext
    @Lob
    @Column(name = "file_content_plaintext", nullable = false, columnDefinition = "TEXT")
    private String fileContentPlaintext;

    @Column(nullable = false, length = 50)
    private String uploadedBy;

    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}
