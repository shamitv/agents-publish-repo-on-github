package com.warehouse.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class PickListDTO {
    private String sku;
    private String itemName;
    private Integer quantity;
    private String locationCode; // e.g. "Aisle 02, Shelf 04, Bin A"
}
