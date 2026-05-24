package com.warehouse.config;

import com.warehouse.model.InventoryItem;
import com.warehouse.model.OrderItem;
import com.warehouse.model.User;
import com.warehouse.model.WarehouseOrder;
import com.warehouse.repository.InventoryRepository;
import com.warehouse.repository.OrderItemRepository;
import com.warehouse.repository.OrderRepository;
import com.warehouse.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private InventoryRepository inventoryRepository;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private OrderItemRepository orderItemRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        if (userRepository.count() > 0) {
            return;
        }

        userRepository.save(User.builder()
                .username("operator")
                .passwordHash(passwordEncoder.encode("operator123"))
                .role("OPERATOR")
                .build());

        userRepository.save(User.builder()
                .username("supervisor")
                .passwordHash(passwordEncoder.encode("supervisor123"))
                .role("SUPERVISOR")
                .build());

        userRepository.save(User.builder()
                .username("admin")
                .passwordHash(passwordEncoder.encode("admin123"))
                .role("ADMIN")
                .build());

        List<InventoryItem> items = new ArrayList<>();
        String[] aisles = {"01", "02", "03", "04", "05"};
        String[] shelves = {"A", "B", "C"};
        String[] bins = {"1", "2", "3"};

        int index = 1;
        for (String aisle : aisles) {
            for (String shelf : shelves) {
                for (String bin : bins) {
                    if (index > 25) break;
                    
                    int qty = (index % 3 == 0) ? 5 : 50; // some are low stock
                    int minQty = 15;
                    
                    items.add(InventoryItem.builder()
                            .sku("SKU-WH-" + String.format("%03d", index))
                            .name("Industrial Item " + index)
                            .description("Heavy-duty item description for part " + index)
                            .quantity(qty)
                            .minQuantity(minQty)
                            .aisle(aisle)
                            .shelf(shelf)
                            .bin(bin)
                            .weightKg(new BigDecimal(1.5 * index).setScale(2, BigDecimal.ROUND_HALF_UP))
                            .unitPrice(new BigDecimal(12.50 * index).setScale(2, BigDecimal.ROUND_HALF_UP))
                            .lastRestocked(LocalDateTime.now().minusDays(index))
                            .build());
                    index++;
                }
            }
        }
        inventoryRepository.saveAll(items);

        List<WarehouseOrder> orders = new ArrayList<>();
        
        orders.add(WarehouseOrder.builder()
                .orderNumber("ORD-99001")
                .customerName("Acme Industries")
                .customerAddress("123 Industrial Parkway, Suite A")
                .status("PENDING")
                .build());

        orders.add(WarehouseOrder.builder()
                .orderNumber("ORD-99002")
                .customerName("Global Logistics Corp")
                .customerAddress("456 Terminal Ave, Bay 4")
                .status("PICKING")
                .assignedOperator("operator")
                .build());

        orders.add(WarehouseOrder.builder()
                .orderNumber("ORD-99003")
                .customerName("Zenith Mfg")
                .customerAddress("789 Assembly Rd")
                .status("PACKED")
                .assignedOperator("operator")
                .build());

        orders.add(WarehouseOrder.builder()
                .orderNumber("ORD-99004")
                .customerName("Nexus Suppliers")
                .customerAddress("101 Supply Chain Blvd")
                .status("SHIPPED")
                .assignedOperator("supervisor")
                .shippedAt(LocalDateTime.now().minusHours(2))
                .build());

        orders.add(WarehouseOrder.builder()
                .orderNumber("ORD-99005")
                .customerName("Dynasty Retailers")
                .customerAddress("202 Market Square")
                .status("PENDING")
                .build());

        orders.add(WarehouseOrder.builder()
                .orderNumber("ORD-99006")
                .customerName("Summit Logistics")
                .customerAddress("303 Altitude Way")
                .status("PENDING")
                .build());

        orders.add(WarehouseOrder.builder()
                .orderNumber("ORD-99007")
                .customerName("Horizon Partners")
                .customerAddress("404 Skyline Dr")
                .status("PICKING")
                .assignedOperator("operator")
                .build());

        orders.add(WarehouseOrder.builder()
                .orderNumber("ORD-99008")
                .customerName("Vertex Solutions")
                .customerAddress("505 Zenith Road")
                .status("SHIPPED")
                .assignedOperator("admin")
                .shippedAt(LocalDateTime.now().minusDays(1))
                .build());

        orderRepository.saveAll(orders);

        List<InventoryItem> savedItems = inventoryRepository.findAll();
        
        for (WarehouseOrder o : orders) {
            orderItemRepository.save(OrderItem.builder()
                    .orderId(o.getId())
                    .inventoryItem(savedItems.get(0))
                    .quantity(2)
                    .picked("SHIPPED".equals(o.getStatus()) || "PACKED".equals(o.getStatus()))
                    .build());
            
            orderItemRepository.save(OrderItem.builder()
                    .orderId(o.getId())
                    .inventoryItem(savedItems.get(2))
                    .quantity(1)
                    .picked("SHIPPED".equals(o.getStatus()) || "PACKED".equals(o.getStatus()))
                    .build());
        }
    }
}
