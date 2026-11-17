package com.prowin.versions;

import com.prowin.common.ApiException;
import com.prowin.common.FileNames;
import com.prowin.toc.TocRepository;
import com.prowin.toc.TocRow;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

@RestController
@RequestMapping("/api/projects/{projectId}/versions")
public class VersionsController {

    private static final int PREVIEW_WIDTH = 960;
    private static final int MAX_PREVIEW_WIDTH = 1600;
    private static final int MIN_PREVIEW_WIDTH = 200;

    public record SnapshotRequest(String branch, String message, String who) {
    }

    private final VersionsRepository repo;
    private final TocRepository tocRepo;
    private final PptxExtractor extractor;
    private final PptxRenderer renderer;
    private final PptxMerger merger;
    private final String uploadBasePath;

    public VersionsController(VersionsRepository repo, TocRepository tocRepo,
                               PptxExtractor extractor, PptxRenderer renderer, PptxMerger merger,
                               @Value("${prowin.upload.path}") String uploadBasePath) {
        this.repo = repo;
        this.tocRepo = tocRepo;
        this.extractor = extractor;
        this.renderer = renderer;
        this.merger = merger;
        this.uploadBasePath = uploadBasePath;
    }

    @GetMapping
    public VersionsResponse get(@PathVariable String projectId) {
        return repo.findAll(projectId);
    }

    /** 커밋 생성 + 검토 노드 갱신 + 목차 장수 갱신을 한 트랜잭션으로 묶어, 중간에 실패해도 일부만 반영되지 않게 한다. */
    @Transactional
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
        String originalName = FileNames.sanitize(file.getOriginalFilename(), "upload.pptx");
        if (!originalName.toLowerCase().endsWith(".pptx")) {
            throw new ApiException("pptx 파일만 업로드할 수 있습니다: " + originalName);
        }
        Path dest;
        try {
            Path dir = Path.of(uploadBasePath, projectId);
            Files.createDirectories(dir);
            // 원본 파일명은 경로에 쓰지 않는다(경로 구분자·인코딩 문제 차단). 원본명은 DB에만 보관.
            String storedName = UUID.randomUUID() + ".pptx";
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
    public ResponseEntity<byte[]> slideImage(@PathVariable String projectId, @PathVariable String commitHash, @PathVariable int index,
                                              @RequestParam(required = false) Integer width) {
        VersionsRepository.StoredFile file = repo.findFile(projectId, commitHash);
        if (file == null || file.filePath() == null) throw new ApiException("미리보기할 파일이 없습니다: " + commitHash);
        int targetWidth = width == null ? PREVIEW_WIDTH : Math.max(MIN_PREVIEW_WIDTH, Math.min(width, MAX_PREVIEW_WIDTH));
        byte[] png = renderCached(projectId, commitHash, index, targetWidth, file.filePath());
        return ResponseEntity.ok().contentType(org.springframework.http.MediaType.IMAGE_PNG).body(png);
    }

    /** 커밋은 불변이므로 커밋해시+슬라이드번호+폭을 키로 디스크에 PNG를 캐시해 재요청 때 다시 그리지 않는다. */
    private byte[] renderCached(String projectId, String commitHash, int index, int width, String sourceFilePath) {
        Path cacheFile = Path.of(uploadBasePath, "_cache", projectId, commitHash + "-" + index + "-" + width + ".png");
        if (Files.exists(cacheFile)) {
            try {
                return Files.readAllBytes(cacheFile);
            } catch (IOException ignored) {
                // 캐시 읽기 실패 시 새로 렌더링
            }
        }
        byte[] png = renderer.renderSlidePng(Path.of(sourceFilePath), index, width);
        try {
            Files.createDirectories(cacheFile.getParent());
            Files.write(cacheFile, png);
        } catch (IOException ignored) {
            // 캐시 저장 실패는 응답에 영향 없음
        }
        return png;
    }

    @GetMapping("/commits/{commitHash}/download")
    public ResponseEntity<byte[]> download(@PathVariable String projectId, @PathVariable String commitHash) throws IOException {
        VersionsRepository.StoredFile file = repo.findFile(projectId, commitHash);
        if (file == null || file.filePath() == null) throw new ApiException("다운로드할 파일이 없습니다: " + commitHash);
        byte[] bytes = Files.readAllBytes(Path.of(file.filePath()));
        String downloadName = file.fileName() == null ? commitHash + ".pptx" : file.fileName();
        // filename(String)만 쓰면 비ISO-8859-1 문자(한글 등)를 그대로 헤더에 넣어 Tomcat이 헤더 전체를 버린다.
        // RFC 5987 인코딩(filename*=UTF-8''...)을 쓰도록 charset을 지정한다.
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        ContentDisposition.attachment().filename(downloadName, java.nio.charset.StandardCharsets.UTF_8).build().toString())
                .contentType(org.springframework.http.MediaType.APPLICATION_OCTET_STREAM)
                .body(bytes);
    }

    /**
     * 슬라이드 썸네일이 이미 내용을 보여주므로 제목·핵심내용을 텍스트로 다시 베껴 적지 않는다.
     * 목차의 예상 장수만 실제 업로드 장수로 갱신한다. 파일을 읽지 못했을 때의 경고는
     * 제안서 관리 화면의 커밋 목록에서 slideCount로 보여준다(viewVersions의 unreadable 배지).
     */
    private void applyExtractedContent(String projectId, String tocRowId, List<PptxExtractor.SlideContent> slides) {
        if (slides.isEmpty()) return;
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
        Path outFile = dir.resolve("merge-" + System.currentTimeMillis() + ".pptx");
        PptxMerger.MergeResult result = merger.merge(sourceFiles, outFile);
        return repo.createSnapshot(projectId, req.branch(), req.message(), req.who(),
                outFile.toString(), result.slideCount(), result.skippedFiles());
    }
}
