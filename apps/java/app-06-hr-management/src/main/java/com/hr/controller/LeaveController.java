package com.hr.controller;

import com.hr.model.Employee;
import com.hr.model.LeaveRequest;
import com.hr.service.EmployeeService;
import com.hr.service.LeaveService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/leave")
public class LeaveController {

    @Autowired
    private LeaveService leaveService;

    @Autowired
    private EmployeeService employeeService;

    @GetMapping("/requests")
    public ResponseEntity<List<LeaveRequest>> getMyLeaveRequests(@AuthenticationPrincipal UserDetails userDetails) {
        Employee current = employeeService.getEmployeeByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("Current user not found"));
        
        // HR_ADMIN or MANAGER can see all, standard employee sees only their own
        if (current.getRole().equals("HR_ADMIN")) {
            return ResponseEntity.ok(leaveService.getAllLeaveRequests());
        } else if (current.getRole().equals("MANAGER")) {
            // Managers see all requests to approve
            return ResponseEntity.ok(leaveService.getAllLeaveRequests());
        } else {
            return ResponseEntity.ok(leaveService.getLeaveRequestsByEmployee(current.getId()));
        }
    }

    @PostMapping("/requests")
    public ResponseEntity<LeaveRequest> submitLeaveRequest(@AuthenticationPrincipal UserDetails userDetails, @RequestBody Map<String, Object> payload) {
        Employee current = employeeService.getEmployeeByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("Current user not found"));

        LeaveRequest req = LeaveRequest.builder()
                .employee(current)
                .leaveType((String) payload.get("leaveType"))
                .startDate(LocalDate.parse((String) payload.get("startDate")))
                .endDate(LocalDate.parse((String) payload.get("endDate")))
                .status("PENDING")
                .build();

        LeaveRequest saved = leaveService.saveLeaveRequest(req);
        return ResponseEntity.ok(saved);
    }

    @PutMapping("/requests/{id}/approve")
    @PreAuthorize("hasAnyRole('MANAGER', 'HR_ADMIN')")
    public ResponseEntity<LeaveRequest> approveLeaveRequest(@PathVariable Long id, @AuthenticationPrincipal UserDetails userDetails, @RequestBody Map<String, String> payload) {
        Employee current = employeeService.getEmployeeByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("Current user not found"));

        return leaveService.getLeaveRequestById(id).map(req -> {
            req.setStatus(payload.getOrDefault("status", "APPROVED"));
            req.setApprover(current);
            LeaveRequest saved = leaveService.saveLeaveRequest(req);
            return ResponseEntity.ok(saved);
        }).orElse(ResponseEntity.notFound().build());
    }
}
