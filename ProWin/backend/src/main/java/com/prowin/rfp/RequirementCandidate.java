package com.prowin.rfp;

/** status: candidate(자동 추출, 미확정) / confirmed(요구사항으로 반영) / rejected(사람이 거절) */
public record RequirementCandidate(String id, String code, String title, String description,
                                    String sourcePage, double confidence, String status, String createdAt) {
}
