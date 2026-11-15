package com.prowin.common;

import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

/**
 * First-boot seed matching prowin-simple's demo data (data/{rfp,toc,review,versions}.json).
 * After the first run the DB is the source of truth; this never overwrites existing rows.
 */
@Component
public class DataSeeder implements ApplicationRunner {

    public static final String PROJECT_ID = "P-001";

    private final JdbcTemplate jdbc;

    public DataSeeder(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public void run(ApplicationArguments args) {
        Integer tocCount = jdbc.queryForObject("SELECT COUNT(*) FROM toc_row WHERE project_id = ?", Integer.class, PROJECT_ID);
        if (tocCount != null && tocCount > 0) return;

        seedRfp();
        seedToc();
        seedReview();
        seedVersions();
    }

    private void seedRfp() {
        jdbc.update("INSERT INTO rfp_document (project_id, file_name, page_count, received_date) VALUES (?, ?, ?, ?)",
                PROJECT_ID, "한화손해보험_장기_차세대_가입설계_RFP_v2.pdf", "218페이지", "2026-10-20 수령");

        String now = Clock.nowText();
        String[][] reqs = {
                {"R-01", "무중단 이관", "서비스 중단 없이 기간계→차세대 데이터 이관"},
                {"R-02", "보안 컴플라이언스", "금융 보안 가이드 준수 및 망분리 대응"},
                {"R-03", "성능 SLA", "조회 응답 3초 이내, 배치 처리 시간 목표"},
                {"R-04", "MSA 분리 방안", "가입설계/심사/계약 서비스 독립 배포"},
                {"R-05", "데이터 정합성", "복합키 기반 정합성 검증 및 보상 처리"},
                {"R-06", "운영 이관", "무중단 운영 전환 및 롤백 시나리오"},
        };
        for (String[] r : reqs) {
            jdbc.update("INSERT INTO rfp_requirement (id, project_id, code, title, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    r[0], PROJECT_ID, r[0], r[1], r[2], now, now);
        }
    }

    private void seedToc() {
        Object[][] rows = {
                {"T-01", 1, "I. 제안 개요", null, null, null, 1},
                {"T-02", 2, "1.1 추진 배경", "제안멤버1", "2p", "done", 2},
                {"T-03", 2, "1.2 사업 목표", "제안멤버1", "2p", "done", 3},
                {"T-04", 2, "1.3 제안 범위", "제안멤버1", "1p", "done", 4},
                {"T-05", 1, "II. 기술 제안", null, null, null, 5},
                {"T-06", 2, "2.1 시스템 아키텍처", "황금빛", "4p", "done", 6},
                {"T-07", 2, "2.2 MSA 전환 방안 (1/2)", "황금빛", "3p", "doing", 7},
                {"T-08", 2, "2.2 MSA 전환 방안 (2/2)", "황금빛", "3p", "doing", 8},
                {"T-09", 2, "2.3 데이터 이관", "제안멤버2", "3p", "fix", 9},
                {"T-10", 2, "2.4 성능·보안 방안", "제안멤버2", "2p", "doing", 10},
                {"T-11", 1, "III. 관리 방안", null, null, null, 11},
                {"T-12", 2, "3.1 사업관리", "제안멤버3", "–", "todo", 12},
                {"T-13", 2, "3.2 품질관리", "제안멤버3", "2p", "doing", 13},
        };
        for (Object[] r : rows) {
            jdbc.update("INSERT INTO toc_row (id, project_id, level, title, owner, pages, status, order_index, presentation_assigned) " +
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)",
                    r[0], PROJECT_ID, r[1], r[2], r[3], r[4], r[5], r[6]);
        }
    }

    private void seedReview() {
        Object[][] nodes = {
                {"T-06", "담당 황금빛 · 예상 4p · 슬라이드 4장 · v1.2", "차세대 시스템 목표 아키텍처",
                        "[\"기간계(모놀리식)\",\"전환 계층\",\"차세대(MSA)\"]",
                        "[\"언더라이팅 가이드라인 서비스 독립 배포 단위 분리\",\"MCI/EAI 연계 표준화 · 트랜잭션 정합성 보장\",\"무중단 이관을 위한 보상 트랜잭션 설계\"]"},
                {"T-07", "담당 황금빛 · 예상 3p · v1.2", "모놀리식 → MSA 분리 전략",
                        "[\"도메인 식별\",\"서비스 분리\",\"배포 단위\"]",
                        "[\"도메인 경계 기준 서비스 식별(언더라이팅/계약/지급)\",\"분리 vs 복제 테이블 분류 기준\"]"},
                {"T-08", "담당 황금빛 · 예상 3p · v1.1", "서비스 간 연계 및 이관 순서",
                        "[\"조회\",\"처리\",\"검증\"]",
                        "[\"단계별 이관 순서 및 검증 지점\",\"유지 테이블 사전적재 방안\"]"},
                {"T-09", "담당 제안멤버2 · 예상 3p · v1.1 · 보완 필요", "데이터 이관 및 정합성 방안",
                        "[\"추출\",\"검증\",\"적재\"]",
                        "[\"복합키 기반 정합성 검증\",\"이관 실패 시 롤백/재처리 시나리오\",\"⚠ 성능 SLA 수치 근거 보완 필요 (리뷰 지적)\"]"},
                {"T-13", "담당 제안멤버3 · 예상 2p · v1.2", "품질보증 및 형상관리 방안",
                        "[\"품질게이트\",\"형상관리\",\"테스트\"]",
                        "[\"단계별 품질 게이트 및 산출물 검토\",\"형상관리·변경관리 프로세스\"]"},
        };
        for (Object[] n : nodes) {
            jdbc.update("INSERT INTO review_node (toc_row_id, memo, title_detail, flow_steps, bullets) VALUES (?, ?, ?, ?, ?)",
                    n[0], n[1], n[2], n[3], n[4]);
        }
    }

    private void seedVersions() {
        // oldest first so that listing (ORDER BY rowid DESC) shows newest first, matching prowin-simple's demo order
        Object[][] commits = {
                {"000init", "main", "프로젝트 생성 · RFP 첨부", "init", "황금빛", "2일 전", 0,
                        "[{\"kind\":\"add\",\"label\":\"+ 프로젝트\",\"detail\":\"한화손해보험 워크스페이스\"},{\"kind\":\"add\",\"label\":\"+ RFP\",\"detail\":\"원문 참고자료 첨부\"}]"},
                {"901aa2", "main", "목차 초안 작성 · 담당 배정", null, "황금빛", "어제", 0,
                        "[{\"kind\":\"add\",\"label\":\"+ 목차\",\"detail\":\"3개 대분류 · 9개 하위 제목 등록\"},{\"kind\":\"add\",\"label\":\"+ 예상장수\",\"detail\":\"노드별 입력\"},{\"kind\":\"add\",\"label\":\"+ 담당\",\"detail\":\"제안멤버1/제안멤버2/제안멤버3/황금빛 배정\"}]"},
                {"44de08", "설명회-발췌", "설명회-발췌 브랜치 생성", "branch: 설명회-발췌", "황금빛", "3시간 전", 0,
                        "[{\"kind\":\"mod\",\"label\":\"~ 브랜치\",\"detail\":\"main에서 분기 — 설명회용 장표 선별\"}]"},
                {"c31b90", "main", "1차 취합 · 파트별 pptx 병합", "v1.1", "제안멤버1", "2시간 전", 1,
                        "[{\"kind\":\"add\",\"label\":\"+ 슬라이드\",\"detail\":\"1.1·2.1 파트 업로드 병합\"},{\"kind\":\"mod\",\"label\":\"~ 목차\",\"detail\":\"II. 기술 제안 정렬\"},{\"kind\":\"add\",\"label\":\"+ 담당\",\"detail\":\"2.3 제안멤버2 배정\"}]"},
                {"a7f2e1", "main", "v1.2 스냅샷 · PL 리뷰 반영", "HEAD → main · v1.2", "황금빛", "14분 전", 1,
                        "[{\"kind\":\"mod\",\"label\":\"~ 목차\",\"detail\":\"2.2 MSA 전환 · (1/2)(2/2) 하위 분리\"},{\"kind\":\"add\",\"label\":\"+ 슬라이드\",\"detail\":\"2.2 · 3장 추가\"},{\"kind\":\"add\",\"label\":\"+ 코멘트\",\"detail\":\"2.1 · 제안멤버2 \\\"다이어그램 교체\\\"\"},{\"kind\":\"mod\",\"label\":\"~ 상태\",\"detail\":\"2.3 데이터 이관 → 보완\"}]"},
        };
        for (Object[] c : commits) {
            jdbc.update("INSERT INTO proposal_commit (commit_hash, project_id, branch, message, tag, uploaded_by, uploaded_at, file_name, file_path, is_snapshot, diff_json) " +
                            "VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?)",
                    c[0], PROJECT_ID, c[1], c[2], c[3], c[4], c[5], c[6], c[7]);
        }
    }
}
