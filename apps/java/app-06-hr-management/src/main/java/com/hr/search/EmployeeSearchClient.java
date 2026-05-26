package com.hr.search;

import com.hr.model.Employee;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
public class EmployeeSearchClient {
    private final RestTemplate searchRestTemplate;
    private final String elasticsearchUrl;
    private final boolean enabled;

    public EmployeeSearchClient(
            RestTemplate searchRestTemplate,
            @Value("${app.elasticsearch.url:http://localhost:9200}") String elasticsearchUrl,
            @Value("${app.elasticsearch.enabled:false}") boolean enabled) {
        this.searchRestTemplate = searchRestTemplate;
        this.elasticsearchUrl = elasticsearchUrl;
        this.enabled = enabled;
    }

    public void index(Employee employee) {
        if (!enabled || employee.getId() == null) {
            return;
        }

        Map<String, Object> document = Map.of(
                "id", employee.getId(),
                "name", employee.getFirstName() + " " + employee.getLastName(),
                "email", employee.getEmail(),
                "role", employee.getRole(),
                "department", employee.getDepartment() == null ? "None" : employee.getDepartment().getName()
        );

        try {
            searchRestTemplate.put(elasticsearchUrl + "/hr-employees/_doc/" + employee.getId(), document);
        } catch (RestClientException ignored) {
            // Search indexing is best effort so HR writes are not blocked by search outages.
        }
    }
}
