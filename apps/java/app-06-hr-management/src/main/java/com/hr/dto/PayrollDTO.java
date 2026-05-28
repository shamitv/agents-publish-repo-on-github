package com.hr.dto;

import lombok.*;
import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PayrollDTO {
    private Long employeeId;
    private String employeeName;
    private BigDecimal baseSalary;
    private String departmentName;
    private String ssnEncrypted;
}
