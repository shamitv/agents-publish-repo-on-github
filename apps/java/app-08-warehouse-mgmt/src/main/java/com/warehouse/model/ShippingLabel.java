package com.warehouse.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "shipping_labels")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ShippingLabel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "order_id", nullable = false)
    private Long orderId;

    @Column(nullable = false, length = 50)
    private String carrier;

    @Column(length = 50)
    private String trackingNumber;

    @Column(length = 500)
    private String labelUrl;

    @Lob
    private byte[] labelData;

    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}
