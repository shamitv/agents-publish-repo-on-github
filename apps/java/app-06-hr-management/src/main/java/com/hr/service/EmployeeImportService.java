package com.hr.service;

import com.hr.model.Employee;
import com.hr.repository.EmployeeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.util.List;

@Service
public class EmployeeImportService {

    @Autowired
    private EmployeeRepository employeeRepository;

    // VULNERABILITY: Insecure Deserialization (A08)
    // Deserialises arbitrary Java objects from an uploaded stream using ObjectInputStream.readObject()
    // without any type checks or filter list, potentially leading to remote code execution.
    @SuppressWarnings("unchecked")
    public List<Employee> importEmployees(InputStream stream) throws Exception {
        ObjectInputStream ois = new ObjectInputStream(stream);
        try {
            List<Employee> employees = (List<Employee>) ois.readObject();
            return employeeRepository.saveAll(employees);
        } finally {
            ois.close();
        }
    }
}
