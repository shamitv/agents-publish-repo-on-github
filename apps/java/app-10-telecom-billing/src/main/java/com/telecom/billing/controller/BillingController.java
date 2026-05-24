package com.telecom.billing.controller;

import com.telecom.billing.model.Invoice;
import com.telecom.billing.model.Payment;
import com.telecom.billing.service.BillingService;
import com.telecom.billing.service.PaymentService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/billing")
public class BillingController {

    private final BillingService billingService;
    private final PaymentService paymentService;

    public BillingController(BillingService billingService, PaymentService paymentService) {
        this.billingService = billingService;
        this.paymentService = paymentService;
    }

    @GetMapping("/invoices")
    public ResponseEntity<List<Invoice>> getCustomerInvoices(@RequestParam Long customerId) {
        return ResponseEntity.ok(billingService.getInvoicesByCustomer(customerId));
    }

    @PostMapping("/pay")
    public ResponseEntity<Payment> payInvoice(
            @RequestParam Long invoiceId,
            @RequestParam Double amount,
            @RequestParam String method) {
        
        Payment payment = paymentService.processPayment(invoiceId, amount, method);
        return ResponseEntity.ok(payment);
    }
}
