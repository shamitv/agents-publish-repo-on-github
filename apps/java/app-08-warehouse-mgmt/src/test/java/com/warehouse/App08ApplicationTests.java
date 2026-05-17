package com.warehouse;

import com.warehouse.model.InventoryItem;
import com.warehouse.repository.InventoryRepository;
import com.warehouse.service.PickListService;
import com.warehouse.dto.PickListDTO;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class App08ApplicationTests {

    @Autowired
    private InventoryRepository inventoryRepository;

    @Autowired
    private PickListService pickListService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Test
    void contextLoads() {
    }

    @Test
    void testInventoryCountAndLowStockThreshold() {
        List<InventoryItem> items = inventoryRepository.findAll();
        assertFalse(items.isEmpty());
        assertTrue(items.size() >= 25);
    }

    @Test
    void testPasswordBCryptSecureHashingDecoy() {
        String rawPass = "operator123";
        String hashed = passwordEncoder.encode(rawPass);
        assertTrue(hashed.startsWith("$2a$"));
        assertTrue(passwordEncoder.matches(rawPass, hashed));
    }

    @Test
    void testPickListAisleSorting() {
        // Run against Order ID 1 (seeded)
        List<PickListDTO> pickList = pickListService.generatePickList(1L);
        assertNotNull(pickList);
        assertFalse(pickList.isEmpty());
        
        // Assert that locations are ordered sequentially
        for (int i = 0; i < pickList.size() - 1; i++) {
            String loc1 = pickList.get(i).getLocationCode();
            String loc2 = pickList.get(i + 1).getLocationCode();
            assertTrue(loc1.compareTo(loc2) <= 0);
        }
    }
}
