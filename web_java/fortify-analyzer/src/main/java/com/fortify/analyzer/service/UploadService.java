// /src/main/java/com/fortify/analyzer/service/UploadService.java
package com.fortify.analyzer.service;

import com.fortify.analyzer.entity.ExternalMapping;
import com.fortify.analyzer.entity.Rule;
import com.fortify.analyzer.entity.RulePack;
import com.fortify.analyzer.repository.RulePackRepository;
import com.fortify.analyzer.repository.RuleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.InputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

@Service
public class UploadService {

    @Autowired
    private LogService logService;
    
    @Autowired
    private RulePackRepository rulePackRepository;

    @Autowired
    private RuleRepository ruleRepository;

    // @Transactional 어노테이션은 그대로 유지합니다. 
    // try-catch로 감싸더라도, 예외 발생 시 롤백 정책은 그대로 적용됩니다.
    @Transactional
    public String processAndSaveFile(MultipartFile file) {
        String location = file.getOriginalFilename();
        
        try {
            if (rulePackRepository.findByLocation(location).isPresent()) {
                String warningMessage = "경고: '" + location + "' 파일은 이미 DB에 존재하므로 건너뜁니다.";
                // '건너뜀' 상태도 로그로 기록합니다.
                logService.log("Upload", warningMessage);
                return warningMessage;
            }

            InputStream inputStream = file.getInputStream();
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(inputStream);
            Element root = doc.getDocumentElement();

            NodeList packInfoNodes = root.getElementsByTagName("PackInfo");
            if (packInfoNodes.getLength() == 0) {
                throw new Exception("파일 '" + location + "'에서 <PackInfo>를 찾을 수 없습니다.");
            }
            Element packInfoElement = (Element) packInfoNodes.item(0);
            String packName = packInfoElement.getElementsByTagName("Name").item(0).getTextContent();
            String packId = packInfoElement.getElementsByTagName("PackID").item(0).getTextContent();
            String packVersion = packInfoElement.getElementsByTagName("Version").item(0).getTextContent();

            RulePack newRulePack = new RulePack();
            newRulePack.setPackName(packName);
            newRulePack.setPackId(packId);
            newRulePack.setPackVersion(packVersion);
            newRulePack.setLocation(location);
            rulePackRepository.save(newRulePack);

            Map<String, Rule> ruleCache = new HashMap<>();
            Set<String> addedMappings = new HashSet<>();
            NodeList mappingNodes = root.getElementsByTagName("Mapping");

            for (int i = 0; i < mappingNodes.getLength(); i++) {
                Element mappingElement = (Element) mappingNodes.item(i);
                String ruleName = mappingElement.getElementsByTagName("InternalCategory").item(0).getTextContent();
                String standardInfo = mappingElement.getElementsByTagName("ExternalCategory").item(0).getTextContent();

                String mappingKey = ruleName + "::" + standardInfo;
                if (addedMappings.contains(mappingKey)) continue;

                Rule currentRule = ruleCache.computeIfAbsent(ruleName, k -> {
                    Rule newRule = new Rule();
                    newRule.setRuleName(k);
                    newRule.setRulePack(newRulePack);
                    return ruleRepository.save(newRule);
                });
                
                ExternalMapping newMapping = new ExternalMapping();
                newMapping.setStandardInfo(standardInfo);
                newMapping.setRule(currentRule);
                currentRule.getMappings().add(newMapping);
                addedMappings.add(mappingKey);
            }
            ruleRepository.saveAll(ruleCache.values());

            String successMessage = "✅ (처리 완료) '" + location + "' 파일의 룰팩과 규칙들을 DB에 새로 추가했습니다.";
            // 성공 시 로그를 기록합니다.
            logService.log("Upload", successMessage);
            return successMessage;

        } catch (Exception e) {
            String errorMessage = "❌ (처리 실패) '" + location + "' 파일 처리 중 오류 발생.";
            // 실패 시 에러 로그를 상세히 기록합니다.
            logService.logError("Upload", errorMessage, e);
            // 컨트롤러로 예외를 다시 던져 사용자에게 에러를 알릴 수 있습니다.
            // 여기서는 적절한 메시지를 반환하도록 처리합니다.
            return errorMessage + " 자세한 내용은 시스템 로그를 확인하세요.";
        }
    }
}