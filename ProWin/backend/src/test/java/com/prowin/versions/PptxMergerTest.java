package com.prowin.versions;

import com.prowin.common.ApiException;
import org.apache.poi.xslf.usermodel.XMLSlideShow;
import org.apache.poi.xslf.usermodel.XSLFSlide;
import org.apache.poi.xslf.usermodel.XSLFTextBox;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.awt.Dimension;
import java.awt.geom.Rectangle2D;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class PptxMergerTest {

    private static final Path FIXTURE_A = Path.of("src/test/resources/fixtures/sample-a.pptx");
    private static final Path FIXTURE_B = Path.of("src/test/resources/fixtures/sample-b.pptx");

    private final PptxMerger merger = new PptxMerger();

    @Test
    void mergesTwoValidFiles_usingFirstSourceAsBase(@TempDir Path tempDir) throws Exception {
        Path out = tempDir.resolve("merged.pptx");

        PptxMerger.MergeResult result = merger.merge(List.of(FIXTURE_A, FIXTURE_B), out);

        assertThat(result.slideCount()).isEqualTo(4);
        assertThat(result.skippedFiles()).isEmpty();

        try (InputStream in = Files.newInputStream(out); XMLSlideShow merged = new XMLSlideShow(in);
             InputStream baseIn = Files.newInputStream(FIXTURE_A); XMLSlideShow base = new XMLSlideShow(baseIn)) {
            assertThat(merged.getSlides()).hasSize(4);
            // 기준 문서(sample-a)의 페이지 크기를 그대로 유지한다
            assertThat(merged.getPageSize()).isEqualTo(base.getPageSize());
            for (XSLFSlide slide : merged.getSlides()) {
                assertThat(slide.getSlideLayout()).isNotNull();
            }
        }
    }

    @Test
    void skipsCorruptSource_andReportsIt(@TempDir Path tempDir) throws Exception {
        Path corrupt = tempDir.resolve("corrupt.pptx");
        Files.writeString(corrupt, "not a real pptx file");
        Path out = tempDir.resolve("merged.pptx");

        PptxMerger.MergeResult result = merger.merge(List.of(FIXTURE_A, corrupt, FIXTURE_B), out);

        assertThat(result.slideCount()).isEqualTo(4);
        assertThat(result.skippedFiles()).hasSize(1);
        assertThat(result.skippedFiles().get(0)).contains("corrupt.pptx");
    }

    @Test
    void allSourcesCorrupt_throwsApiException(@TempDir Path tempDir) throws Exception {
        Path corrupt = tempDir.resolve("corrupt.pptx");
        Files.writeString(corrupt, "not a real pptx file");
        Path out = tempDir.resolve("merged.pptx");

        assertThatThrownBy(() -> merger.merge(List.of(corrupt), out))
                .isInstanceOf(ApiException.class);
    }

    @Test
    void rescalesWiderSource_soNothingIsClippedOffTheRightEdge(@TempDir Path tempDir) throws Exception {
        // 기준 문서(sample-a, 720x540pt 4:3)보다 넓은 16:9(960x540pt) 소스를 두 번째로 병합하면
        // 도형이 잘리지 않도록 축소·중앙 배치되어야 한다
        Path widerSource = tempDir.resolve("wider.pptx");
        Dimension widerSize = new Dimension(960, 540);
        try (XMLSlideShow ppt = new XMLSlideShow()) {
            ppt.setPageSize(widerSize);
            XSLFSlide slide = ppt.createSlide();
            XSLFTextBox box = slide.createTextBox();
            box.setAnchor(new Rectangle2D.Double(850, 0, 100, 50)); // 오른쪽 끝 근처(960pt 폭 기준)
            box.setText("오른쪽 끝 텍스트");
            try (OutputStream out = Files.newOutputStream(widerSource)) {
                ppt.write(out);
            }
        }

        Path out = tempDir.resolve("merged.pptx");
        PptxMerger.MergeResult result = merger.merge(List.of(FIXTURE_A, widerSource), out);
        assertThat(result.skippedFiles()).isEmpty();

        try (InputStream in = Files.newInputStream(out); XMLSlideShow merged = new XMLSlideShow(in)) {
            Dimension targetSize = merged.getPageSize();
            XSLFSlide lastSlide = merged.getSlides().get(merged.getSlides().size() - 1);
            XSLFTextBox rescaled = (XSLFTextBox) lastSlide.getShapes().stream()
                    .filter(s -> s instanceof XSLFTextBox).findFirst().orElseThrow();
            Rectangle2D anchor = rescaled.getAnchor();
            assertThat(anchor.getMaxX()).isLessThanOrEqualTo(targetSize.getWidth() + 0.01);
        }
    }
}
