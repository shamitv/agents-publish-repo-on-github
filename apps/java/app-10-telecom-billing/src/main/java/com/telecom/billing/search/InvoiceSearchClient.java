package com.telecom.billing.search;

import com.telecom.billing.model.Invoice;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
public class InvoiceSearchClient {
    private final RestTemplate searchRestTemplate;
    private final String elasticsearchUrl;
    private final boolean enabled;

    public InvoiceSearchClient(
            RestTemplate searchRestTemplate,
            @Value("${app.elasticsearch.url:http://localhost:9200}") String elasticsearchUrl,
            @Value("${app.elasticsearch.enabled:false}") boolean enabled) {
        this.searchRestTemplate = searchRestTemplate;
        this.elasticsearchUrl = elasticsearchUrl;
        this.enabled = enabled;
    }

    public void index(Invoice invoice) {
        if (!enabled || invoice.getId() == null) {
            return;
        }

        Map<String, Object> document = Map.of(
                "id", invoice.getId(),
                "customerId", invoice.getCustomerId(),
                "billingPeriod", invoice.getBillingPeriod(),
                "totalAmount", invoice.getTotalAmount(),
                "status", invoice.getStatus()
        );

        try {
            searchRestTemplate.put(elasticsearchUrl + "/telecom-invoices/_doc/" + invoice.getId(), document);
        } catch (RestClientException ignored) {
            // Invoice writes are not blocked by optional search indexing failures.
        }
    }
}
