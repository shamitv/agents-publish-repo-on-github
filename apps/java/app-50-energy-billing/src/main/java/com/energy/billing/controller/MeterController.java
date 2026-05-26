package com.energy.billing.controller;
import com.energy.billing.model.MeterReading;
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
@RequestMapping("/api/meters")
public class MeterController {
    @PersistenceContext
    private EntityManager entityManager;
    @GetMapping("/readings/search")
    @SuppressWarnings("unchecked")
    public ResponseEntity<List<MeterReading>> searchReadings(
            @RequestParam String meterSerial,
            @RequestParam String dateRange) {
        // SQL injection: concatenates inputs directly into a native SQL query string
        String sql = "SELECT mr.* FROM meter_readings mr JOIN meters m ON mr.meter_id = m.id " +
                     "WHERE m.meter_serial = '" + meterSerial + "' AND mr.reading_date = '" + dateRange + "'";
        Query query = entityManager.createNativeQuery(sql, MeterReading.class);
        List<MeterReading> results = query.getResultList();
        return ResponseEntity.ok(results);
    }
}