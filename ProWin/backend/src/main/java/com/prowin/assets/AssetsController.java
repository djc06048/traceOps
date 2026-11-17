package com.prowin.assets;

import com.prowin.common.ApiException;
import com.prowin.common.FileNames;
import com.prowin.versions.PptxExtractor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

/**
 * 자산 라이브러리 2-2(슬라이드 단위 적재)·2-3 P0(메타·키워드 검색)만 구현한다.
 * 2-3 P1(의미 검색)·P2(재정렬)는 임베딩 모델 반입 등 2-8의 결정사항이 확정된 뒤 추가한다.
 */
@RestController
@RequestMapping("/api/assets")
public class AssetsController {

    private final AssetsRepository repo;
    private final PptxExtractor extractor;
    private final String uploadBasePath;

    public AssetsController(AssetsRepository repo, PptxExtractor extractor,
                             @Value("${prowin.upload.path}") String uploadBasePath) {
        this.repo = repo;
        this.extractor = extractor;
        this.uploadBasePath = uploadBasePath;
    }

    @GetMapping
    public List<AssetSlide> all() {
        return repo.findAll();
    }

    @GetMapping("/search")
    public List<AssetSlide> search(@RequestParam(required = false) String q,
                                    @RequestParam(required = false) String clientSector,
                                    @RequestParam(required = false) String year,
                                    @RequestParam(required = false) Boolean won,
                                    @RequestParam(defaultValue = "20") int limit) {
        int safeLimit = Math.min(Math.max(limit, 1), 100);
        return repo.search(new AssetsRepository.SearchFilter(q, clientSector, year, won), safeLimit);
    }

    /** 과거 제안서 PPTX를 슬라이드 단위로 분해해 메타데이터와 함께 적재한다. */
    @PostMapping(value = "/ingest", consumes = "multipart/form-data")
    public List<AssetSlide> ingest(@RequestParam("file") MultipartFile file,
                                    @RequestParam String proposalName,
                                    @RequestParam(required = false) String clientSector,
                                    @RequestParam(required = false) String year,
                                    @RequestParam(defaultValue = "false") boolean won,
                                    @RequestParam(required = false) String author,
                                    @RequestParam(required = false) String confidentiality,
                                    @RequestParam(required = false) String tags) {
        if (file == null || file.isEmpty()) throw new ApiException("자산으로 등록할 PPTX 파일을 선택해 주세요");
        if (proposalName == null || proposalName.isBlank()) throw new ApiException("사업명을 입력해 주세요");
        String originalName = FileNames.sanitize(file.getOriginalFilename(), "upload.pptx");
        if (!originalName.toLowerCase().endsWith(".pptx")) {
            throw new ApiException("pptx 파일만 등록할 수 있습니다: " + originalName);
        }

        Path dest;
        try {
            Path dir = Path.of(uploadBasePath, "_assets");
            Files.createDirectories(dir);
            dest = dir.resolve(UUID.randomUUID() + ".pptx");
            file.transferTo(dest);
        } catch (IOException e) {
            throw new ApiException("자산 파일 저장에 실패했습니다: " + e.getMessage());
        }

        List<PptxExtractor.SlideContent> slides = extractor.extract(dest);
        if (slides.isEmpty()) throw new ApiException("슬라이드 내용을 읽지 못했습니다. pptx 파일이 올바른지 확인해 주세요");

        List<AssetsRepository.NewSlide> newSlides = new ArrayList<>();
        for (int i = 0; i < slides.size(); i++) {
            PptxExtractor.SlideContent slide = slides.get(i);
            newSlides.add(new AssetsRepository.NewSlide(slide.title(), String.join("\n", slide.bullets()), i + 1));
        }
        List<String> tagList = tags == null || tags.isBlank() ? List.of()
                : Arrays.stream(tags.split(",")).map(String::strip).filter(t -> !t.isBlank()).toList();

        return repo.ingest(proposalName, clientSector, year, won, author, confidentiality, tagList, dest.toString(), newSlides);
    }
}
