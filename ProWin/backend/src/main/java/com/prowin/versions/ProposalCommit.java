package com.prowin.versions;

import java.util.List;

public record ProposalCommit(String commitHash, String branch, String message, String tag, String uploadedBy,
                              String uploadedAt, String fileName, boolean isSnapshot, List<DiffEntry> diff, String tocRowId,
                              int slideCount) {
}
