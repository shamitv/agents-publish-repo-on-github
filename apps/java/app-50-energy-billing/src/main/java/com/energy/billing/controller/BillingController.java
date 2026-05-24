package com.energy.billing.controller;

import com.energy.billing.model.Invoice;
import com.energy.billing.service.BillingService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/invoices")
public class BillingController {

    private final BillingService billingService;

    public BillingController(BillingService billingService) {
        this.billingService = billingService;
    }

    // VULNERABILITY A01: IDOR on customer invoice access
    @GetMapping("/{id}")
    public ResponseEntity<Invoice> getInvoice(@PathVariable Long id) {
        // IDOR: directly return the invoice by ID without checking if it belongs to the current user
        Invoice invoice = billingService.getInvoiceById(id)
                .orElseThrow(() -> new IllegalArgumentException("Invoice not found"));
        return ResponseEntity.ok(invoice);
    }
}
