package com.warehouse.repository;

import com.warehouse.model.WarehouseOrder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface OrderRepository extends JpaRepository<WarehouseOrder, Long> {
    List<WarehouseOrder> findByStatus(String status);
    Optional<WarehouseOrder> findByOrderNumber(String orderNumber);
}
