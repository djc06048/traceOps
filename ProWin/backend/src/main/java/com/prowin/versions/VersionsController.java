package com.prowin.versions;

import com.prowin.common.ApiException;
import com.prowin.review.ReviewNode;
import com.prowin.review.ReviewRepository;
import com.prowin.toc.TocRepository;
import com.prowin.toc.TocRow;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;

@RestController
@RequestMapping("/api/projects/{projectId}/versions")
public class VersionsController {

    private static final int BULLET_LIMIT = 20;
    private static final int PREVIEW_WIDTH = 960;

    public record SnapshotRequest(String branch, String message, String who) {
    }

    private final VersionsRepository repo;
    private final TocRepository tocRepo;
    private final ReviewRepository reviewRepo;
    private final PptxExtractor extractor;
    private final PptxRenderer renderer;
    private final PptxMerger merger;
    private final String uploadBasePath;

    public VersionsController(VersionsRepository repo, TocRepository tocRepo, ReviewRepository reviewRepo,
                               PptxExtractor extractor, PptxRenderer renderer, PptxMerger merger,
                               @Value("${prowin.upload.path}") String uploadBasePath) {
        this.repo = repo;
        this.tocRepo = tocRepo;
        this.reviewRepo = reviewRepo;
        this.extractor = extractor;
        this.renderer = renderer;
        this.merger = merger;
        this.uploadBasePath = uploadBasePath;
    }

    @GetMapping
    public VersionsResponse get(@PathVariable String projectId) {
        return repo.findAll(projectId);
    }

    @PostMapping(value = "/commits", consumes = "multipart/form-data")
    public ProposalCommit createCommit(@PathVariable String projectId,
                                        @RequestParam("file") MultipartFile file,
                                        @RequestParam String message,
                                        @RequestParam String who,
                                        @RequestParam String tocRowId,
                                        @RequestParam(required = false) String branch) {
        if (file == null || file.isEmpty()) throw new ApiException("업로드할 파일을 선택해 주세요");
        TocRow tocRow = tocRepo.findAll(projectId).stream().filter(r -> r.id().equals(tocRowId)).findFirst()
                .orElseThrow(() -> new ApiException("목차를 찾을 수 없습니다: " + tocRowId));
        if (tocRow.level() != 2) throw new ApiException("세부 목차에만 업로드할 수 있습니다: " + tocRowId);
        String originalName = file.getOriginalFilename() == null ? "upload" : file.getOriginalFilename();
        Path dest;
        try {
            Path dir = Path.of(uploadBasePath, projectId);
            Files.createDirectories(dir);
            String storedName = System.currentTimeMillis() + "_" + originalName;
            dest = dir.resolve(storedName);
            file.transferTo(dest);
        } catch (IOException e) {
            throw new ApiException("파일 업로드에 실패했습니다: " + e.getMessage());
        }
        List<PptxExtractor.SlideContent> slides = extractor.extract(dest);
        ProposalCommit commit = repo.createCommit(projectId, branch, message, who, originalName, dest.toString(), tocRowId, slides.size());
        applyExtractedContent(projectId, tocRowId, slides);
        return commit;
    }

    @GetMapping(value = "/commits/{commitHash}/slides/{index}", produces = "image/png")
    public ResponseEntity<byte[]> slideImage(@PathVariable String projectId, @PathVariable String commitHash, @PathVariable int index) {
        VersionsRepository.StoredFile file = repo.findFile(projectId, commitHash);
        if (file == null || file.filePath() == null) throw new ApiException("미리보기할 파일이 없습니다: " + commitHash);
        byte[] png = renderer.renderSlidePng(Path.of(file.filePath()), index, PREVIEW_WIDTH);
        return ResponseEntity.ok().contentType(org.springframework.http.MediaType.IMAGE_PNG).body(png);
    }

    @GetMapping("/commits/{commitHash}/download")
    public ResponseEntity<byte[]> download(@PathVariable String projectId, @PathVariable String commitHash) throws IOException {
        VersionsRepository.StoredFile file = repo.findFile(projectId, commitHash);
        if (file == null || file.filePath() == null) throw new ApiException("다운로드할 파일이 없습니다: " + commitHash);
        byte[] bytes = Files.readAllBytes(Path.of(file.filePath()));
        String downloadName = file.fileName() == null ? commitHash + ".pptx" : file.fileName();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, ContentDisposition.attachment().filename(downloadName).build().toString())
                .contentType(org.springframework.http.MediaType.APPLICATION_OCTET_STREAM)
                .body(bytes);
    }

    /** PPTX에서 뽑은 슬라이드 제목/핵심내용을 해당 목차의 검토 노드·예상 장수에 즉시 반영한다. 추출 결과가 없으면 조용히 건너뛴다. */
    private void applyExtractedContent(String projectId, String tocRowId, List<PptxExtractor.SlideContent> slides) {
        if (slides.isEmpty()) return;
        ReviewNode existing = reviewRepo.findAll(projectId).stream().filter(n -> n.tocRowId().equals(tocRowId)).findFirst().orElse(null);
        String titleDetail = slides.get(0).title();
        List<String> bullets = slides.stream().flatMap(s -> s.bullets().stream()).limit(BULLET_LIMIT).toList();
        reviewRepo.upsertNode(projectId, tocRowId,
                existing == null ? null : existing.memo(),
                titleDetail == null ? (existing == null ? null : existing.titleDetail()) : titleDetail,
                existing == null ? List.of() : existing.flowSteps(),
                bullets.isEmpty() ? (existing == null ? List.of() : existing.bullets()) : bullets,
                "system");
        tocRepo.updatePages(projectId, tocRowId, slides.size() + "p");
    }

    @PostMapping("/snapshot")
    public ProposalCommit createSnapshot(@PathVariable String projectId, @RequestBody SnapshotRequest req) {
        List<TocRow> level2 = tocRepo.findAll(projectId).stream()
                .filter(r -> r.level() == 2)
                .sorted(Comparator.comparingInt(TocRow::orderIndex))
                .toList();
        List<ProposalCommit> commits = repo.findAll(projectId).commits();
        List<Path> sourceFiles = new ArrayList<>();
        for (TocRow row : level2) {
            commits.stream()
                    .filter(c -> row.id().equals(c.tocRowId()) && c.fileName() != null)
                    .findFirst()
                    .map(c -> repo.findFile(projectId, c.commitHash()))
                    .filter(Objects::nonNull)
                    .map(VersionsRepository.StoredFile::filePath)
                    .filter(Objects::nonNull)
                    .ifPresent(fp -> sourceFiles.add(Path.of(fp)));
        }
        if (sourceFiles.isEmpty()) throw new ApiException("병합할 업로드가 없습니다. 먼저 섹션별로 PPT를 업로드해 주세요");
        Path dir = Path.of(uploadBasePath, projectId);
        try {
            Files.createDirectories(dir);
        } catch (IOException e) {
            throw new ApiException("합본 저장 폴더를 만들지 못했습니다: " + e.getMessage());
        }
        Path outFile = dir.resolve(System.currentTimeMillis() + "_합본.pptx");
        PptxMerger.MergeResult result = merger.merge(sourceFiles, outFile);
        return repo.createSnapshot(projectId, req.branch(), req.message(), req.who(),
                outFile.getFileName().toString(), outFile.toString(), result.slideCount());
    }
}
