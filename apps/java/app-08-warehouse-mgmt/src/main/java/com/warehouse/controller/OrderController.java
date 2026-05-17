package com.warehouse.controller;

import com.warehouse.dto.PickListDTO;
import com.warehouse.model.OrderItem;
import com.warehouse.model.WarehouseOrder;
import com.warehouse.service.OrderService;
import com.warehouse.service.PickListService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @Autowired
    private OrderService orderService;

    @Autowired
    private PickListService pickListService;

    @GetMapping
    public ResponseEntity<List<WarehouseOrder>> listAll() {
        return ResponseEntity.ok(orderService.listAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<WarehouseOrder> getById(@PathVariable Long id) {
        return orderService.getById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/{id}/items")
    public ResponseEntity<List<OrderItem>> getItems(@PathVariable Long id) {
        return ResponseEntity.ok(orderService.getOrderItems(id));
    }

    @GetMapping("/{id}/picklist")
    @PreAuthorize("hasAnyRole('OPERATOR', 'SUPERVISOR', 'ADMIN')")
    public ResponseEntity<List<PickListDTO>> getPickList(@PathVariable Long id) {
        return ResponseEntity.ok(pickListService.generatePickList(id));
    }

    @PutMapping("/{id}/status")
    @PreAuthorize("hasAnyRole('OPERATOR', 'SUPERVISOR', 'ADMIN')")
    public ResponseEntity<?> updateStatus(
            @PathVariable Long id,
            @RequestBody Map<String, String> payload,
            @AuthenticationPrincipal UserDetails userDetails) {
        
        String nextStatus = payload.get("status");
        if (nextStatus == null) {
            return ResponseEntity.badRequest().body("Status is required");
        }

        try {
            WarehouseOrder updated = orderService.transitionStatus(id, nextStatus, userDetails.getUsername());
            return ResponseEntity.ok(updated);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}
