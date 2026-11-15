package com.prowin.rfp;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/projects/{projectId}/rfp")
public class RfpController {

    public record CreateRequirementRequest(String code, String title, String description, String who) {
    }

    public record UpdateRequirementRequest(String title, String description, String who) {
    }

    public record DeleteRequest(String who, String reason) {
    }

    private final RfpRepository repo;

    public RfpController(RfpRepository repo) {
        this.repo = repo;
    }

    @GetMapping
    public RfpResponse get(@PathVariable String projectId) {
        return new RfpResponse(repo.findDocument(projectId), repo.findRequirements(projectId));
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
