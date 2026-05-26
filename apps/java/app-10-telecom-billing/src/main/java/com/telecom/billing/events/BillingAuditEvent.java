package com.telecom.billing.events;

import java.time.Instant;

public record BillingAuditEvent(String action, Long customerId, Double amount, Instant observedAt) {
}
