package com.prowin.review;

import java.util.List;

public record ReviewNode(String tocRowId, String memo, String titleDetail, List<String> flowSteps,
                          List<String> bullets, boolean presentationAssigned, List<ReviewComment> comments) {
}
