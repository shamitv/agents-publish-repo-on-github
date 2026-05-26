package com.hr.cache;

import com.hr.model.Employee;
import org.springframework.stereotype.Component;

import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

@Component
public class EmployeeProfileCache {
    private final ConcurrentMap<Long, Employee> profiles = new ConcurrentHashMap<>();

    public Optional<Employee> get(Long employeeId) {
        return Optional.ofNullable(profiles.get(employeeId));
    }

    public void put(Employee employee) {
        if (employee.getId() != null) {
            profiles.put(employee.getId(), employee);
        }
    }

    public void evict(Long employeeId) {
        profiles.remove(employeeId);
    }
}
