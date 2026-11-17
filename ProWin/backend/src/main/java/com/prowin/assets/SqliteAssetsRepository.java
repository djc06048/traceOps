package com.prowin.assets;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.prowin.common.Clock;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * P0 단계(메타·키워드 검색)만 구현한다: SQL LIKE + 메타 필터.
 * 이 라이브러리 규모(과거 제안서 수백~수천 슬라이드)에서는 LIKE로 충분하고 외부 의존이 없다.
 * 자산이 수만 건 이상으로 늘어 LIKE 성능이 문제가 되면 FTS5(trigram)나 P1 의미 검색으로 전환을 검토한다.
 */
@Repository
public class SqliteAssetsRepository implements AssetsRepository {

    private final JdbcTemplate jdbc;
    private final ObjectMapper json;

    public SqliteAssetsRepository(JdbcTemplate jdbc, ObjectMapper json) {
        this.jdbc = jdbc;
        this.json = json;
    }

    private List<String> parseTags(String raw) {
        if (raw == null || raw.isBlank()) return List.of();
        try {
            return json.readValue(raw, new TypeReference<List<String>>() {
            });
        } catch (Exception e) {
            return List.of();
        }
    }

    private String writeTags(List<String> tags) {
        try {
            return json.writeValueAsString(tags == null ? List.of() : tags);
        } catch (Exception e) {
            return "[]";
        }
    }

    private final org.springframework.jdbc.core.RowMapper<AssetSlide> mapper = (rs, i) -> new AssetSlide(
            rs.getString("id"), rs.getString("proposal_name"), rs.getString("client_sector"), rs.getString("year"),
            rs.getInt("won") != 0, rs.getString("author"), rs.getString("confidentiality"),
            parseTags(rs.getString("tags")), rs.getInt("slide_number"), rs.getString("title"), rs.getString("body"),
            rs.getString("created_at"));

    @Override
    public List<AssetSlide> ingest(String proposalName, String clientSector, String year, boolean won,
                                    String author, String confidentiality, List<String> tags,
                                    String sourceFile, List<NewSlide> slides) {
        String now = Clock.nowText();
        String tagsJson = writeTags(tags);
        List<String> ids = new ArrayList<>();
        for (NewSlide slide : slides) {
            String id = UUID.randomUUID().toString();
            ids.add(id);
            jdbc.update("INSERT INTO asset_slide (id, proposal_name, client_sector, year, won, author, confidentiality, tags, slide_number, title, body, source_file, created_at) " +
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    id, proposalName, clientSector, year, won ? 1 : 0, author, confidentiality, tagsJson,
                    slide.slideNumber(), slide.title(), slide.body(), sourceFile, now);
        }
        List<AssetSlide> result = new ArrayList<>();
        for (String id : ids) result.add(jdbc.queryForObject("SELECT * FROM asset_slide WHERE id = ?", mapper, id));
        return result;
    }

    @Override
    public List<AssetSlide> search(SearchFilter filter, int limit) {
        StringBuilder sql = new StringBuilder("SELECT * FROM asset_slide WHERE 1=1");
        List<Object> args = new ArrayList<>();
        if (filter.keyword() != null && !filter.keyword().isBlank()) {
            sql.append(" AND (title LIKE ? OR body LIKE ? OR tags LIKE ? OR proposal_name LIKE ?)");
            String like = "%" + filter.keyword().strip() + "%";
            args.add(like);
            args.add(like);
            args.add(like);
            args.add(like);
        }
        if (filter.clientSector() != null && !filter.clientSector().isBlank()) {
            sql.append(" AND client_sector = ?");
            args.add(filter.clientSector());
        }
        if (filter.year() != null && !filter.year().isBlank()) {
            sql.append(" AND year = ?");
            args.add(filter.year());
        }
        if (filter.won() != null) {
            sql.append(" AND won = ?");
            args.add(filter.won() ? 1 : 0);
        }
        sql.append(" ORDER BY created_at DESC LIMIT ?");
        args.add(limit);
        return jdbc.query(sql.toString(), mapper, args.toArray());
    }

    @Override
    public List<AssetSlide> findAll() {
        return jdbc.query("SELECT * FROM asset_slide ORDER BY created_at DESC", mapper);
    }
}
