package com.fortify.analyzer.controller;

import com.fortify.analyzer.service.UploadService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
public class UploadController {

    private final Logger logger = LoggerFactory.getLogger(UploadController.class);

    @Autowired
    private UploadService uploadService;

    @GetMapping("/upload")
    public String uploadPage() {
        return "upload"; // upload.html 템플릿을 보여줌
    }

    @PostMapping("/upload")
    public String handleFileUpload(@RequestParam("xml_files") MultipartFile[] files,
                                   RedirectAttributes redirectAttributes) {
        
        logger.info("파일 업로드 요청을 받았습니다. 총 파일 수: {}", files.length);

        int processedCount = 0;
        for (MultipartFile file : files) {
            if (file.isEmpty() || !file.getOriginalFilename().endsWith("externalmetadata.xml")) {
                continue;
            }
            try {
                String message = uploadService.processAndSaveFile(file);
                redirectAttributes.addFlashAttribute("message", message);
                processedCount++;
            } catch (Exception e) {
                logger.error("파일 처리 중 오류 발생: {}", file.getOriginalFilename(), e);
                redirectAttributes.addFlashAttribute("error", "오류: " + file.getOriginalFilename() + " 처리 중 문제가 발생했습니다.");
            }
        }

        if (processedCount == 0) {
            redirectAttributes.addFlashAttribute("warning", "처리할 'externalmetadata.xml' 파일을 찾지 못했습니다.");
        }

        return "redirect:/upload";
    }
}