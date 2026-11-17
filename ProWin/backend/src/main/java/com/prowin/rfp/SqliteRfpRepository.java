package com.prowin.rfp;

import com.prowin.common.ApiException;
import com.prowin.common.Clock;
import com.prowin.common.IdGen;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

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

    @Override
    public RfpDocument saveDocument(String projectId, String fileName, String pageCount, String receivedDate, String filePath) {
        int n = jdbc.update("UPDATE rfp_document SET file_name = ?, page_count = ?, received_date = ?, file_path = ? WHERE project_id = ?",
                fileName, pageCount, receivedDate, filePath, projectId);
        if (n == 0) {
            jdbc.update("INSERT INTO rfp_document (project_id, file_name, page_count, received_date, file_path) VALUES (?, ?, ?, ?, ?)",
                    projectId, fileName, pageCount, receivedDate, filePath);
        }
        return new RfpDocument(fileName, pageCount, receivedDate);
    }

    @Override
    public List<RequirementCandidate> saveCandidates(String projectId, List<RfpRequirementExtractor.ExtractedCandidate> candidates) {
        // 재추출 시 이전에 확정/거절되지 않은 후보는 비우고 새로 채운다
        jdbc.update("DELETE FROM rfp_requirement_candidate WHERE project_id = ? AND status = 'candidate'", projectId);
        String now = Clock.nowText();
        for (RfpRequirementExtractor.ExtractedCandidate c : candidates) {
            String id = UUID.randomUUID().toString();
            jdbc.update("INSERT INTO rfp_requirement_candidate (id, project_id, code, title, description, source_page, confidence, status, created_at, updated_at) " +
                            "VALUES (?, ?, ?, ?, ?, ?, ?, 'candidate', ?, ?)",
                    id, projectId, c.code(), c.title(), c.description(), c.sourcePage(), c.confidence(), now, now);
        }
        return findCandidates(projectId);
    }

    @Override
    public List<RequirementCandidate> findCandidates(String projectId) {
        return jdbc.query(
                "SELECT id, code, title, description, source_page, confidence, status, created_at FROM rfp_requirement_candidate " +
                        "WHERE project_id = ? ORDER BY created_at DESC",
                (rs, i) -> new RequirementCandidate(rs.getString("id"), rs.getString("code"), rs.getString("title"),
                        rs.getString("description"), rs.getString("source_page"), rs.getDouble("confidence"),
                        rs.getString("status"), rs.getString("created_at")),
                projectId);
    }

    private RequirementCandidate findCandidate(String projectId, String id) {
        List<RequirementCandidate> rows = jdbc.query(
                "SELECT id, code, title, description, source_page, confidence, status, created_at FROM rfp_requirement_candidate " +
                        "WHERE project_id = ? AND id = ?",
                (rs, i) -> new RequirementCandidate(rs.getString("id"), rs.getString("code"), rs.getString("title"),
                        rs.getString("description"), rs.getString("source_page"), rs.getDouble("confidence"),
                        rs.getString("status"), rs.getString("created_at")),
                projectId, id);
        if (rows.isEmpty()) throw new ApiException("후보를 찾을 수 없습니다: " + id);
        return rows.get(0);
    }

    @Override
    public RequirementCandidate updateCandidate(String projectId, String id, String title, String description, String who) {
        findCandidate(projectId, id);
        if (title == null || title.isBlank()) throw new ApiException("요구사항을 입력해 주세요");
        jdbc.update("UPDATE rfp_requirement_candidate SET title = ?, description = ?, updated_at = ? WHERE project_id = ? AND id = ?",
                title, description, Clock.nowText(), projectId, id);
        return findCandidate(projectId, id);
    }

    @Override
    public RfpRequirement confirmCandidate(String projectId, String id, String who) {
        RequirementCandidate candidate = findCandidate(projectId, id);
        if (!"candidate".equals(candidate.status())) throw new ApiException("이미 처리된 후보입니다: " + id);
        String code = candidate.code();
        if (code == null || code.isBlank()) {
            code = IdGen.next("REQ", findRequirements(projectId), RfpRequirement::code);
        }
        // 코드가 이미 쓰이고 있으면 겹치지 않게 접미사를 붙인다
        java.util.Set<String> existingCodes = new java.util.HashSet<>();
        for (RfpRequirement r : findRequirements(projectId)) existingCodes.add(r.code());
        String candidateCode = code;
        int suffix = 1;
        while (existingCodes.contains(candidateCode)) {
            candidateCode = code + "-" + (++suffix);
        }
        RfpRequirement created = create(projectId, candidateCode, candidate.title(), candidate.description(), who);
        jdbc.update("UPDATE rfp_requirement_candidate SET status = 'confirmed', updated_at = ? WHERE project_id = ? AND id = ?",
                Clock.nowText(), projectId, id);
        return created;
    }

    @Override
    public void rejectCandidate(String projectId, String id, String who, String reason) {
        findCandidate(projectId, id);
        jdbc.update("UPDATE rfp_requirement_candidate SET status = 'rejected', updated_at = ? WHERE project_id = ? AND id = ?",
                Clock.nowText(), projectId, id);
    }
}
