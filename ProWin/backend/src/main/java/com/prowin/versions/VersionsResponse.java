package com.prowin.versions;

import java.util.List;

public record VersionsResponse(List<String> branches, List<ProposalCommit> commits) {
}
