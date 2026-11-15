package com.prowin.toc;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/projects/{projectId}/toc")
public class TocController {

    public record RowRequest(int level, String title, String owner, String pages, String status, String who) {
    }

    public record DeleteRequest(String who, String reason) {
    }

    private final TocRepository repo;

    public TocController(TocRepository repo) {
        this.repo = repo;
    }

    @GetMapping
    public TocResponse get(@PathVariable String projectId) {
        return new TocResponse(repo.findAll(projectId), TocResponse.STATUS_LABEL);
    }

    @PostMapping("/rows")
    public TocRow create(@PathVariable String projectId, @RequestBody RowRequest req) {
        return repo.create(projectId, req.level(), req.title(), req.owner(), req.pages(), req.status(), req.who());
    }

    @PutMapping("/rows/{id}")
    public TocRow update(@PathVariable String projectId, @PathVariable String id, @RequestBody RowRequest req) {
        return repo.update(projectId, id, req.level(), req.title(), req.owner(), req.pages(), req.status(), req.who());
    }

    @DeleteMapping("/rows/{id}")
    public void delete(@PathVariable String projectId, @PathVariable String id, @RequestBody DeleteRequest req) {
        repo.delete(projectId, id, req.who(), req.reason());
    }
}
