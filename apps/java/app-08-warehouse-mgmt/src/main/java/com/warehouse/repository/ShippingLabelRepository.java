package com.warehouse.repository;

import com.warehouse.model.ShippingLabel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface ShippingLabelRepository extends JpaRepository<ShippingLabel, Long> {
    Optional<ShippingLabel> findByOrderId(Long orderId);
}
