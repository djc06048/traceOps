package com.prowin.review;

import java.util.List;

public interface ReviewRepository {
    List<ReviewNode> findAll(String projectId);

    ReviewNode upsertNode(String projectId, String tocRowId, String memo, String titleDetail,
                           List<String> flowSteps, List<String> bullets, String who);

    ReviewComment addComment(String projectId, String tocRowId, String author, String body);

    void setPresentation(String projectId, String tocRowId, boolean assigned, String who);
}
