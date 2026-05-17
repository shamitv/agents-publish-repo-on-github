package com.warehouse.service;

import com.warehouse.model.InventoryItem;
import com.warehouse.repository.InventoryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class InventoryService {

    @Autowired
    private InventoryRepository inventoryRepository;

    public List<InventoryItem> listAll() {
        return inventoryRepository.findAll();
    }

    public List<InventoryItem> listLowStock() {
        // Return items whose quantity is strictly less than their low-stock threshold (minQuantity)
        return inventoryRepository.findAll().stream()
                .filter(item -> item.getQuantity() < item.getMinQuantity())
                .toList();
    }

    public Optional<InventoryItem> getById(Long id) {
        return inventoryRepository.findById(id);
    }

    public InventoryItem create(InventoryItem item) {
        if (inventoryRepository.findBySku(item.getSku()).isPresent()) {
            throw new RuntimeException("SKU already exists: " + item.getSku());
        }
        item.setCreatedAt(LocalDateTime.now());
        return inventoryRepository.save(item);
    }

    public InventoryItem update(Long id, InventoryItem details) {
        InventoryItem item = inventoryRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Item not found"));
        
        item.setName(details.getName());
        item.setDescription(details.getDescription());
        item.setQuantity(details.getQuantity());
        item.setMinQuantity(details.getMinQuantity());
        item.setAisle(details.getAisle());
        item.setShelf(details.getShelf());
        item.setBin(details.getBin());
        item.setWeightKg(details.getWeightKg());
        item.setUnitPrice(details.getUnitPrice());
        item.setLastRestocked(LocalDateTime.now());
        
        return inventoryRepository.save(item);
    }

    public void delete(Long id) {
        inventoryRepository.deleteById(id);
    }
}
