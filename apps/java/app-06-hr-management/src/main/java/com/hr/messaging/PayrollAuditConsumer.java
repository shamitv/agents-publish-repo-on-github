package com.hr.messaging;

import com.hr.events.PayrollAuditEvent;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "app.kafka.enabled", havingValue = "true")
public class PayrollAuditConsumer {
    private static final Logger LOGGER = LogManager.getLogger(PayrollAuditConsumer.class);

    @KafkaListener(topics = "${app.kafka.audit-topic}", groupId = "${spring.kafka.consumer.group-id}")
    public void consume(PayrollAuditEvent event) {
        // VULNERABILITY A08: Logs externally supplied audit event content through Log4j 2.14.1.
        LOGGER.info("Payroll audit event consumed: " + event);
    }
}
