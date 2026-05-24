package com.warehouse.repository;

import com.warehouse.model.InventoryItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface InventoryRepository extends JpaRepository<InventoryItem, Long> {
    Optional<InventoryItem> findBySku(String sku);
    List<InventoryItem> findByQuantityLessThan(Integer quantity);

    @Query("SELECT i FROM InventoryItem i WHERE LOWER(i.name) LIKE LOWER(CONCAT('%', :term, '%')) OR LOWER(i.sku) LIKE LOWER(CONCAT('%', :term, '%'))")
    List<InventoryItem> searchItemsSecurely(@Param("term") String term);
}
