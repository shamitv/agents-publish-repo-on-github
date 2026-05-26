package com.energy.billing.controller;

import com.energy.billing.model.Tariff;
import com.energy.billing.service.TariffService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/tariffs")
public class TariffController {

    private final TariffService tariffService;

    public TariffController(TariffService tariffService) {
        this.tariffService = tariffService;
    }

    @GetMapping
    @PreAuthorize("hasRole('BILLING_ADMIN')")
    public ResponseEntity<List<Tariff>> getTariffs() {
        return ResponseEntity.ok(tariffService.getAllTariffs());
    }
}
