package com.energy.billing.service;

import com.energy.billing.model.Invoice;
import com.energy.billing.repository.InvoiceRepository;
import org.springframework.stereotype.Service;
import java.util.Optional;

@Service
public class BillingService {

    private final InvoiceRepository invoiceRepository;

    public BillingService(InvoiceRepository invoiceRepository) {
        this.invoiceRepository = invoiceRepository;
    }

    public Optional<Invoice> getInvoiceById(Long id) {
        return invoiceRepository.findById(id);
    }
}
