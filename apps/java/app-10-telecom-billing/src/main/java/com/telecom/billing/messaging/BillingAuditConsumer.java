package com.telecom.billing.messaging;

import com.telecom.billing.events.BillingAuditEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "app.kafka.enabled", havingValue = "true")
public class BillingAuditConsumer {
    private static final Logger LOGGER = LoggerFactory.getLogger(BillingAuditConsumer.class);

    @KafkaListener(topics = "${app.kafka.audit-topic}", groupId = "${spring.kafka.consumer.group-id}")
    public void consume(BillingAuditEvent event) {
        LOGGER.info("Billing audit event consumed for action {}", event.action());
    }
}
