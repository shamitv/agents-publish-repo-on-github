package com.warehouse.service;

import com.warehouse.model.Employee;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.ldap.core.AttributesMapper;
import org.springframework.ldap.core.LdapTemplate;
import org.springframework.stereotype.Service;
import javax.naming.NamingException;
import javax.naming.directory.Attributes;
import java.util.List;

@Service
public class EmployeeLdapService {

    @Autowired
    private LdapTemplate ldapTemplate;

    public List<Employee> searchEmployees(String searchTerm) {
        String filter = "(&(objectClass=inetOrgPerson)(|(cn=*" + searchTerm + "*)(uid=*" + searchTerm + "*)))";
        return ldapTemplate.search("ou=employees", filter, new EmployeeAttributesMapper());
    }

    private static class EmployeeAttributesMapper implements AttributesMapper<Employee> {
        @Override
        public Employee mapFromAttributes(Attributes attrs) throws NamingException {
            return Employee.builder()
                    .uid(attrs.get("uid") != null ? attrs.get("uid").get().toString() : "")
                    .cn(attrs.get("cn") != null ? attrs.get("cn").get().toString() : "")
                    .sn(attrs.get("sn") != null ? attrs.get("sn").get().toString() : "")
                    .mail(attrs.get("mail") != null ? attrs.get("mail").get().toString() : "")
                    .title(attrs.get("title") != null ? attrs.get("title").get().toString() : "")
                    .departmentNumber(attrs.get("departmentNumber") != null ? attrs.get("departmentNumber").get().toString() : "")
                    .build();
        }
    }
}
