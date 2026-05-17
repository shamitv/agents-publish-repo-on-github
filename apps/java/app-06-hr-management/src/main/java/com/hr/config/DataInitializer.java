package com.hr.config;

import com.hr.model.Department;
import com.hr.model.Employee;
import com.hr.model.LeaveRequest;
import com.hr.repository.DepartmentRepository;
import com.hr.repository.EmployeeRepository;
import com.hr.repository.LeaveRequestRepository;
import com.hr.service.EmployeeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import java.math.BigDecimal;
import java.time.LocalDate;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private DepartmentRepository departmentRepository;

    @Autowired
    private EmployeeService employeeService;

    @Autowired
    private LeaveRequestRepository leaveRequestRepository;

    @Override
    public void run(String... args) throws Exception {
        // 1. Seed Departments
        Department hr = departmentRepository.save(Department.builder().name("Human Resources").build());
        Department eng = departmentRepository.save(Department.builder().name("Engineering").build());
        Department sales = departmentRepository.save(Department.builder().name("Sales").build());

        // 2. Seed Employees
        Employee admin = Employee.builder()
                .firstName("Admin")
                .lastName("User")
                .email("admin@hr.com")
                .passwordHash("admin")
                .role("HR_ADMIN")
                .department(hr)
                .salary(new BigDecimal("120000.00"))
                .build();
        admin.setRawSsn("999-01-0001");
        employeeService.saveEmployee(admin);

        Employee manager = Employee.builder()
                .firstName("Manager")
                .lastName("Bob")
                .email("manager@hr.com")
                .passwordHash("manager")
                .role("MANAGER")
                .department(eng)
                .salary(new BigDecimal("95000.00"))
                .build();
        manager.setRawSsn("999-02-0002");
        employeeService.saveEmployee(manager);

        Employee alice = Employee.builder()
                .firstName("Alice")
                .lastName("Smith")
                .email("alice@hr.com")
                .passwordHash("alice")
                .role("EMPLOYEE")
                .department(eng)
                .salary(new BigDecimal("75000.00"))
                .build();
        alice.setRawSsn("999-03-0003");
        employeeService.saveEmployee(alice);

        Employee bob = Employee.builder()
                .firstName("Bob")
                .lastName("Johnson")
                .email("bob@hr.com")
                .passwordHash("bob")
                .role("EMPLOYEE")
                .department(sales)
                .salary(new BigDecimal("68000.00"))
                .build();
        bob.setRawSsn("999-04-0004");
        employeeService.saveEmployee(bob);

        Employee charlie = Employee.builder()
                .firstName("Charlie")
                .lastName("Brown")
                .email("charlie@hr.com")
                .passwordHash("charlie")
                .role("EMPLOYEE")
                .department(sales)
                .salary(new BigDecimal("62000.00"))
                .build();
        charlie.setRawSsn("999-05-0005");
        employeeService.saveEmployee(charlie);

        // 3. Seed Leave Requests
        leaveRequestRepository.save(LeaveRequest.builder()
                .employee(alice)
                .leaveType("VACATION")
                .startDate(LocalDate.now().plusDays(5))
                .endDate(LocalDate.now().plusDays(12))
                .status("PENDING")
                .build());

        leaveRequestRepository.save(LeaveRequest.builder()
                .employee(bob)
                .leaveType("SICK")
                .startDate(LocalDate.now().minusDays(2))
                .endDate(LocalDate.now().plusDays(1))
                .status("APPROVED")
                .approver(manager)
                .build());
    }
}
