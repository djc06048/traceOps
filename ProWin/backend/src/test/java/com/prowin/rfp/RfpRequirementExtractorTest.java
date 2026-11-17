package com.prowin.rfp;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.apache.pdfbox.pdmodel.font.Standard14Fonts;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.apache.poi.xwpf.usermodel.XWPFTable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class RfpRequirementExtractorTest {

    private final RfpRequirementExtractor extractor = new RfpRequirementExtractor();

    @Test
    void parsesRequirementTableFromDocx(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("rfp.docx");
        try (XWPFDocument doc = new XWPFDocument()) {
            XWPFTable table = doc.createTable(3, 3);
            setRow(table, 0, "고유번호", "요구사항명", "설명");
            setRow(table, 1, "SFR-001", "무중단 이관", "서비스 중단 없이 데이터 이관");
            setRow(table, 2, "SFR-002", "보안 컴플라이언스", "금융 보안 가이드 준수");
            try (OutputStream out = Files.newOutputStream(file)) {
                doc.write(out);
            }
        }

        List<RfpRequirementExtractor.ExtractedCandidate> result = extractor.extract(file, "rfp.docx");

        assertThat(result).hasSize(2);
        RfpRequirementExtractor.ExtractedCandidate first = result.get(0);
        assertThat(first.code()).isEqualTo("SFR-001");
        assertThat(first.title()).isEqualTo("무중단 이관");
        assertThat(first.description()).isEqualTo("서비스 중단 없이 데이터 이관");
        assertThat(first.confidence()).isGreaterThanOrEqualTo(0.9);
    }

    @Test
    void fallsBackToPatternMatchingWhenDocxHasNoTable(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("rfp-no-table.docx");
        try (XWPFDocument doc = new XWPFDocument()) {
            doc.createParagraph().createRun().setText("RF_SEC_001 망분리 환경에서 동작해야 한다");
            doc.createParagraph().createRun().setText("일반 설명 문단, 패턴이 없습니다");
            try (OutputStream out = Files.newOutputStream(file)) {
                doc.write(out);
            }
        }

        List<RfpRequirementExtractor.ExtractedCandidate> result = extractor.extract(file, "rfp-no-table.docx");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).code()).isEqualTo("RF_SEC_001");
    }

    @Test
    void parsesCodePatternFromPdfAndTracksSourcePage(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("rfp.pdf");
        // PDFBox 표준 Type1 폰트는 한글 글리프가 없어 ASCII 텍스트로만 구성한다(폰트 임베딩은 이 테스트의 범위가 아님)
        try (PDDocument pdf = new PDDocument()) {
            addTextPage(pdf, "SFR-010 performance requirement under 3 seconds");
            addTextPage(pdf, "plain paragraph without any requirement code");
            try (OutputStream out = Files.newOutputStream(file)) {
                pdf.save(out);
            }
        }

        List<RfpRequirementExtractor.ExtractedCandidate> result = extractor.extract(file, "rfp.pdf");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).code()).isEqualTo("SFR-010");
        assertThat(result.get(0).sourcePage()).isEqualTo("1");
    }

    @Test
    void unsupportedExtensionReturnsEmpty(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("rfp.hwp");
        Files.writeString(file, "지원하지 않는 형식");

        assertThat(extractor.extract(file, "rfp.hwp")).isEmpty();
    }

    private void setRow(XWPFTable table, int rowIndex, String... values) {
        for (int c = 0; c < values.length; c++) {
            table.getRow(rowIndex).getCell(c).setText(values[c]);
        }
    }

    private void addTextPage(PDDocument pdf, String text) throws IOException {
        PDPage page = new PDPage();
        pdf.addPage(page);
        try (PDPageContentStream content = new PDPageContentStream(pdf, page)) {
            content.beginText();
            content.setFont(new PDType1Font(Standard14Fonts.FontName.HELVETICA), 12);
            content.newLineAtOffset(50, 700);
            content.showText(text);
            content.endText();
        }
    }
}
