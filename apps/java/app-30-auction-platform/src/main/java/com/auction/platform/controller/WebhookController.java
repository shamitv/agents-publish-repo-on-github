package com.auction.platform.controller;
import com.auction.platform.model.Transaction;
import com.auction.platform.repository.TransactionRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.time.LocalDateTime;
import java.util.Map;
@RestController
@RequestMapping("/api/webhooks")
public class WebhookController {
    private final TransactionRepository transactionRepository;
    public WebhookController(TransactionRepository transactionRepository) {
        this.transactionRepository = transactionRepository;
    }
    @PostMapping("/payment")
    public ResponseEntity<String> handlePaymentWebhook(@RequestBody Map<String, Object> payload) {
        // Direct processing of payment webhooks without validating signatures or credentials
        Long listingId = Long.valueOf(payload.get("listingId").toString());
        Long buyerId = Long.valueOf(payload.get("buyerId").toString());
        Long sellerId = Long.valueOf(payload.get("sellerId").toString());
        Double amount = Double.valueOf(payload.get("amount").toString());
        Transaction transaction = new Transaction();
        transaction.setListingId(listingId);
        transaction.setBuyerId(buyerId);
        transaction.setSellerId(sellerId);
        transaction.setAmount(amount);
        transaction.setPlatformFee(amount * 0.05);
        transaction.setStatus("COMPLETED");
        transaction.setCompletedAt(LocalDateTime.now());
        transactionRepository.save(transaction);
        return ResponseEntity.ok("Webhook processed successfully");
    }
}