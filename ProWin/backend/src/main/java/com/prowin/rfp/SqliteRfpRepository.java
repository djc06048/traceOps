package com.prowin.rfp;

import com.prowin.common.ApiException;
import com.prowin.common.Clock;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class SqliteRfpRepository implements RfpRepository {

    private final JdbcTemplate jdbc;

    public SqliteRfpRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public RfpDocument findDocument(String projectId) {
        try {
            return jdbc.queryForObject(
                    "SELECT file_name, page_count, received_date FROM rfp_document WHERE project_id = ?",
                    (rs, i) -> new RfpDocument(rs.getString("file_name"), rs.getString("page_count"), rs.getString("received_date")),
                    projectId);
        } catch (EmptyResultDataAccessException e) {
            return null;
        }
    }

    @Override
    public List<RfpRequirement> findRequirements(String projectId) {
        return jdbc.query(
                "SELECT id, code, title, description, created_at, updated_at FROM rfp_requirement " +
                        "WHERE project_id = ? AND deleted_at IS NULL ORDER BY code",
                (rs, i) -> new RfpRequirement(rs.getString("id"), rs.getString("code"), rs.getString("title"),
                        rs.getString("description"), rs.getString("created_at"), rs.getString("updated_at")),
                projectId);
    }

    @Override
    public RfpRequirement create(String projectId, String code, String title, String description, String who) {
        if (code == null || code.isBlank()) throw new ApiException("ID(코드)를 입력해 주세요");
        if (title == null || title.isBlank()) throw new ApiException("요구사항을 입력해 주세요");
        Integer count = jdbc.queryForObject(
                "SELECT COUNT(*) FROM rfp_requirement WHERE project_id = ? AND code = ? AND deleted_at IS NULL",
                Integer.class, projectId, code);
        if (count != null && count > 0) throw new ApiException("이미 존재하는 ID입니다: " + code);
        String now = Clock.nowText();
        jdbc.update("INSERT INTO rfp_requirement (id, project_id, code, title, description, created_at, updated_at) " +
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                code, projectId, code, title, description, now, now);
        return new RfpRequirement(code, code, title, description, now, now);
    }

    @Override
    public RfpRequirement update(String projectId, String id, String title, String description, String who) {
        if (title == null || title.isBlank()) throw new ApiException("요구사항을 입력해 주세요");
        String now = Clock.nowText();
        int n = jdbc.update("UPDATE rfp_requirement SET title = ?, description = ?, updated_at = ? " +
                        "WHERE project_id = ? AND id = ? AND deleted_at IS NULL",
                title, description, now, projectId, id);
        if (n == 0) throw new ApiException("요구사항을 찾을 수 없습니다: " + id);
        return jdbc.queryForObject(
                "SELECT id, code, title, description, created_at, updated_at FROM rfp_requirement WHERE project_id = ? AND id = ?",
                (rs, i) -> new RfpRequirement(rs.getString("id"), rs.getString("code"), rs.getString("title"),
                        rs.getString("description"), rs.getString("created_at"), rs.getString("updated_at")),
                projectId, id);
    }

    @Override
    public void delete(String projectId, String id, String who, String reason) {
        if (reason == null || reason.isBlank()) throw new ApiException("삭제 사유를 입력해 주세요");
        int n = jdbc.update("UPDATE rfp_requirement SET deleted_at = ?, deleted_by = ?, deleted_reason = ? " +
                        "WHERE project_id = ? AND id = ? AND deleted_at IS NULL",
                Clock.nowText(), who, reason, projectId, id);
        if (n == 0) throw new ApiException("요구사항을 찾을 수 없습니다: " + id);
    }
}
