package com.prowin.review;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.prowin.common.ApiException;
import com.prowin.common.Clock;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Repository
public class SqliteReviewRepository implements ReviewRepository {

    private final JdbcTemplate jdbc;
    private final ObjectMapper json;

    public SqliteReviewRepository(JdbcTemplate jdbc, ObjectMapper json) {
        this.jdbc = jdbc;
        this.json = json;
    }

    private List<String> parseList(String raw) {
        if (raw == null || raw.isBlank()) return List.of();
        try {
            return json.readValue(raw, new TypeReference<List<String>>() {
            });
        } catch (Exception e) {
            return List.of();
        }
    }

    private String writeList(List<String> list) {
        try {
            return json.writeValueAsString(list == null ? List.of() : list);
        } catch (Exception e) {
            return "[]";
        }
    }

    private void requireTocRow(String projectId, String tocRowId) {
        Integer count = jdbc.queryForObject(
                "SELECT COUNT(*) FROM toc_row WHERE project_id = ? AND id = ? AND deleted_at IS NULL",
                Integer.class, projectId, tocRowId);
        if (count == null || count == 0) throw new ApiException("목차를 찾을 수 없습니다: " + tocRowId);
    }

    @Override
    public List<ReviewNode> findAll(String projectId) {
        Map<String, List<ReviewComment>> commentsByNode = new HashMap<>();
        jdbc.query("SELECT id, toc_row_id, author, body, created_at FROM review_comment rc " +
                        "WHERE toc_row_id IN (SELECT id FROM toc_row WHERE project_id = ?) ORDER BY id",
                rs -> {
                    String tocRowId = rs.getString("toc_row_id");
                    commentsByNode.computeIfAbsent(tocRowId, k -> new java.util.ArrayList<>())
                            .add(new ReviewComment(rs.getLong("id"), rs.getString("author"), rs.getString("body"), rs.getString("created_at")));
                }, projectId);

        return jdbc.query(
                "SELECT t.id AS toc_row_id, t.presentation_assigned, rn.memo, rn.title_detail, rn.flow_steps, rn.bullets " +
                        "FROM toc_row t LEFT JOIN review_node rn ON rn.toc_row_id = t.id " +
                        "WHERE t.project_id = ? AND t.deleted_at IS NULL AND t.level = 2 ORDER BY t.order_index",
                (rs, i) -> {
                    String tocRowId = rs.getString("toc_row_id");
                    return new ReviewNode(tocRowId, rs.getString("memo"), rs.getString("title_detail"),
                            parseList(rs.getString("flow_steps")), parseList(rs.getString("bullets")),
                            rs.getInt("presentation_assigned") != 0,
                            commentsByNode.getOrDefault(tocRowId, List.of()));
                }, projectId);
    }

    @Override
    public ReviewNode upsertNode(String projectId, String tocRowId, String memo, String titleDetail,
                                  List<String> flowSteps, List<String> bullets, String who) {
        requireTocRow(projectId, tocRowId);
        String flowJson = writeList(flowSteps);
        String bulletsJson = writeList(bullets);
        int updated = jdbc.update("UPDATE review_node SET memo = ?, title_detail = ?, flow_steps = ?, bullets = ? WHERE toc_row_id = ?",
                memo, titleDetail, flowJson, bulletsJson, tocRowId);
        if (updated == 0) {
            jdbc.update("INSERT INTO review_node (toc_row_id, memo, title_detail, flow_steps, bullets) VALUES (?, ?, ?, ?, ?)",
                    tocRowId, memo, titleDetail, flowJson, bulletsJson);
        }
        boolean presentationAssigned = Boolean.TRUE.equals(jdbc.queryForObject(
                "SELECT presentation_assigned FROM toc_row WHERE id = ?", Boolean.class, tocRowId));
        return new ReviewNode(tocRowId, memo, titleDetail, flowSteps, bullets, presentationAssigned, findComments(tocRowId));
    }

    private List<ReviewComment> findComments(String tocRowId) {
        return jdbc.query("SELECT id, author, body, created_at FROM review_comment WHERE toc_row_id = ? ORDER BY id",
                (rs, i) -> new ReviewComment(rs.getLong("id"), rs.getString("author"), rs.getString("body"), rs.getString("created_at")),
                tocRowId);
    }

    @Override
    public ReviewComment addComment(String projectId, String tocRowId, String author, String body) {
        requireTocRow(projectId, tocRowId);
        if (body == null || body.isBlank()) throw new ApiException("코멘트 내용을 입력해 주세요");
        String now = Clock.nowText();
        jdbc.update("INSERT INTO review_comment (toc_row_id, author, body, created_at) VALUES (?, ?, ?, ?)",
                tocRowId, author, body, now);
        Long id = jdbc.queryForObject("SELECT MAX(id) FROM review_comment WHERE toc_row_id = ?", Long.class, tocRowId);
        return new ReviewComment(id == null ? 0 : id, author, body, now);
    }

    @Override
    public void setPresentation(String projectId, String tocRowId, boolean assigned, String who) {
        requireTocRow(projectId, tocRowId);
        jdbc.update("UPDATE toc_row SET presentation_assigned = ? WHERE project_id = ? AND id = ?",
                assigned ? 1 : 0, projectId, tocRowId);
    }
}
