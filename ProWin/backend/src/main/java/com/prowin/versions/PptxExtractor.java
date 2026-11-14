package com.prowin.versions;

import org.apache.poi.xslf.usermodel.XMLSlideShow;
import org.apache.poi.xslf.usermodel.XSLFShape;
import org.apache.poi.xslf.usermodel.XSLFSlide;
import org.apache.poi.xslf.usermodel.XSLFTextShape;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

@Component
public class PptxExtractor {

    public record SlideContent(String title, List<String> bullets) {
    }

    /** 손상된 파일이거나 pptx가 아니면 빈 목록을 돌려준다 — 업로드/커밋 자체는 항상 성공해야 한다. */
    public List<SlideContent> extract(Path file) {
        try (InputStream in = Files.newInputStream(file); XMLSlideShow ppt = new XMLSlideShow(in)) {
            List<SlideContent> result = new ArrayList<>();
            for (XSLFSlide slide : ppt.getSlides()) {
                String title = null;
                List<String> bullets = new ArrayList<>();
                for (XSLFShape shape : slide.getShapes()) {
                    if (!(shape instanceof XSLFTextShape textShape)) continue;
                    String text = textShape.getText();
                    if (text == null || text.isBlank()) continue;
                    if (title == null) {
                        title = text.strip().lines().findFirst().orElse(text.strip());
                        continue;
                    }
                    text.lines().map(String::strip).filter(s -> !s.isBlank()).forEach(bullets::add);
                }
                result.add(new SlideContent(title, bullets));
            }
            return result;
        } catch (IOException | RuntimeException e) {
            return List.of();
        }
    }
}
