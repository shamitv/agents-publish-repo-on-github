package com.hr.messaging;

import com.hr.events.PayrollAuditEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "app.kafka.enabled", havingValue = "true")
public class PayrollAuditConsumer {
    private static final Logger LOGGER = LoggerFactory.getLogger(PayrollAuditConsumer.class);

    @KafkaListener(topics = "${app.kafka.audit-topic}", groupId = "${spring.kafka.consumer.group-id}")
    public void consume(PayrollAuditEvent event) {
        LOGGER.info("Payroll audit event consumed for employee {}", event.employeeId());
    }
}
