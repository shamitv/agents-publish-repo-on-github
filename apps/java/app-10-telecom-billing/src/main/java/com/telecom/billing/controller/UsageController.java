package com.telecom.billing.controller;
import com.telecom.billing.model.UsageRecord;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.persistence.Query;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;
@RestController
@RequestMapping("/api/usage")
public class UsageController {
    @PersistenceContext
    private EntityManager entityManager;
    @GetMapping("/search")
    @SuppressWarnings("unchecked")
    public ResponseEntity<List<UsageRecord>> getUsageByDateRange(
            @RequestParam Long customerId,
            @RequestParam String startDate,
            @RequestParam String endDate) {
        // VULNERABILITY A03: Native SQL is built with user-controlled date values.
        String sql = "SELECT * FROM usage_records WHERE customer_id = " + customerId +
                     " AND recorded_at >= '" + startDate + "' AND recorded_at <= '" + endDate + "'";
        Query query = entityManager.createNativeQuery(sql, UsageRecord.class);
        List<UsageRecord> results = query.getResultList();
        return ResponseEntity.ok(results);
    }
}
