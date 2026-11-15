package com.prowin.versions;

import com.prowin.common.ApiException;
import org.apache.poi.xslf.usermodel.XMLSlideShow;
import org.apache.poi.xslf.usermodel.XSLFSlide;
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
import javax.imageio.ImageIO;

@Component
public class PptxRenderer {

    public byte[] renderSlidePng(Path file, int slideIndex, int targetWidth) {
        try (InputStream in = Files.newInputStream(file); XMLSlideShow ppt = new XMLSlideShow(in)) {
            var slides = ppt.getSlides();
            if (slideIndex < 0 || slideIndex >= slides.size()) {
                throw new ApiException("슬라이드 번호가 올바르지 않습니다: " + slideIndex);
            }
            XSLFSlide slide = slides.get(slideIndex);
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
}
