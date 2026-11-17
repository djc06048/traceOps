package com.prowin.versions;

import com.prowin.common.ApiException;
import org.apache.poi.xslf.usermodel.XMLSlideShow;
import org.apache.poi.xslf.usermodel.XSLFSlide;
import org.apache.poi.xslf.usermodel.XSLFTextBox;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import javax.imageio.ImageIO;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class PptxRendererTest {

    private static final Path FIXTURE_A = Path.of("src/test/resources/fixtures/sample-a.pptx");

    private final PptxRenderer renderer = new PptxRenderer();

    @Test
    void rendersSlideAtRequestedWidth() throws IOException {
        byte[] png = renderer.renderSlidePng(FIXTURE_A, 0, 400);

        BufferedImage img = ImageIO.read(new ByteArrayInputStream(png));
        assertThat(img.getWidth()).isEqualTo(400);
        assertThat(img.getHeight()).isGreaterThan(0);
    }

    @Test
    void invalidSlideIndexThrowsApiException() {
        assertThatThrownBy(() -> renderer.renderSlidePng(FIXTURE_A, 99, 400))
                .isInstanceOf(ApiException.class);
    }

    @Test
    void rendersSlideWithSymbolFontRunsWithoutError(@TempDir Path tempDir) throws IOException {
        Path file = tempDir.resolve("wingdings.pptx");
        try (XMLSlideShow ppt = new XMLSlideShow()) {
            XSLFSlide slide = ppt.createSlide();
            XSLFTextBox box = slide.createTextBox();
            box.setAnchor(new java.awt.geom.Rectangle2D.Double(0, 0, 300, 100));
            box.setText(" 글머리 기호");
            box.getTextParagraphs().get(0).getTextRuns().get(0).setFontFamily("Wingdings");
            try (OutputStream out = Files.newOutputStream(file)) {
                ppt.write(out);
            }
        }

        byte[] png = renderer.renderSlidePng(file, 0, 300);
        assertThat(png).isNotEmpty();
        BufferedImage img = ImageIO.read(new ByteArrayInputStream(png));
        assertThat(img.getWidth()).isEqualTo(300);
    }
}
