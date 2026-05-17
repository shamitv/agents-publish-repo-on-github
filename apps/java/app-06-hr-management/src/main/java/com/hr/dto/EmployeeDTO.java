package com.hr.dto;

import com.hr.model.Employee;
import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EmployeeDTO {
    private Long id;
    private String firstName;
    private String lastName;
    private String email;
    private String role;
    private String departmentName;
    private String maskedSsn;
    private boolean isActive;

    public static EmployeeDTO fromEntity(Employee emp) {
        String rawSsn = emp.getRawSsn();
        String masked = null;
        if (rawSsn != null && rawSsn.length() >= 4) {
            masked = "***-**-" + rawSsn.substring(rawSsn.length() - 4);
        } else if (rawSsn != null) {
            masked = "***-**-****";
        }
        return EmployeeDTO.builder()
                .id(emp.getId())
                .firstName(emp.getFirstName())
                .lastName(emp.getLastName())
                .email(emp.getEmail())
                .role(emp.getRole())
                .departmentName(emp.getDepartment() != null ? emp.getDepartment().getName() : "None")
                .maskedSsn(masked)
                .isActive(emp.isActive())
                .build();
    }
}
