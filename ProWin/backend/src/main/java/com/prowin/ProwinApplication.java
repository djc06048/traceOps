package com.prowin;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@SpringBootApplication
public class ProwinApplication {
    public static void main(String[] args) throws IOException {
        String dbPath = System.getenv().getOrDefault("PROWIN_DB_PATH", "./data/prowin.db");
        String uploadPath = System.getenv().getOrDefault("PROWIN_UPLOAD_PATH", "./data/uploads");
        Files.createDirectories(Path.of(dbPath).toAbsolutePath().getParent());
        Files.createDirectories(Path.of(uploadPath));
        SpringApplication.run(ProwinApplication.class, args);
    }
}
