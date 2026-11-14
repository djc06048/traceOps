package com.prowin.review;

import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/projects/{projectId}/review")
public class ReviewController {

    public record NodeRequest(String memo, String titleDetail, List<String> flowSteps, List<String> bullets, String who) {
    }

    public record CommentRequest(String author, String body) {
    }

    public record PresentationRequest(boolean assigned, String who) {
    }

    private final ReviewRepository repo;

    public ReviewController(ReviewRepository repo) {
        this.repo = repo;
    }

    @GetMapping
    public List<ReviewNode> get(@PathVariable String projectId) {
        return repo.findAll(projectId);
    }

    @PutMapping("/nodes/{tocRowId}")
    public ReviewNode upsertNode(@PathVariable String projectId, @PathVariable String tocRowId, @RequestBody NodeRequest req) {
        return repo.upsertNode(projectId, tocRowId, req.memo(), req.titleDetail(), req.flowSteps(), req.bullets(), req.who());
    }

    @PostMapping("/nodes/{tocRowId}/comments")
    public ReviewComment addComment(@PathVariable String projectId, @PathVariable String tocRowId, @RequestBody CommentRequest req) {
        return repo.addComment(projectId, tocRowId, req.author(), req.body());
    }

    @PutMapping("/nodes/{tocRowId}/presentation")
    public void setPresentation(@PathVariable String projectId, @PathVariable String tocRowId, @RequestBody PresentationRequest req) {
        repo.setPresentation(projectId, tocRowId, req.assigned(), req.who());
    }
}
