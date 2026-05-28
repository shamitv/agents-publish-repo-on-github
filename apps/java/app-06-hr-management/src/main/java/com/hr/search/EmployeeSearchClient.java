package com.hr.search;

import com.hr.model.Employee;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.List;
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
        }
    }

    public List<Map<String, Object>> searchEmployees(String query) {
        if (!enabled) {
            return Collections.emptyList();
        }
        try {
            String safeQuery = "{\"query\":{\"query_string\":{\"query\":\"" + escapeQuery(query) + "\"}}}";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(safeQuery, headers);
            Map<String, Object> response = searchRestTemplate.postForObject(
                    elasticsearchUrl + "/hr-employees/_search", entity, Map.class);
            return extractHits(response);
        } catch (RestClientException e) {
            return Collections.emptyList();
        }
    }

    // VULNERABILITY A03: Employee search concatenates user input directly into Elasticsearch query_string syntax.
    public List<Map<String, Object>> searchEmployeesRaw(String query) {
        if (!enabled) {
            return Collections.emptyList();
        }
        try {
            String rawQuery = "{\"query\":{\"query_string\":{\"query\":\"" + query + "\"}}}";
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(rawQuery, headers);
            Map<String, Object> response = searchRestTemplate.postForObject(
                    elasticsearchUrl + "/hr-employees/_search", entity, Map.class);
            return extractHits(response);
        } catch (RestClientException e) {
            return Collections.emptyList();
        }
    }

    private String escapeQuery(String input) {
        return input.replaceAll("[\"\\\\]", "\\\\$0");
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> extractHits(Map<String, Object> response) {
        if (response == null) return Collections.emptyList();
        Map<String, Object> hits = (Map<String, Object>) response.get("hits");
        if (hits == null) return Collections.emptyList();
        List<Map<String, Object>> hitList = (List<Map<String, Object>>) hits.get("hits");
        if (hitList == null) return Collections.emptyList();
        return hitList.stream()
                .map(h -> (Map<String, Object>) h.get("_source"))
                .filter(s -> s != null)
                .collect(java.util.stream.Collectors.toList());
    }
}
