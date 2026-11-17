package com.prowin.versions;

import com.prowin.common.ApiException;
import org.apache.poi.sl.usermodel.PlaceableShape;
import org.apache.poi.xslf.usermodel.*;
import org.springframework.stereotype.Component;

import java.awt.Dimension;
import java.awt.geom.Rectangle2D;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

@Component
public class PptxMerger {

    /** skippedFiles: 열지 못했거나 깨져서 병합에서 빠진 파일의 "파일명: 사유" 목록. */
    public record MergeResult(int slideCount, List<String> skippedFiles) {
    }

    /**
     * 첫 소스 파일을 기준 문서로 삼아 마스터·테마·배경·페이지 크기를 그대로 유지하고,
     * 이후 소스는 같은 이름/유형의 레이아웃에 맞춰 슬라이드를 추가한다.
     * 페이지 크기가 다른 소스는 잘리지 않도록 기준 문서 크기에 맞춰 축소·중앙 배치한다.
     */
    public MergeResult merge(List<Path> sourceFiles, Path outputFile) {
        List<String> skipped = new ArrayList<>();
        XMLSlideShow target = null;
        try {
            int count = 0;
            for (Path src : sourceFiles) {
                if (target == null) {
                    try (InputStream in = Files.newInputStream(src)) {
                        target = new XMLSlideShow(in);
                        count += target.getSlides().size();
                    } catch (IOException | RuntimeException e) {
                        skipped.add(src.getFileName() + ": " + causeMessage(e));
                    }
                    continue;
                }
                try (InputStream in = Files.newInputStream(src); XMLSlideShow source = new XMLSlideShow(in)) {
                    double scale = pageScale(source, target);
                    for (XSLFSlide slide : source.getSlides()) {
                        XSLFSlideLayout layout = matchLayout(target, slide);
                        XSLFSlide newSlide = layout != null ? target.createSlide(layout) : target.createSlide();
                        newSlide.importContent(slide);
                        if (scale != 1.0) rescaleShapes(newSlide, source.getPageSize(), target.getPageSize(), scale);
                        sanitizeEmptyRuns(newSlide);
                        count++;
                    }
                } catch (IOException | RuntimeException e) {
                    skipped.add(src.getFileName() + ": " + causeMessage(e));
                }
            }
            if (target == null || count == 0) throw new ApiException("병합할 수 있는 슬라이드가 없습니다");
            try (OutputStream out = Files.newOutputStream(outputFile)) {
                target.write(out);
            }
            return new MergeResult(count, skipped);
        } catch (ApiException e) {
            throw e;
        } catch (IOException e) {
            throw new ApiException("합본 파일을 생성하지 못했습니다: " + e.getMessage());
        } finally {
            if (target != null) {
                try {
                    target.close();
                } catch (IOException ignored) {
                    // 쓰기 완료 후 닫기 실패는 결과물에 영향 없음
                }
            }
        }
    }

    private String causeMessage(Exception e) {
        String m = e.getMessage();
        return m == null || m.isBlank() ? e.getClass().getSimpleName() : m;
    }

    /** 소스 슬라이드와 같은 이름의 레이아웃을 기준 문서에서 찾고, 없으면 같은 유형의 레이아웃으로 대신한다. */
    private XSLFSlideLayout matchLayout(XMLSlideShow target, XSLFSlide sourceSlide) {
        XSLFSlideLayout srcLayout = sourceSlide.getSlideLayout();
        if (srcLayout == null) return null;
        String name = srcLayout.getName();
        if (name != null && !name.isBlank()) {
            XSLFSlideLayout byName = target.findLayout(name);
            if (byName != null) return byName;
        }
        SlideLayout type = srcLayout.getType();
        if (type != null) {
            for (XSLFSlideMaster master : target.getSlideMasters()) {
                for (XSLFSlideLayout layout : master.getSlideLayouts()) {
                    if (layout.getType() == type) return layout;
                }
            }
        }
        return null;
    }

    private double pageScale(XMLSlideShow source, XMLSlideShow target) {
        Dimension s = source.getPageSize();
        Dimension t = target.getPageSize();
        if (s.equals(t)) return 1.0;
        double sx = t.getWidth() / s.getWidth();
        double sy = t.getHeight() / s.getHeight();
        return Math.min(sx, sy);
    }

    /** 원본보다 작은 대상 페이지에 맞춰 도형을 축소하고 가운데로 옮겨 잘림을 막는다. */
    private void rescaleShapes(XSLFSlide slide, Dimension sourceSize, Dimension targetSize, double scale) {
        double offsetX = (targetSize.getWidth() - sourceSize.getWidth() * scale) / 2;
        double offsetY = (targetSize.getHeight() - sourceSize.getHeight() * scale) / 2;
        for (XSLFShape shape : slide.getShapes()) {
            if (!(shape instanceof PlaceableShape<?, ?> placeable)) continue;
            Rectangle2D a = placeable.getAnchor();
            placeable.setAnchor(new Rectangle2D.Double(
                    a.getX() * scale + offsetX, a.getY() * scale + offsetY,
                    a.getWidth() * scale, a.getHeight() * scale));
        }
    }

    /** importContent가 만드는 a:t 없는 빈 런을 채워 PowerPoint 복구 메시지를 막는다. */
    private void sanitizeEmptyRuns(XSLFSlide slide) {
        for (XSLFShape shape : slide.getShapes()) sanitizeShape(shape);
    }

    private void sanitizeShape(XSLFShape shape) {
        if (shape instanceof XSLFTextShape textShape) {
            for (XSLFTextParagraph para : textShape.getTextParagraphs()) {
                for (XSLFTextRun run : para.getTextRuns()) {
                    if (run.getRawText() == null) run.setText("");
                }
            }
        } else if (shape instanceof XSLFTable table) {
            for (XSLFTableRow row : table.getRows()) {
                for (XSLFTableCell cell : row.getCells()) sanitizeShape(cell);
            }
        } else if (shape instanceof XSLFGroupShape group) {
            for (XSLFShape child : group.getShapes()) sanitizeShape(child);
        }
    }
}
