package com.prowin.assets;

import org.apache.poi.xslf.usermodel.XMLSlideShow;
import org.apache.poi.xslf.usermodel.XSLFSlide;
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

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class AssetsIntegrationTest {

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
    void ingestsSlidesThenFindsThemByKeywordAndMetaFilter() throws Exception {
        Path pptx = tempDir.resolve("past-proposal.pptx");
        try (XMLSlideShow ppt = new XMLSlideShow()) {
            XSLFSlide s1 = ppt.createSlide();
            s1.createTextBox().setText("무중단 이관 아키텍처");
            XSLFSlide s2 = ppt.createSlide();
            s2.createTextBox().setText("품질관리 방안");
            try (OutputStream out = Files.newOutputStream(pptx)) {
                ppt.write(out);
            }
        }

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        ByteArrayResource resource = new ByteArrayResource(Files.readAllBytes(pptx)) {
            @Override
            public String getFilename() {
                return "past-proposal.pptx";
            }
        };
        body.add("file", resource);
        body.add("proposalName", "OO손해보험 차세대");
        body.add("clientSector", "보험");
        body.add("year", "2026");
        body.add("won", "true");
        body.add("tags", "MSA"); // "이관"을 태그에 넣지 않아 키워드 검색이 슬라이드 본문만으로 판가름나게 한다
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        ResponseEntity<AssetSlide[]> ingestResp = rest.postForEntity("/api/assets/ingest", new HttpEntity<>(body, headers), AssetSlide[].class);
        assertThat(ingestResp.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(ingestResp.getBody()).hasSize(2);
        assertThat(ingestResp.getBody()[0].tags()).containsExactly("MSA");

        ResponseEntity<AssetSlide[]> byKeyword = rest.getForEntity("/api/assets/search?q=이관", AssetSlide[].class);
        assertThat(List.of(byKeyword.getBody())).extracting(AssetSlide::title).containsExactly("무중단 이관 아키텍처");

        ResponseEntity<AssetSlide[]> byMeta = rest.getForEntity("/api/assets/search?clientSector=보험&year=2026&won=true", AssetSlide[].class);
        assertThat(byMeta.getBody()).hasSize(2);

        ResponseEntity<AssetSlide[]> noMatch = rest.getForEntity("/api/assets/search?q=존재하지않는단어", AssetSlide[].class);
        assertThat(noMatch.getBody()).isEmpty();
    }
}
