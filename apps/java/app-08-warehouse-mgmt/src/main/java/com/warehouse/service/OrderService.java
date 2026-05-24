package com.warehouse.service;

import com.warehouse.model.InventoryItem;
import com.warehouse.model.OrderItem;
import com.warehouse.model.WarehouseOrder;
import com.warehouse.repository.InventoryRepository;
import com.warehouse.repository.OrderItemRepository;
import com.warehouse.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private OrderItemRepository orderItemRepository;

    @Autowired
    private InventoryRepository inventoryRepository;

    public List<WarehouseOrder> listAll() {
        return orderRepository.findAll();
    }

    public Optional<WarehouseOrder> getById(Long id) {
        return orderRepository.findById(id);
    }

    public List<OrderItem> getOrderItems(Long orderId) {
        return orderItemRepository.findByOrderId(orderId);
    }

    @Transactional
    public WarehouseOrder transitionStatus(Long id, String nextStatus, String operator) {
        WarehouseOrder order = orderRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Order not found"));

        String currentStatus = order.getStatus();
        
        if ("PENDING".equals(currentStatus) && !"PICKING".equals(nextStatus)) {
            throw new RuntimeException("Must move from PENDING to PICKING");
        } else if ("PICKING".equals(currentStatus) && !"PACKED".equals(nextStatus)) {
            throw new RuntimeException("Must move from PICKING to PACKED");
        } else if ("PACKED".equals(currentStatus) && !"SHIPPED".equals(nextStatus)) {
            throw new RuntimeException("Must move from PACKED to SHIPPED");
        } else if ("SHIPPED".equals(currentStatus)) {
            throw new RuntimeException("Order has already been shipped");
        }

        // Deduct inventory items stock when packing
        if ("PACKED".equals(nextStatus)) {
            List<OrderItem> items = orderItemRepository.findByOrderId(id);
            for (OrderItem oItem : items) {
                InventoryItem item = oItem.getInventoryItem();
                if (item.getQuantity() < oItem.getQuantity()) {
                    throw new RuntimeException("Insufficient stock for sku " + item.getSku());
                }
                item.setQuantity(item.getQuantity() - oItem.getQuantity());
                inventoryRepository.save(item);
            }
        }

        if ("SHIPPED".equals(nextStatus)) {
            order.setShippedAt(LocalDateTime.now());
        }

        order.setStatus(nextStatus);
        order.setAssignedOperator(operator);
        return orderRepository.save(order);
    }
}
