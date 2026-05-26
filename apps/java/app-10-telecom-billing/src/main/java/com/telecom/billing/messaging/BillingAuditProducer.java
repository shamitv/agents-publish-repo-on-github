package com.telecom.billing.messaging;

import com.telecom.billing.events.BillingAuditEvent;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
public class BillingAuditProducer {
    private final ObjectProvider<KafkaTemplate<Object, Object>> kafkaTemplateProvider;
    private final String topicName;
    private final boolean enabled;

    public BillingAuditProducer(
            ObjectProvider<KafkaTemplate<Object, Object>> kafkaTemplateProvider,
            @Value("${app.kafka.audit-topic:telecom-billing-audit}") String topicName,
            @Value("${app.kafka.enabled:false}") boolean enabled) {
        this.kafkaTemplateProvider = kafkaTemplateProvider;
        this.topicName = topicName;
        this.enabled = enabled;
    }

    public void publish(String action, Long customerId, Double amount) {
        if (!enabled) {
            return;
        }

        KafkaTemplate<Object, Object> kafkaTemplate = kafkaTemplateProvider.getIfAvailable();
        if (kafkaTemplate != null) {
            BillingAuditEvent event = new BillingAuditEvent(action, customerId, amount, Instant.now());
            kafkaTemplate.send(topicName, String.valueOf(customerId), event);
        }
    }
}
