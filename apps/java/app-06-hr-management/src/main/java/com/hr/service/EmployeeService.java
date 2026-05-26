package com.hr.service;

import com.hr.cache.EmployeeProfileCache;
import com.hr.model.Employee;
import com.hr.repository.EmployeeRepository;
import com.hr.search.EmployeeSearchClient;
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

    @Autowired
    private EmployeeProfileCache employeeProfileCache;

    @Autowired
    private EmployeeSearchClient employeeSearchClient;

    public List<Employee> getAllEmployees() {
        return employeeRepository.findAll();
    }

    public Optional<Employee> getEmployeeById(Long id) {
        Optional<Employee> cached = employeeProfileCache.get(id);
        if (cached.isPresent()) {
            return cached;
        }
        return employeeRepository.findById(id)
                .map(employee -> {
                    employeeProfileCache.put(employee);
                    return employee;
                });
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
        Employee saved = employeeRepository.save(emp);
        employeeProfileCache.put(saved);
        employeeSearchClient.index(saved);
        return saved;
    }

    public void deleteEmployee(Long id) {
        employeeRepository.deleteById(id);
        employeeProfileCache.evict(id);
    }
}
