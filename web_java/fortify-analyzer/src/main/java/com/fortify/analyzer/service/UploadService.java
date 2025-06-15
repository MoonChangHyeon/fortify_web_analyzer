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
    private RulePackRepository rulePackRepository;

    @Autowired
    private RuleRepository ruleRepository;

    @Transactional
    public String processAndSaveFile(MultipartFile file) throws Exception {
        String location = file.getOriginalFilename();

        if (rulePackRepository.findByLocation(location).isPresent()) {
            return "경고: '" + location + "' 파일은 이미 DB에 존재하므로 건너뜁니다.";
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

        return "✅ (처리 완료) '" + location + "' 파일의 룰팩과 규칙들을 DB에 새로 추가했습니다.";
    }
}