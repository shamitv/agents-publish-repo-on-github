package com.warehouse.controller;

import com.warehouse.model.Employee;
import com.warehouse.service.EmployeeLdapService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    @Autowired
    private EmployeeLdapService employeeLdapService;

    @GetMapping("/search")
    public ResponseEntity<List<Employee>> search(@RequestParam(value = "q", defaultValue = "") String searchTerm) {
        List<Employee> results = employeeLdapService.searchEmployees(searchTerm);
        return ResponseEntity.ok(results);
    }
}
