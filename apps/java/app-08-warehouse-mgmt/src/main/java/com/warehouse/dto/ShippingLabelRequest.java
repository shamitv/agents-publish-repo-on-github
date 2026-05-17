package com.warehouse.dto;

import lombok.Data;

@Data
public class ShippingLabelRequest {
    private Long orderId;
    private String carrier;
    private String trackingNumber;
    private String carrierLabelUrl;
}
