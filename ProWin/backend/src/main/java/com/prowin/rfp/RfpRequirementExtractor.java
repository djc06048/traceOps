package com.prowin.rfp;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.apache.poi.xwpf.usermodel.XWPFTableCell;
import org.apache.poi.xwpf.usermodel.XWPFTableRow;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * ReqSync와 같은 원칙: 자동화는 후보 추출까지만 한다. 확정은 사람(PM·사업관리)이 한다.
 * 방식 A(규칙 기반) 전용 PoC — 요구사항 총괄표 파싱(DOCX)과 번호 패턴 탐지(PDF/DOCX 본문)만 수행하고,
 * LLM 기반 방식 B(본문 보완)는 1-7의 결정사항(LLM 사용 가능 범위)이 확정된 뒤 추가한다.
 */
@Component
public class RfpRequirementExtractor {

    public record ExtractedCandidate(String code, String title, String description, String sourcePage, double confidence) {
    }

    private static final Pattern CODE_PATTERN = Pattern.compile("\\b[A-Z]{2,8}(?:[-_][A-Z0-9]{1,8}){1,2}\\b");

    public List<ExtractedCandidate> extract(Path file, String originalName) {
        String lower = originalName == null ? "" : originalName.toLowerCase();
        try {
            if (lower.endsWith(".docx")) return extractDocx(file);
            if (lower.endsWith(".pdf")) return extractPdf(file);
        } catch (IOException | RuntimeException e) {
            return List.of();
        }
        return List.of();
    }

    // ---------- DOCX: 표 파싱 우선 ----------

    private List<ExtractedCandidate> extractDocx(Path file) throws IOException {
        List<ExtractedCandidate> out = new ArrayList<>();
        try (InputStream in = Files.newInputStream(file); XWPFDocument doc = new XWPFDocument(in)) {
            for (XWPFTable table : doc.getTables()) {
                out.addAll(extractFromTable(table));
            }
            if (out.isEmpty()) {
                // 표가 없으면 본문 문단에서 번호 패턴만 보조로 찾는다(방식 A의 최소 보강)
                StringBuilder text = new StringBuilder();
                doc.getParagraphs().forEach(p -> text.append(p.getText()).append('\n'));
                out.addAll(extractByPattern(text.toString(), null));
            }
        }
        return dedupe(out);
    }

    private List<ExtractedCandidate> extractFromTable(XWPFTable table) {
        List<XWPFTableRow> rows = table.getRows();
        if (rows.isEmpty()) return List.of();
        List<String> header = rowCells(rows.get(0));
        int codeCol = findColumn(header, "고유번호", "번호", "id", "코드");
        int titleCol = findColumn(header, "요구사항명", "명칭", "제목", "요구사항", "title", "name");
        int descCol = findColumn(header, "요구사항 내용", "상세설명", "설명", "내용", "description", "detail");
        boolean headerMatched = codeCol >= 0 || titleCol >= 0;

        List<ExtractedCandidate> out = new ArrayList<>();
        for (int r = headerMatched ? 1 : 0; r < rows.size(); r++) {
            List<String> cells = rowCells(rows.get(r));
            if (cells.isEmpty() || cells.stream().allMatch(String::isBlank)) continue;

            String code = cellAt(cells, codeCol);
            String title = cellAt(cells, titleCol);
            String desc = cellAt(cells, descCol);
            if (isBlank(code)) code = firstCodeIn(String.join(" ", cells));
            if (isBlank(title)) title = cells.size() > 1 ? cells.get(1) : cells.get(0);
            if (isBlank(desc) && cells.size() > 2) desc = cells.get(cells.size() - 1);
            if (isBlank(title)) continue;

            double confidence = (codeCol >= 0 && titleCol >= 0) ? 0.9 : headerMatched ? 0.7 : 0.5;
            out.add(new ExtractedCandidate(isBlank(code) ? null : code.trim(), title.trim(),
                    isBlank(desc) ? null : desc.trim(), null, confidence));
        }
        return out;
    }

    private List<String> rowCells(XWPFTableRow row) {
        List<String> cells = new ArrayList<>();
        for (XWPFTableCell cell : row.getTableCells()) cells.add(cell.getText() == null ? "" : cell.getText().strip());
        return cells;
    }

    private int findColumn(List<String> header, String... keywords) {
        for (int i = 0; i < header.size(); i++) {
            String h = header.get(i).toLowerCase().replace(" ", "");
            for (String kw : keywords) {
                if (h.contains(kw.toLowerCase().replace(" ", ""))) return i;
            }
        }
        return -1;
    }

    private String cellAt(List<String> cells, int index) {
        return index >= 0 && index < cells.size() ? cells.get(index) : null;
    }

    // ---------- PDF: 페이지별 텍스트에서 번호 패턴 탐지 ----------

    private List<ExtractedCandidate> extractPdf(Path file) throws IOException {
        List<ExtractedCandidate> out = new ArrayList<>();
        try (PDDocument pdf = Loader.loadPDF(file.toFile())) {
            PDFTextStripper stripper = new PDFTextStripper();
            int pageCount = pdf.getNumberOfPages();
            for (int page = 1; page <= pageCount; page++) {
                stripper.setStartPage(page);
                stripper.setEndPage(page);
                String text = stripper.getText(pdf);
                out.addAll(extractByPattern(text, String.valueOf(page)));
            }
        }
        return dedupe(out);
    }

    /** "SFR-001 요구사항 설명 ~" 같이 번호로 시작하는 줄을 후보 한 건으로 본다(표 형식이 아닌 본문 대상). */
    private List<ExtractedCandidate> extractByPattern(String text, String sourcePage) {
        List<ExtractedCandidate> out = new ArrayList<>();
        for (String rawLine : text.split("\\r?\\n")) {
            String line = rawLine.strip();
            if (line.isBlank()) continue;
            Matcher m = CODE_PATTERN.matcher(line);
            if (!m.find()) continue;
            String code = m.group();
            String rest = (line.substring(0, m.start()) + " " + line.substring(m.end())).strip();
            if (rest.isBlank()) continue;
            out.add(new ExtractedCandidate(code, rest, null, sourcePage, 0.6));
        }
        return out;
    }

    private String firstCodeIn(String text) {
        Matcher m = CODE_PATTERN.matcher(text);
        return m.find() ? m.group() : null;
    }

    private boolean isBlank(String s) {
        return s == null || s.isBlank();
    }

    /** 같은 code(없으면 title)가 여러 번 나오면 가장 신뢰도 높은 것만 남긴다. */
    private List<ExtractedCandidate> dedupe(List<ExtractedCandidate> candidates) {
        Map<String, ExtractedCandidate> byKey = new LinkedHashMap<>();
        for (ExtractedCandidate c : candidates) {
            String key = isBlank(c.code()) ? "title:" + c.title() : "code:" + c.code();
            ExtractedCandidate existing = byKey.get(key);
            if (existing == null || c.confidence() > existing.confidence()) byKey.put(key, c);
        }
        return new ArrayList<>(byKey.values());
    }
}
