package com.prowin.versions;

import java.util.List;

public interface VersionsRepository {
    record StoredFile(String fileName, String filePath) {
    }

    VersionsResponse findAll(String projectId);

    ProposalCommit createCommit(String projectId, String branch, String message, String who, String fileName, String filePath, String tocRowId, int slideCount);

    /** 표시 파일명(제안서_합본_vX.Y.pptx)은 저장소가 스냅샷 번호 규칙에 따라 직접 만든다. */
    ProposalCommit createSnapshot(String projectId, String branch, String message, String who, String filePath, int slideCount, List<String> skippedFiles);

    StoredFile findFile(String projectId, String commitHash);
}
