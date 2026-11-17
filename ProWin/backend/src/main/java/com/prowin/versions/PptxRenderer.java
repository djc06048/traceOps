package com.prowin.versions;

import com.prowin.common.ApiException;
import org.apache.poi.xslf.usermodel.*;
import org.springframework.stereotype.Component;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import javax.imageio.ImageIO;

@Component
public class PptxRenderer {

    /** Wingdings 등 기호 글꼴은 서버에 없으면 ♣ 같은 깨진 글자로 그려지므로 일반 글머리 기호로 바꿔 그린다. */
    private static final Set<String> SYMBOL_FONTS = Set.of("wingdings", "wingdings 2", "wingdings 3", "webdings", "symbol");
    private static final String FALLBACK_FONT = "Malgun Gothic";

    public byte[] renderSlidePng(Path file, int slideIndex, int targetWidth) {
        try (InputStream in = Files.newInputStream(file); XMLSlideShow ppt = new XMLSlideShow(in)) {
            var slides = ppt.getSlides();
            if (slideIndex < 0 || slideIndex >= slides.size()) {
                throw new ApiException("슬라이드 번호가 올바르지 않습니다: " + slideIndex);
            }
            XSLFSlide slide = slides.get(slideIndex);
            replaceSymbolFonts(slide);
            Dimension pageSize = ppt.getPageSize();
            double scale = targetWidth / pageSize.getWidth();
            int width = targetWidth;
            int height = (int) Math.round(pageSize.getHeight() * scale);
            BufferedImage img = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
            Graphics2D graphics = img.createGraphics();
            graphics.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            graphics.setColor(Color.WHITE);
            graphics.fillRect(0, 0, width, height);
            graphics.scale(scale, scale);
            slide.draw(graphics);
            graphics.dispose();
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ImageIO.write(img, "png", baos);
            return baos.toByteArray();
        } catch (ApiException e) {
            throw e;
        } catch (IOException | RuntimeException e) {
            throw new ApiException("슬라이드를 렌더링하지 못했습니다: " + e.getMessage());
        }
    }

    private void replaceSymbolFonts(XSLFSlide slide) {
        for (XSLFShape shape : slide.getShapes()) replaceSymbolFonts(shape);
    }

    private void replaceSymbolFonts(XSLFShape shape) {
        if (shape instanceof XSLFTextShape textShape) {
            for (XSLFTextParagraph para : textShape.getTextParagraphs()) {
                for (XSLFTextRun run : para.getTextRuns()) {
                    String family = run.getFontFamily();
                    if (family == null || !SYMBOL_FONTS.contains(family.trim().toLowerCase())) continue;
                    String text = run.getRawText();
                    if (text != null && !text.isBlank()) run.setText("•".repeat(text.length()));
                    run.setFontFamily(FALLBACK_FONT);
                }
            }
        } else if (shape instanceof XSLFTable table) {
            for (XSLFTableRow row : table.getRows()) {
                for (XSLFTableCell cell : row.getCells()) replaceSymbolFonts(cell);
            }
        } else if (shape instanceof XSLFGroupShape group) {
            for (XSLFShape child : group.getShapes()) replaceSymbolFonts(child);
        }
    }
}
