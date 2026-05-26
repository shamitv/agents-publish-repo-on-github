package com.hr.controller;
import com.hr.dto.EmployeeDTO;
import com.hr.model.Employee;
import com.hr.repository.DepartmentRepository;
import com.hr.service.EmployeeImportService;
import com.hr.service.EmployeeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.HashMap;
@RestController
@RequestMapping("/api/employees")
public class EmployeeController {
    @Autowired
    private EmployeeService employeeService;
    @Autowired
    private EmployeeImportService employeeImportService;
    @Autowired
    private DepartmentRepository departmentRepository;
    @GetMapping
    public ResponseEntity<List<EmployeeDTO>> listEmployees(@RequestParam(value = "q", required = false) String query) {
        List<Employee> list = employeeService.searchEmployees(query);
        List<EmployeeDTO> dtos = list.stream()
                .map(EmployeeDTO::fromEntity)
                .collect(Collectors.toList());
        return ResponseEntity.ok(dtos);
    }
    @GetMapping("/{id}")
    public ResponseEntity<EmployeeDTO> getEmployee(@PathVariable Long id) {
        return employeeService.getEmployeeById(id)
                .map(emp -> ResponseEntity.ok(EmployeeDTO.fromEntity(emp)))
                .orElse(ResponseEntity.notFound().build());
    }
    @PostMapping
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<EmployeeDTO> createEmployee(@RequestBody Map<String, Object> payload) {
        Employee emp = Employee.builder()
                .firstName((String) payload.get("firstName"))
                .lastName((String) payload.get("lastName"))
                .email((String) payload.get("email"))
                .passwordHash((String) payload.get("password"))
                .role((String) payload.get("role"))
                .salary(new BigDecimal(payload.get("salary").toString()))
                .build();
        emp.setRawSsn((String) payload.get("ssn"));
        if (payload.containsKey("departmentId")) {
            departmentRepository.findById(Long.valueOf(payload.get("departmentId").toString()))
                    .ifPresent(emp::setDepartment);
        }
        Employee saved = employeeService.saveEmployee(emp);
        return ResponseEntity.ok(EmployeeDTO.fromEntity(saved));
    }
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<EmployeeDTO> updateEmployee(@PathVariable Long id, @RequestBody Map<String, Object> payload) {
        return employeeService.getEmployeeById(id).map(emp -> {
            emp.setFirstName((String) payload.get("firstName"));
            emp.setLastName((String) payload.get("lastName"));
            emp.setEmail((String) payload.get("email"));
            emp.setRole((String) payload.get("role"));
            emp.setSalary(new BigDecimal(payload.get("salary").toString()));
            if (payload.containsKey("ssn") && payload.get("ssn") != null) {
                emp.setRawSsn((String) payload.get("ssn"));
            }
            if (payload.containsKey("departmentId")) {
                departmentRepository.findById(Long.valueOf(payload.get("departmentId").toString()))
                        .ifPresent(emp::setDepartment);
            }
            Employee saved = employeeService.saveEmployee(emp);
            return ResponseEntity.ok(EmployeeDTO.fromEntity(saved));
        }).orElse(ResponseEntity.notFound().build());
    }
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<Void> deleteEmployee(@PathVariable Long id) {
        employeeService.deleteEmployee(id);
        return ResponseEntity.noContent().build();
    }
    // passwordHash field. The missing @PreAuthorize means any authenticated employee can
    // call this for any employee ID. Individually a minor IDOR, but the exposed hash
    // enables the offline-crack step that unlocks higher-privilege sessions.
    @GetMapping("/{id}/audit")
    public ResponseEntity<?> getEmployeeAudit(@PathVariable Long id) {
        return employeeService.getEmployeeById(id).map(emp -> {
            Map<String, Object> auditData = new HashMap<>();
            auditData.put("id", emp.getId());
            auditData.put("firstName", emp.getFirstName());
            auditData.put("lastName", emp.getLastName());
            auditData.put("email", emp.getEmail());
            auditData.put("role", emp.getRole());
            auditData.put("passwordHash", emp.getPasswordHash());
            return ResponseEntity.ok(auditData);
        }).orElse(ResponseEntity.notFound().build());
    }
    // Import employees endpoint
    @PostMapping("/import")
    @PreAuthorize("hasRole('HR_ADMIN')")
    public ResponseEntity<List<EmployeeDTO>> importEmployees(@RequestParam("file") MultipartFile file) {
        try {
            List<Employee> imported = employeeImportService.importEmployees(file.getInputStream());
            List<EmployeeDTO> dtos = imported.stream()
                    .map(EmployeeDTO::fromEntity)
                    .collect(Collectors.toList());
            return ResponseEntity.ok(dtos);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
}