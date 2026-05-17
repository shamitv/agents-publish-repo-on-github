package com.hr.controller;

import com.hr.model.Employee;
import com.hr.repository.DepartmentRepository;
import com.hr.service.EmployeeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class WebController {

    @Autowired
    private EmployeeService employeeService;

    @Autowired
    private DepartmentRepository departmentRepository;

    @GetMapping("/")
    public String login() {
        return "login";
    }

    @GetMapping("/dashboard")
    public String dashboard(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Employee current = employeeService.getEmployeeByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("Current user not found"));
        model.addAttribute("currentUser", current);
        return "dashboard";
    }

    @GetMapping("/employees")
    public String employees(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Employee current = employeeService.getEmployeeByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("Current user not found"));
        model.addAttribute("currentUser", current);
        model.addAttribute("departments", departmentRepository.findAll());
        return "employees";
    }

    @GetMapping("/payroll")
    public String payroll(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Employee current = employeeService.getEmployeeByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("Current user not found"));
        model.addAttribute("currentUser", current);
        return "payroll";
    }

    @GetMapping("/leave")
    public String leave(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Employee current = employeeService.getEmployeeByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("Current user not found"));
        model.addAttribute("currentUser", current);
        return "leave";
    }

    @GetMapping("/org-chart")
    public String orgChart(@AuthenticationPrincipal UserDetails userDetails, Model model) {
        Employee current = employeeService.getEmployeeByEmail(userDetails.getUsername())
                .orElseThrow(() -> new RuntimeException("Current user not found"));
        model.addAttribute("currentUser", current);
        return "org-chart";
    }
}
