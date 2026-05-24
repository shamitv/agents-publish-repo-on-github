package com.warehouse.controller;
import com.warehouse.model.InventoryItem;
import com.warehouse.service.InventoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController
@RequestMapping("/api/inventory")
public class InventoryController {
    @Autowired
    private InventoryService inventoryService;
    @GetMapping
    public ResponseEntity<List<InventoryItem>> listAll() {
        return ResponseEntity.ok(inventoryService.listAll());
    }
    @GetMapping("/low-stock")
    public ResponseEntity<List<InventoryItem>> listLowStock() {
        return ResponseEntity.ok(inventoryService.listLowStock());
    }
    @GetMapping("/{id}")
    public ResponseEntity<InventoryItem> getById(@PathVariable Long id) {
        return inventoryService.getById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
    @PostMapping
    @PreAuthorize("hasAnyRole('SUPERVISOR', 'ADMIN')")
    public ResponseEntity<?> create(@RequestBody InventoryItem item) {
        try {
            InventoryItem created = inventoryService.create(item);
            return ResponseEntity.ok(created);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('SUPERVISOR', 'ADMIN')")
    public ResponseEntity<?> update(@PathVariable Long id, @RequestBody InventoryItem details) {
        try {
            InventoryItem updated = inventoryService.update(id, details);
            return ResponseEntity.ok(updated);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        try {
            inventoryService.delete(id);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
    // not the SUPERVISOR or ADMIN role. Any warehouse worker account discovered via the
    // LDAP injection in step 1 can modify quantities for any item.
    @PostMapping("/{id}/adjust")
    public ResponseEntity<?> adjustQuantity(
            @PathVariable Long id,
            @RequestParam int delta) {
        try {
            // Missing @PreAuthorize role check — any authenticated user can adjust stock
            InventoryItem updated = inventoryService.getById(id)
                    .map(item -> {
                        item.setQuantity(item.getQuantity() + delta);
                        return inventoryService.create(item);
                    })
                    .orElseThrow(() -> new RuntimeException("Item not found"));
            return ResponseEntity.ok(updated);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}