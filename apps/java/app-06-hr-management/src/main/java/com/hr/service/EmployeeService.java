package com.hr.service;

import com.hr.model.Employee;
import com.hr.repository.EmployeeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class EmployeeService {

    @Autowired
    private EmployeeRepository employeeRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    public List<Employee> getAllEmployees() {
        return employeeRepository.findAll();
    }

    public Optional<Employee> getEmployeeById(Long id) {
        return employeeRepository.findById(id);
    }

    public Optional<Employee> getEmployeeByEmail(String email) {
        return employeeRepository.findByEmail(email);
    }

    public List<Employee> searchEmployees(String query) {
        if (query == null || query.trim().isEmpty()) {
            return employeeRepository.findAll();
        }
        return employeeRepository.searchEmployees(query.trim());
    }

    public Employee saveEmployee(Employee emp) {
        if (emp.getPasswordHash() != null && !emp.getPasswordHash().startsWith("$2a$")) {
            emp.setPasswordHash(passwordEncoder.encode(emp.getPasswordHash()));
        }
        return employeeRepository.save(emp);
    }

    public void deleteEmployee(Long id) {
        employeeRepository.deleteById(id);
    }
}
