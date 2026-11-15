package com.prowin.toc;

import com.prowin.common.ApiException;
import com.prowin.common.IdGen;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class SqliteTocRepository implements TocRepository {

    private final JdbcTemplate jdbc;

    public SqliteTocRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private static TocRow mapRow(java.sql.ResultSet rs, int i) throws java.sql.SQLException {
        return new TocRow(rs.getString("id"), rs.getInt("level"), rs.getString("title"), rs.getString("owner"),
                rs.getString("pages"), rs.getString("status"), rs.getInt("order_index"),
                rs.getInt("presentation_assigned") != 0);
    }

    @Override
    public List<TocRow> findAll(String projectId) {
        return jdbc.query(
                "SELECT id, level, title, owner, pages, status, order_index, presentation_assigned FROM toc_row " +
                        "WHERE project_id = ? AND deleted_at IS NULL ORDER BY order_index",
                SqliteTocRepository::mapRow, projectId);
    }

    @Override
    public TocRow create(String projectId, int level, String title, String owner, String pages, String status, String who) {
        if (title == null || title.isBlank()) throw new ApiException("제목을 입력해 주세요");
        List<String> ids = jdbc.query("SELECT id FROM toc_row WHERE project_id = ?",
                (rs, i) -> rs.getString("id"), projectId);
        String id = IdGen.next("T", ids, x -> x);
        Integer maxOrder = jdbc.queryForObject("SELECT COALESCE(MAX(order_index), 0) FROM toc_row WHERE project_id = ?",
                Integer.class, projectId);
        int orderIndex = (maxOrder == null ? 0 : maxOrder) + 1;
        jdbc.update("INSERT INTO toc_row (id, project_id, level, title, owner, pages, status, order_index, presentation_assigned) " +
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)",
                id, projectId, level, title, owner, pages, status, orderIndex);
        return new TocRow(id, level, title, owner, pages, status, orderIndex, false);
    }

    @Override
    public TocRow update(String projectId, String id, int level, String title, String owner, String pages, String status, String who) {
        if (title == null || title.isBlank()) throw new ApiException("제목을 입력해 주세요");
        int n = jdbc.update("UPDATE toc_row SET level = ?, title = ?, owner = ?, pages = ?, status = ? " +
                        "WHERE project_id = ? AND id = ? AND deleted_at IS NULL",
                level, title, owner, pages, status, projectId, id);
        if (n == 0) throw new ApiException("목차를 찾을 수 없습니다: " + id);
        return jdbc.queryForObject(
                "SELECT id, level, title, owner, pages, status, order_index, presentation_assigned FROM toc_row WHERE project_id = ? AND id = ?",
                SqliteTocRepository::mapRow, projectId, id);
    }

    @Override
    public void updatePages(String projectId, String id, String pages) {
        jdbc.update("UPDATE toc_row SET pages = ? WHERE project_id = ? AND id = ? AND deleted_at IS NULL",
                pages, projectId, id);
    }

    @Override
    public void delete(String projectId, String id, String who, String reason) {
        if (reason == null || reason.isBlank()) throw new ApiException("삭제 사유를 입력해 주세요");
        int n = jdbc.update("UPDATE toc_row SET deleted_at = ?, deleted_by = ?, deleted_reason = ? " +
                        "WHERE project_id = ? AND id = ? AND deleted_at IS NULL",
                com.prowin.common.Clock.nowText(), who, reason, projectId, id);
        if (n == 0) throw new ApiException("목차를 찾을 수 없습니다: " + id);
    }
}
