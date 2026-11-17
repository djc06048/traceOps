package com.prowin.versions;

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

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class VersionsIntegrationTest {

    private static final Path FIXTURE_A = Path.of("src/test/resources/fixtures/sample-a.pptx");
    private static final Path FIXTURE_B = Path.of("src/test/resources/fixtures/sample-b.pptx");
    private static final String BASE = "/api/projects/P-001/versions";

    @TempDir
    static Path tempDir;

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("prowin.db.path", () -> tempDir.resolve("test.db").toString());
        registry.add("prowin.upload.path", () -> tempDir.resolve("uploads").toString());
    }

    @org.springframework.beans.factory.annotation.Autowired
    private TestRestTemplate rest;

    private HttpEntity<MultiValueMap<String, Object>> multipartUpload(Path file, String tocRowId) throws Exception {
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        ByteArrayResource resource = new ByteArrayResource(Files.readAllBytes(file)) {
            @Override
            public String getFilename() {
                return file.getFileName().toString();
            }
        };
        body.add("file", resource);
        body.add("message", "통합테스트 업로드");
        body.add("who", "integration-test");
        body.add("tocRowId", tocRowId);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);
        return new HttpEntity<>(body, headers);
    }

    @Test
    void rejectsNonPptxUpload() throws Exception {
        Path notPptx = tempDir.resolve("not-a-pptx.txt");
        Files.writeString(notPptx, "hello");

        ResponseEntity<Map> resp = rest.postForEntity(BASE + "/commits", multipartUpload(notPptx, "T-02"), Map.class);

        assertThat(resp.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
        assertThat(resp.getBody()).containsKey("error");
    }

    @Test
    void uploadMergeAndDownloadRoundTrip() throws Exception {
        ResponseEntity<ProposalCommit> up1 = rest.postForEntity(BASE + "/commits", multipartUpload(FIXTURE_A, "T-02"), ProposalCommit.class);
        assertThat(up1.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(up1.getBody().slideCount()).isEqualTo(2);

        ResponseEntity<ProposalCommit> up2 = rest.postForEntity(BASE + "/commits", multipartUpload(FIXTURE_B, "T-03"), ProposalCommit.class);
        assertThat(up2.getStatusCode()).isEqualTo(HttpStatus.OK);

        HttpHeaders jsonHeaders = new HttpHeaders();
        jsonHeaders.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> snapshotReq = new HttpEntity<>(
                Map.of("branch", "main", "message", "통합테스트 합본", "who", "integration-test"), jsonHeaders);
        ResponseEntity<ProposalCommit> snap = rest.postForEntity(BASE + "/snapshot", snapshotReq, ProposalCommit.class);

        assertThat(snap.getStatusCode()).isEqualTo(HttpStatus.OK);
        ProposalCommit snapshot = snap.getBody();
        assertThat(snapshot.slideCount()).isEqualTo(4);
        assertThat(snapshot.skippedFiles()).isEmpty();
        assertThat(snapshot.fileName()).startsWith("제안서_합본_");

        ResponseEntity<byte[]> download = rest.getForEntity(
                BASE + "/commits/" + snapshot.commitHash() + "/download", byte[].class);
        assertThat(download.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(download.getBody()).isNotEmpty();
        // 한글 파일명이어도 Content-Disposition 헤더가 깨지거나 사라지면 안 된다(Tomcat은 비ASCII 헤더를 통째로 버린다)
        assertThat(download.getHeaders().getContentDisposition().getFilename()).isEqualTo(snapshot.fileName());

        ResponseEntity<byte[]> preview = rest.getForEntity(
                BASE + "/commits/" + up1.getBody().commitHash() + "/slides/0?width=400", byte[].class);
        assertThat(preview.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(preview.getHeaders().getContentType()).isEqualTo(MediaType.IMAGE_PNG);
    }
}
