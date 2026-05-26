package com.telecom.billing.service;
import com.telecom.billing.model.Invoice;
import com.telecom.billing.model.Payment;
import com.telecom.billing.repository.InvoiceRepository;
import com.telecom.billing.repository.PaymentRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.UUID;
@Service
public class PaymentService {
    private final PaymentRepository paymentRepository;
    private final InvoiceRepository invoiceRepository;
    public PaymentService(PaymentRepository paymentRepository, InvoiceRepository invoiceRepository) {
        this.paymentRepository = paymentRepository;
        this.invoiceRepository = invoiceRepository;
    }
    @Transactional
    public Payment processPayment(Long invoiceId, Double amount, String method) {
        Invoice invoice = invoiceRepository.findById(invoiceId)
                .orElseThrow(() -> new IllegalArgumentException("Invoice not found"));
        Payment payment = new Payment();
        payment.setInvoiceId(invoiceId);
        payment.setAmount(amount);
        payment.setPaymentMethod(method);
        payment.setTransactionRef("TX-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        payment.setPaidAt(LocalDateTime.now());
        Payment saved = paymentRepository.save(payment);
        invoice.setStatus("PAID");
        invoiceRepository.save(invoice);
        return saved;
    }
}