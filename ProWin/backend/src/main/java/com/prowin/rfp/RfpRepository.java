package com.prowin.rfp;

import java.util.List;

public interface RfpRepository {
    RfpDocument findDocument(String projectId);

    List<RfpRequirement> findRequirements(String projectId);

    RfpRequirement create(String projectId, String code, String title, String description, String who);

    RfpRequirement update(String projectId, String id, String title, String description, String who);

    void delete(String projectId, String id, String who, String reason);

    /** RFP 파일 업로드 시 문서 메타(파일명·페이지수·수령일·저장경로)를 갱신한다. */
    RfpDocument saveDocument(String projectId, String fileName, String pageCount, String receivedDate, String filePath);

    /** 추출된 후보를 candidate 상태로 저장한다. 기존 미확정(candidate) 후보는 재추출 시 비운다. */
    List<RequirementCandidate> saveCandidates(String projectId, List<RfpRequirementExtractor.ExtractedCandidate> candidates);

    List<RequirementCandidate> findCandidates(String projectId);

    RequirementCandidate updateCandidate(String projectId, String id, String title, String description, String who);

    /** candidate를 rfp_requirement로 확정 반영하고 candidate 상태를 confirmed로 바꾼다. */
    RfpRequirement confirmCandidate(String projectId, String id, String who);

    void rejectCandidate(String projectId, String id, String who, String reason);
}
