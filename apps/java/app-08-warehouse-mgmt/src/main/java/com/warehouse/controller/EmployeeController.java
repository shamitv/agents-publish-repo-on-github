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
import java.util.Map;

@RestController
@RequestMapping("/api/employees")
public class EmployeeController {

    @Autowired
    private EmployeeLdapService employeeLdapService;

    // CHAIN LINK 1 (chain-01): LDAP injection is in EmployeeLdapService.searchEmployees()
    // CHAIN LINK 2 (chain-01): LDAP exception details, including internal DN paths and
    // directory base, are surfaced verbatim in the HTTP response body. An attacker who
    // triggers an error via a malformed LDAP filter learns the full directory structure.
    @GetMapping("/search")
    public ResponseEntity<?> search(@RequestParam(value = "q", defaultValue = "") String searchTerm) {
        try {
            List<Employee> results = employeeLdapService.searchEmployees(searchTerm);
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            // Verbose error: exposes LDAP exception message including internal DN paths
            return ResponseEntity.status(500)
                    .body(Map.of("error", e.getMessage(), "cause", String.valueOf(e.getCause())));
        }
    }
}
