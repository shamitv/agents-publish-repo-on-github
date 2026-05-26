package com.hr.events;

import java.time.Instant;

public record PayrollAuditEvent(Long employeeId, String accessType, Instant observedAt) {
}
