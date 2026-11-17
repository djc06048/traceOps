package com.prowin.rfp;

import com.prowin.common.ApiException;
import com.prowin.common.FileNames;
import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.UUID;

@RestController
@RequestMapping("/api/projects/{projectId}/rfp")
public class RfpController {

    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(".pdf", ".docx");

    public record CreateRequirementRequest(String code, String title, String description, String who) {
    }

    public record UpdateRequirementRequest(String title, String description, String who) {
    }

    public record DeleteRequest(String who, String reason) {
    }

    public record UpdateCandidateRequest(String title, String description, String who) {
    }

    public record RejectCandidateRequest(String who, String reason) {
    }

    private final RfpRepository repo;
    private final RfpRequirementExtractor extractor;
    private final String uploadBasePath;

    public RfpController(RfpRepository repo, RfpRequirementExtractor extractor,
                          @Value("${prowin.upload.path}") String uploadBasePath) {
        this.repo = repo;
        this.extractor = extractor;
        this.uploadBasePath = uploadBasePath;
    }

    @GetMapping
    public RfpResponse get(@PathVariable String projectId) {
        return new RfpResponse(repo.findDocument(projectId), repo.findRequirements(projectId));
    }

    /**
     * RFP(PDF/DOCX)를 업로드해 요구사항 후보를 규칙 기반(방식 A)으로 추출한다.
     * 자동화는 후보 생성까지만 하고, 화면에서 사람이 확인·수정 후 확정한다(candidate → confirmed).
     */
    @PostMapping(value = "/extract", consumes = "multipart/form-data")
    public RfpResponse extract(@PathVariable String projectId, @RequestParam("file") MultipartFile file,
                                @RequestParam(required = false) String receivedDate) {
        if (file == null || file.isEmpty()) throw new ApiException("RFP 파일을 선택해 주세요");
        String originalName = FileNames.sanitize(file.getOriginalFilename(), "upload.pdf");
        String lower = originalName.toLowerCase();
        if (ALLOWED_EXTENSIONS.stream().noneMatch(lower::endsWith)) {
            throw new ApiException("PDF 또는 DOCX 파일만 업로드할 수 있습니다: " + originalName);
        }
        String extension = lower.endsWith(".pdf") ? ".pdf" : ".docx";
        Path dest;
        try {
            Path dir = Path.of(uploadBasePath, projectId, "rfp");
            Files.createDirectories(dir);
            dest = dir.resolve(UUID.randomUUID() + extension);
            file.transferTo(dest);
        } catch (IOException e) {
            throw new ApiException("RFP 파일 업로드에 실패했습니다: " + e.getMessage());
        }

        String pageCount = lower.endsWith(".pdf") ? pdfPageCount(dest) : null;
        repo.saveDocument(projectId, originalName, pageCount, receivedDate, dest.toString());

        List<RfpRequirementExtractor.ExtractedCandidate> extracted = extractor.extract(dest, originalName);
        repo.saveCandidates(projectId, extracted);

        return new RfpResponse(repo.findDocument(projectId), repo.findRequirements(projectId));
    }

    private String pdfPageCount(Path file) {
        try (PDDocument pdf = Loader.loadPDF(file.toFile())) {
            return pdf.getNumberOfPages() + "페이지";
        } catch (IOException | RuntimeException e) {
            return null;
        }
    }

    @GetMapping("/candidates")
    public List<RequirementCandidate> candidates(@PathVariable String projectId) {
        return repo.findCandidates(projectId);
    }

    @PutMapping("/candidates/{id}")
    public RequirementCandidate updateCandidate(@PathVariable String projectId, @PathVariable String id,
                                                 @RequestBody UpdateCandidateRequest req) {
        return repo.updateCandidate(projectId, id, req.title(), req.description(), req.who());
    }

    @PostMapping("/candidates/{id}/confirm")
    public RfpRequirement confirmCandidate(@PathVariable String projectId, @PathVariable String id,
                                            @RequestBody(required = false) CreateRequirementRequest req) {
        return repo.confirmCandidate(projectId, id, req == null ? null : req.who());
    }

    @PostMapping("/candidates/{id}/reject")
    public void rejectCandidate(@PathVariable String projectId, @PathVariable String id,
                                 @RequestBody RejectCandidateRequest req) {
        repo.rejectCandidate(projectId, id, req.who(), req.reason());
    }

    @PostMapping("/requirements")
    public RfpRequirement create(@PathVariable String projectId, @RequestBody CreateRequirementRequest req) {
        return repo.create(projectId, req.code(), req.title(), req.description(), req.who());
    }

    @PutMapping("/requirements/{id}")
    public RfpRequirement update(@PathVariable String projectId, @PathVariable String id, @RequestBody UpdateRequirementRequest req) {
        return repo.update(projectId, id, req.title(), req.description(), req.who());
    }

    @DeleteMapping("/requirements/{id}")
    public void delete(@PathVariable String projectId, @PathVariable String id, @RequestBody DeleteRequest req) {
        repo.delete(projectId, id, req.who(), req.reason());
    }
}
