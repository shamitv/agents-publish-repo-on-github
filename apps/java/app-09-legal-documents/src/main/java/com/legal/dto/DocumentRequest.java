package com.legal.dto;

import lombok.Data;

@Data
public class DocumentRequest {
    private Long caseId;
    private String title;
    private String filename;
    private String fileContentPlaintext;
}
