package com.prowin.versions;

import org.apache.poi.sl.usermodel.Placeholder;
import org.apache.poi.xslf.usermodel.*;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

@Component
public class PptxExtractor {

    private static final int BULLET_LIMIT_PER_SLIDE = 20;

    /** textFound=false면 이 슬라이드에서 글자를 하나도 읽지 못했다는 뜻이다(이미지형 슬라이드 등). */
    public record SlideContent(String title, List<String> bullets, boolean textFound) {
    }

    /** 손상된 파일이거나 pptx가 아니면 빈 목록을 돌려준다 — 업로드/커밋 자체는 항상 성공해야 한다. */
    public List<SlideContent> extract(Path file) {
        try (InputStream in = Files.newInputStream(file); XMLSlideShow ppt = new XMLSlideShow(in)) {
            List<SlideContent> result = new ArrayList<>();
            for (XSLFSlide slide : ppt.getSlides()) {
                result.add(extractSlide(slide));
            }
            return result;
        } catch (IOException | RuntimeException e) {
            return List.of();
        }
    }

    private SlideContent extractSlide(XSLFSlide slide) {
        List<XSLFShape> shapes = slide.getShapes();
        String title = findTitleFromPlaceholder(shapes);
        if (title == null) title = findTitleFromTopmostShape(shapes);

        List<String> bullets = new ArrayList<>();
        for (XSLFShape shape : shapes) collectBullets(shape, title, bullets);
        boolean textFound = title != null || !bullets.isEmpty();
        List<String> limited = bullets.size() > BULLET_LIMIT_PER_SLIDE ? bullets.subList(0, BULLET_LIMIT_PER_SLIDE) : bullets;
        return new SlideContent(title, limited, textFound);
    }

    /** 사용자 가이드의 "제목칸에 입력" 규칙과 맞추어 제목 placeholder를 우선한다. */
    private String findTitleFromPlaceholder(List<XSLFShape> shapes) {
        for (XSLFShape shape : shapes) {
            if (!(shape instanceof XSLFTextShape textShape)) continue;
            Placeholder type = textShape.getTextType();
            if (type == Placeholder.TITLE || type == Placeholder.CENTERED_TITLE) {
                String line = firstNonBlankLine(textShape.getText());
                if (line != null) return line;
            }
        }
        return null;
    }

    /** 제목 placeholder가 없는 슬라이드는 화면에서 가장 위에 있는 텍스트 도형의 첫 줄을 제목으로 쓴다. */
    private String findTitleFromTopmostShape(List<XSLFShape> shapes) {
        XSLFTextShape topmost = null;
        double topY = Double.MAX_VALUE;
        for (XSLFShape shape : shapes) {
            if (!(shape instanceof XSLFTextShape textShape)) continue;
            String text = textShape.getText();
            if (text == null || text.isBlank()) continue;
            double y = (shape instanceof XSLFSimpleShape simple) ? simple.getAnchor().getY() : Double.MAX_VALUE;
            if (y < topY) {
                topY = y;
                topmost = textShape;
            }
        }
        return topmost == null ? null : firstNonBlankLine(topmost.getText());
    }

    /** 그룹 도형과 표 안의 텍스트까지 재귀적으로 모은다. 제목으로 이미 쓴 줄은 중복 수집하지 않는다. */
    private void collectBullets(XSLFShape shape, String title, List<String> bullets) {
        if (shape instanceof XSLFTable table) {
            for (XSLFTableRow row : table.getRows()) {
                for (XSLFTableCell cell : row.getCells()) addLines(cell.getText(), title, bullets);
            }
        } else if (shape instanceof XSLFGroupShape group) {
            for (XSLFShape child : group.getShapes()) collectBullets(child, title, bullets);
        } else if (shape instanceof XSLFTextShape textShape) {
            Placeholder type = textShape.getTextType();
            if (type == Placeholder.TITLE || type == Placeholder.CENTERED_TITLE) return;
            addLines(textShape.getText(), title, bullets);
        }
    }

    private void addLines(String text, String title, List<String> bullets) {
        if (text == null || text.isBlank()) return;
        text.lines().map(String::strip).filter(s -> !s.isBlank() && !s.equals(title)).forEach(bullets::add);
    }

    private String firstNonBlankLine(String text) {
        if (text == null) return null;
        return text.strip().lines().map(String::strip).filter(s -> !s.isBlank()).findFirst().orElse(null);
    }
}
