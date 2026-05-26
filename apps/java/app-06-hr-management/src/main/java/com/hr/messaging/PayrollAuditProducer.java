package com.hr.messaging;

import com.hr.events.PayrollAuditEvent;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
public class PayrollAuditProducer {
    private final ObjectProvider<KafkaTemplate<Object, Object>> kafkaTemplateProvider;
    private final String topicName;
    private final boolean enabled;

    public PayrollAuditProducer(
            ObjectProvider<KafkaTemplate<Object, Object>> kafkaTemplateProvider,
            @Value("${app.kafka.audit-topic:hr-payroll-audit}") String topicName,
            @Value("${app.kafka.enabled:false}") boolean enabled) {
        this.kafkaTemplateProvider = kafkaTemplateProvider;
        this.topicName = topicName;
        this.enabled = enabled;
    }

    public void publishPayrollRead(Long employeeId) {
        if (!enabled) {
            return;
        }

        KafkaTemplate<Object, Object> kafkaTemplate = kafkaTemplateProvider.getIfAvailable();
        if (kafkaTemplate != null) {
            PayrollAuditEvent event = new PayrollAuditEvent(employeeId, "PAYROLL_READ", Instant.now());
            kafkaTemplate.send(topicName, String.valueOf(employeeId), event);
        }
    }
}
