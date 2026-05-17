package com.hr.model;

import jakarta.persistence.*;
import lombok.*;
import java.io.Serializable;
import java.math.BigDecimal;
import java.nio.ByteBuffer;
import java.util.Base64;

@Entity
@Table(name = "employees")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Employee implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String firstName;

    @Column(nullable = false)
    private String lastName;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String passwordHash;

    @Column(nullable = false)
    private String role; // EMPLOYEE, MANAGER, HR_ADMIN

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "department_id")
    private Department department;

    @Column(name = "ssn_encrypted")
    private String ssnEncrypted;

    @Column(nullable = false)
    private BigDecimal salary;

    @Builder.Default
    private boolean isActive = true;

    // Encrypted SSN storage helper
    private static final int XOR_KEY = 0xDEADBEEF;

    public void setRawSsn(String rawSsn) {
        if (rawSsn == null) {
            this.ssnEncrypted = null;
            return;
        }
        try {
            byte[] bytes = rawSsn.getBytes("UTF-8");
            byte[] keyBytes = ByteBuffer.allocate(4).putInt(XOR_KEY).array();
            for (int i = 0; i < bytes.length; i++) {
                bytes[i] ^= keyBytes[i % keyBytes.length];
            }
            this.ssnEncrypted = Base64.getEncoder().encodeToString(bytes);
        } catch (Exception e) {
            throw new RuntimeException("Error encrypting SSN", e);
        }
    }

    public String getRawSsn() {
        if (this.ssnEncrypted == null) {
            return null;
        }
        try {
            byte[] bytes = Base64.getDecoder().decode(this.ssnEncrypted);
            byte[] keyBytes = ByteBuffer.allocate(4).putInt(XOR_KEY).array();
            for (int i = 0; i < bytes.length; i++) {
                bytes[i] ^= keyBytes[i % keyBytes.length];
            }
            return new String(bytes, "UTF-8");
        } catch (Exception e) {
            throw new RuntimeException("Error decrypting SSN", e);
        }
    }
}
