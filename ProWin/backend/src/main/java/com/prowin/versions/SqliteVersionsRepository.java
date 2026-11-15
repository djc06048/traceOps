package com.prowin.versions;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.prowin.common.ApiException;
import com.prowin.common.Clock;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.security.SecureRandom;
import java.util.List;

@Repository
public class SqliteVersionsRepository implements VersionsRepository {

    private static final SecureRandom RANDOM = new SecureRandom();
    private final JdbcTemplate jdbc;
    private final ObjectMapper json;

    public SqliteVersionsRepository(JdbcTemplate jdbc, ObjectMapper json) {
        this.jdbc = jdbc;
        this.json = json;
    }

    private List<DiffEntry> parseDiff(String raw) {
        if (raw == null || raw.isBlank()) return List.of();
        try {
            return json.readValue(raw, new TypeReference<List<DiffEntry>>() {
            });
        } catch (Exception e) {
            return List.of();
        }
    }

    private String writeDiff(List<DiffEntry> diff) {
        try {
            return json.writeValueAsString(diff == null ? List.of() : diff);
        } catch (Exception e) {
            return "[]";
        }
    }

    private String randomHash() {
        byte[] bytes = new byte[3];
        RANDOM.nextBytes(bytes);
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) sb.append(String.format("%02x", b));
        return sb.toString();
    }

    @Override
    public VersionsResponse findAll(String projectId) {
        List<String> branches = jdbc.query(
                "SELECT branch FROM proposal_commit WHERE project_id = ? GROUP BY branch ORDER BY MIN(rowid)",
                (rs, i) -> rs.getString("branch"), projectId);
        List<ProposalCommit> commits = jdbc.query(
                "SELECT commit_hash, branch, message, tag, uploaded_by, uploaded_at, file_name, is_snapshot, diff_json, toc_row_id, slide_count " +
                        "FROM proposal_commit WHERE project_id = ? ORDER BY rowid DESC",
                (rs, i) -> new ProposalCommit(rs.getString("commit_hash"), rs.getString("branch"), rs.getString("message"),
                        rs.getString("tag"), rs.getString("uploaded_by"), rs.getString("uploaded_at"),
                        rs.getString("file_name"), rs.getInt("is_snapshot") != 0, parseDiff(rs.getString("diff_json")),
                        rs.getString("toc_row_id"), rs.getInt("slide_count")),
                projectId);
        return new VersionsResponse(branches, commits);
    }

    @Override
    public ProposalCommit createCommit(String projectId, String branch, String message, String who, String fileName, String filePath, String tocRowId, int slideCount) {
        if (message == null || message.isBlank()) throw new ApiException("커밋 메시지를 입력해 주세요");
        String hash = randomHash();
        String now = Clock.nowText();
        String branchName = (branch == null || branch.isBlank()) ? "main" : branch;
        jdbc.update("INSERT INTO proposal_commit (commit_hash, project_id, branch, message, tag, uploaded_by, uploaded_at, file_name, file_path, is_snapshot, diff_json, toc_row_id, slide_count) " +
                        "VALUES (?, ?, ?, ?, NULL, ?, ?, ?, ?, 0, '[]', ?, ?)",
                hash, projectId, branchName, message, who, now, fileName, filePath, tocRowId, slideCount);
        return new ProposalCommit(hash, branchName, message, null, who, now, fileName, false, List.of(), tocRowId, slideCount);
    }

    @Override
    public StoredFile findFile(String projectId, String commitHash) {
        List<StoredFile> rows = jdbc.query("SELECT file_name, file_path FROM proposal_commit WHERE project_id = ? AND commit_hash = ?",
                (rs, i) -> new StoredFile(rs.getString("file_name"), rs.getString("file_path")), projectId, commitHash);
        return rows.isEmpty() ? null : rows.get(0);
    }

    @Override
    public ProposalCommit createSnapshot(String projectId, String branch, String message, String who, String fileName, String filePath, int slideCount) {
        if (message == null || message.isBlank()) throw new ApiException("합본 메시지를 입력해 주세요");
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM proposal_commit WHERE project_id = ?", Integer.class, projectId);
        int num = (count == null ? 0 : count) + 1;
        String tag = "v1." + num;
        String hash = "snap" + randomHash();
        String now = Clock.nowText();
        String branchName = (branch == null || branch.isBlank()) ? "main" : branch;
        List<DiffEntry> diff = List.of(new DiffEntry("add", "+ 스냅샷", "현재 각 노드의 최신본을 묶어 생성"));
        jdbc.update("INSERT INTO proposal_commit (commit_hash, project_id, branch, message, tag, uploaded_by, uploaded_at, file_name, file_path, is_snapshot, diff_json, slide_count) " +
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)",
                hash, projectId, branchName, message, tag, who, now, fileName, filePath, writeDiff(diff), slideCount);
        return new ProposalCommit(hash, branchName, message, tag, who, now, fileName, true, diff, null, slideCount);
    }
}
