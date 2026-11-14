package com.prowin.versions;

import com.prowin.common.ApiException;
import org.apache.poi.xslf.usermodel.XMLSlideShow;
import org.apache.poi.xslf.usermodel.XSLFSlide;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

@Component
public class PptxMerger {

    public record MergeResult(int slideCount) {
    }

    /** 소스 중 깨진 파일은 건너뛰고 나머지로 계속 병합한다. 복사된 슬라이드가 하나도 없으면 실패. */
    public MergeResult merge(List<Path> sourceFiles, Path outputFile) {
        try (XMLSlideShow target = new XMLSlideShow()) {
            int count = 0;
            for (Path src : sourceFiles) {
                try (InputStream in = Files.newInputStream(src); XMLSlideShow source = new XMLSlideShow(in)) {
                    for (XSLFSlide slide : source.getSlides()) {
                        target.createSlide().importContent(slide);
                        count++;
                    }
                } catch (IOException | RuntimeException e) {
                    // 이 파일만 건너뛰고 계속 진행
                }
            }
            if (count == 0) throw new ApiException("병합할 수 있는 슬라이드가 없습니다");
            try (OutputStream out = Files.newOutputStream(outputFile)) {
                target.write(out);
            }
            return new MergeResult(count);
        } catch (ApiException e) {
            throw e;
        } catch (IOException e) {
            throw new ApiException("합본 파일을 생성하지 못했습니다: " + e.getMessage());
        }
    }
}
