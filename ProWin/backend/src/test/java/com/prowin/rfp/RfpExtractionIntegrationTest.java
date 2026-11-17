package com.prowin.rfp;

import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class RfpExtractionIntegrationTest {

    private static final String BASE = "/api/projects/P-001/rfp";

    @TempDir
    static Path tempDir;

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("prowin.db.path", () -> tempDir.resolve("test.db").toString());
        registry.add("prowin.upload.path", () -> tempDir.resolve("uploads").toString());
    }

    @org.springframework.beans.factory.annotation.Autowired
    private TestRestTemplate rest;

    @Test
    void extractThenConfirmAddsToRequirements() throws Exception {
        Path rfp = tempDir.resolve("rfp.docx");
        try (XWPFDocument doc = new XWPFDocument()) {
            XWPFTable table = doc.createTable(2, 3);
            table.getRow(0).getCell(0).setText("고유번호");
            table.getRow(0).getCell(1).setText("요구사항명");
            table.getRow(0).getCell(2).setText("설명");
            table.getRow(1).getCell(0).setText("SFR-100");
            table.getRow(1).getCell(1).setText("무중단 이관");
            table.getRow(1).getCell(2).setText("서비스 중단 없이 이관한다");
            try (OutputStream out = Files.newOutputStream(rfp)) {
                doc.write(out);
            }
        }

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        ByteArrayResource resource = new ByteArrayResource(Files.readAllBytes(rfp)) {
            @Override
            public String getFilename() {
                return "rfp.docx";
            }
        };
        body.add("file", resource);
        body.add("receivedDate", "2026-11-16");
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        ResponseEntity<RfpResponse> extractResp = rest.postForEntity(BASE + "/extract", new HttpEntity<>(body, headers), RfpResponse.class);
        assertThat(extractResp.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(extractResp.getBody().document().fileName()).isEqualTo("rfp.docx");

        ResponseEntity<RequirementCandidate[]> listResp = rest.getForEntity(BASE + "/candidates", RequirementCandidate[].class);
        assertThat(listResp.getBody()).hasSize(1);
        RequirementCandidate candidate = listResp.getBody()[0];
        assertThat(candidate.status()).isEqualTo("candidate");
        assertThat(candidate.code()).isEqualTo("SFR-100");

        HttpHeaders jsonHeaders = new HttpHeaders();
        jsonHeaders.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> confirmReq = new HttpEntity<>(Map.of("who", "tester"), jsonHeaders);
        ResponseEntity<RfpRequirement> confirmResp = rest.postForEntity(
                BASE + "/candidates/" + candidate.id() + "/confirm", confirmReq, RfpRequirement.class);
        assertThat(confirmResp.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(confirmResp.getBody().code()).isEqualTo("SFR-100");
        assertThat(confirmResp.getBody().title()).isEqualTo("무중단 이관");

        ResponseEntity<RfpResponse> after = rest.getForEntity(BASE, RfpResponse.class);
        assertThat(after.getBody().requirements()).extracting(RfpRequirement::code).contains("SFR-100");

        ResponseEntity<RequirementCandidate[]> listAfterConfirm = rest.getForEntity(BASE + "/candidates", RequirementCandidate[].class);
        assertThat(List.of(listAfterConfirm.getBody())).extracting(RequirementCandidate::status).containsOnly("confirmed");
    }
}
