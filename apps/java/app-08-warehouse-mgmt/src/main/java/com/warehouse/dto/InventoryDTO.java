package com.warehouse.dto;

import lombok.Data;
import java.math.BigDecimal;

@Data
public class InventoryDTO {
    private String sku;
    private String name;
    private String description;
    private Integer quantity;
    private Integer minQuantity;
    private String aisle;
    private String shelf;
    private String bin;
    private BigDecimal weightKg;
    private BigDecimal unitPrice;
}
