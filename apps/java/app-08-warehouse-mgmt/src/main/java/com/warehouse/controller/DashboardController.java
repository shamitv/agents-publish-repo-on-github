package com.warehouse.controller;

import com.warehouse.model.InventoryItem;
import com.warehouse.model.WarehouseOrder;
import com.warehouse.service.InventoryService;
import com.warehouse.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    @Autowired
    private InventoryService inventoryService;

    @Autowired
    private OrderService orderService;

    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getStats() {
        List<InventoryItem> lowStock = inventoryService.listLowStock();
        List<WarehouseOrder> allOrders = orderService.listAll();
        
        long pendingOrdersCount = allOrders.stream()
                .filter(o -> "PENDING".equals(o.getStatus()) || "PICKING".equals(o.getStatus()))
                .count();

        long packedOrdersCount = allOrders.stream()
                .filter(o -> "PACKED".equals(o.getStatus()))
                .count();

        Map<String, Object> stats = new HashMap<>();
        stats.put("totalItems", inventoryService.listAll().size());
        stats.put("lowStockCount", lowStock.size());
        stats.put("lowStockItems", lowStock);
        stats.put("pendingOrdersCount", pendingOrdersCount);
        stats.put("packedOrdersCount", packedOrdersCount);
        
        return ResponseEntity.ok(stats);
    }
}
