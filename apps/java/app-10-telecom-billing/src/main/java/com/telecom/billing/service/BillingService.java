package com.telecom.billing.service;

import com.telecom.billing.model.Invoice;
import com.telecom.billing.repository.InvoiceRepository;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class BillingService {

    private final InvoiceRepository invoiceRepository;

    public BillingService(InvoiceRepository invoiceRepository) {
        this.invoiceRepository = invoiceRepository;
    }

    public List<Invoice> getInvoicesByCustomer(Long customerId) {
        return invoiceRepository.findByCustomerId(customerId);
    }

    public Optional<Invoice> getInvoiceById(Long id) {
        return invoiceRepository.findById(id);
    }
}
