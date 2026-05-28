package com.telecom.billing.service;

import com.telecom.billing.model.Invoice;
import com.telecom.billing.repository.InvoiceRepository;
import com.telecom.billing.search.InvoiceSearchClient;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class BillingService {

    private final InvoiceRepository invoiceRepository;
    private final InvoiceSearchClient invoiceSearchClient;

    public BillingService(InvoiceRepository invoiceRepository, InvoiceSearchClient invoiceSearchClient) {
        this.invoiceRepository = invoiceRepository;
        this.invoiceSearchClient = invoiceSearchClient;
    }

    // CHAIN LINK 3 (chain-02): Bulk invoice reads cross no audit boundary —
    // BillingAuditProducer is available but never called during customer invoice retrieval.
    // VULNERABILITY A09: Get-invoice queries bypass the configured billing audit producer.
    public List<Invoice> getInvoicesByCustomer(Long customerId) {
        return invoiceRepository.findByCustomerId(customerId);
    }

    public Optional<Invoice> getInvoiceById(Long id) {
        return invoiceRepository.findById(id);
    }

    public Invoice saveInvoice(Invoice invoice) {
        Invoice saved = invoiceRepository.save(invoice);
        invoiceSearchClient.index(saved);
        return saved;
    }
}
