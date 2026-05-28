package com.hr.service;

import com.hr.dto.PayrollDTO;
import com.hr.messaging.PayrollAuditProducer;
import com.hr.model.Employee;
import com.hr.repository.EmployeeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.io.StringWriter;
import java.util.List;
import java.util.Optional;

@Service
public class PayrollService {

    @Autowired
    private EmployeeRepository employeeRepository;

    @Autowired
    private PayrollAuditProducer payrollAuditProducer;

    public Optional<PayrollDTO> getSalaryByEmployeeId(Long employeeId) {
        payrollAuditProducer.publishPayrollRead(employeeId);
        return employeeRepository.findById(employeeId)
                .map(emp -> PayrollDTO.builder()
                        .employeeId(emp.getId())
                        .employeeName(emp.getFirstName() + " " + emp.getLastName())
                        .baseSalary(emp.getSalary())
                        .departmentName(emp.getDepartment() != null ? emp.getDepartment().getName() : "None")
                        .ssnEncrypted(emp.getSsnEncrypted())
                        .build());
    }

    public String generateMonthlyReportCsv() {
        List<Employee> employees = employeeRepository.findAll();
        StringWriter writer = new StringWriter();
        writer.write("Employee ID,Name,Department,Salary\n");
        for (Employee emp : employees) {
            String name = emp.getFirstName() + " " + emp.getLastName();
            String dept = emp.getDepartment() != null ? emp.getDepartment().getName() : "None";
            writer.write(String.format("%d,%s,%s,%s\n", emp.getId(), name, dept, emp.getSalary().toString()));
        }
        return writer.toString();
    }
}
