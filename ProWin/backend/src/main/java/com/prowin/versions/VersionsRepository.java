package com.prowin.versions;

public interface VersionsRepository {
    record StoredFile(String fileName, String filePath) {
    }

    VersionsResponse findAll(String projectId);

    ProposalCommit createCommit(String projectId, String branch, String message, String who, String fileName, String filePath, String tocRowId, int slideCount);

    ProposalCommit createSnapshot(String projectId, String branch, String message, String who, String fileName, String filePath, int slideCount);

    StoredFile findFile(String projectId, String commitHash);
}
