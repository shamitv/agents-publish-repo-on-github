 A02: Storing highly sensitive legal documents in cleartext
    @Lob
    @Column(name = "file_content_plaintext", nullable = false, columnDefinition = "TEXT")
    private String fileContentPlaintext;
    @Column(nullable = false, length = 50)
    private String uploadedBy;
    @Builder.Default
    private LocalDateTime createdAt = LocalDateTime.now();
}