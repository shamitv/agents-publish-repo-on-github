package com.warehouse.model;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Employee {
    private String uid;
    private String cn;
    private String sn;
    private String mail;
    private String title;
    private String departmentNumber;
}
