package com.prowin.versions;

import org.apache.poi.xslf.usermodel.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.awt.geom.Rectangle2D;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class PptxExtractorTest {

    private static final Path FIXTURE_A = Path.of("src/test/resources/fixtures/sample-a.pptx");

    private final PptxExtractor extractor = new PptxExtractor();

    @Test
    void extractsTitlePlaceholderAndBullets() {
        List<PptxExtractor.SlideContent> slides = extractor.extract(FIXTURE_A);

        assertThat(slides).hasSize(2);
        assertThat(slides.get(0).title()).isEqualTo("차세대 시스템 목표 아키텍처");
        assertThat(slides.get(0).bullets()).containsExactly("기간계 모놀리식 분리", "MSA 전환 1단계");
        assertThat(slides.get(0).textFound()).isTrue();
    }

    @Test
    void corruptFileReturnsEmptyList(@TempDir Path tempDir) throws IOException {
        Path broken = tempDir.resolve("broken.pptx");
        Files.writeString(broken, "이건 pptx가 아닙니다");

        assertThat(extractor.extract(broken)).isEmpty();
    }

    @Test
    void collectsTextFromGroupsAndTables(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("group-table.pptx");
        try (XMLSlideShow ppt = new XMLSlideShow()) {
            XSLFSlide slide = ppt.createSlide();

            XSLFGroupShape group = slide.createGroup();
            group.setAnchor(new Rectangle2D.Double(0, 0, 100, 100));
            group.setInteriorAnchor(new Rectangle2D.Double(0, 0, 100, 100));
            XSLFTextBox groupText = group.createTextBox();
            groupText.setAnchor(new Rectangle2D.Double(0, 0, 100, 50));
            groupText.setText("그룹 안의 텍스트");

            XSLFTable table = slide.createTable();
            table.setAnchor(new Rectangle2D.Double(0, 150, 300, 100));
            XSLFTableRow row = table.addRow();
            row.addCell().setText("표 셀 내용");

            XSLFTextBox title = slide.createTextBox();
            title.setAnchor(new Rectangle2D.Double(0, 260, 300, 50));
            title.setText("제목 없는 슬라이드의 첫 도형");

            try (OutputStream out = Files.newOutputStream(file)) {
                ppt.write(out);
            }
        }

        List<PptxExtractor.SlideContent> slides = extractor.extract(file);
        assertThat(slides).hasSize(1);
        PptxExtractor.SlideContent slide = slides.get(0);
        assertThat(slide.bullets()).contains("그룹 안의 텍스트", "표 셀 내용");
    }

    @Test
    void emptyTextSlideReportsTextNotFound(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("blank.pptx");
        try (XMLSlideShow ppt = new XMLSlideShow()) {
            ppt.createSlide();
            try (OutputStream out = Files.newOutputStream(file)) {
                ppt.write(out);
            }
        }

        List<PptxExtractor.SlideContent> slides = extractor.extract(file);
        assertThat(slides).hasSize(1);
        assertThat(slides.get(0).textFound()).isFalse();
    }
}
