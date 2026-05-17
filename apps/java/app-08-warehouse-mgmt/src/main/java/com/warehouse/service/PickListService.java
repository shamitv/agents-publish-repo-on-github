package com.warehouse.service;

import com.warehouse.dto.PickListDTO;
import com.warehouse.model.OrderItem;
import com.warehouse.repository.OrderItemRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class PickListService {

    @Autowired
    private OrderItemRepository orderItemRepository;

    public List<PickListDTO> generatePickList(Long orderId) {
        List<OrderItem> items = orderItemRepository.findByOrderId(orderId);
        
        // Arrange items by location (Aisle, Shelf, Bin) for warehouse path efficiency
        return items.stream()
                .sorted(Comparator.comparing((OrderItem oi) -> oi.getInventoryItem().getAisle())
                        .thenComparing(oi -> oi.getInventoryItem().getShelf())
                        .thenComparing(oi -> oi.getInventoryItem().getBin()))
                .map(oi -> PickListDTO.builder()
                        .sku(oi.getInventoryItem().getSku())
                        .itemName(oi.getInventoryItem().getName())
                        .quantity(oi.getQuantity())
                        .locationCode("Aisle " + oi.getInventoryItem().getAisle() + 
                                      ", Shelf " + oi.getInventoryItem().getShelf() + 
                                      ", Bin " + oi.getInventoryItem().getBin())
                        .build())
                .collect(Collectors.toList());
    }
}
