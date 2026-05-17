package com.hr.controller;

import com.hr.dto.PayrollDTO;
import com.hr.service.PayrollService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/payroll")
public class PayrollController {

    @Autowired
    private PayrollService payrollService;

    // Retrieve payroll data
    @GetMapping("/{employeeId}")
    public ResponseEntity<PayrollDTO> getPayroll(@PathVariable Long employeeId) {
        return payrollService.getSalaryByEmployeeId(employeeId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // Decoy Safe Endpoint: correctly restricted to HR_ADMIN
    @GetMapping("/report")
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<byte[]> getPayrollReport() {
        String csv = payrollService.generateMonthlyReportCsv();
        byte[] csvBytes = csv.getBytes();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=payroll_report.csv")
                .contentType(MediaType.parseMediaType("text/csv"))
                .contentLength(csvBytes.length)
                .body(csvBytes);
    }
}
