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

    // VULNERABILITY A08: Deserializes untrusted employee import uploads without a class allowlist.
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
