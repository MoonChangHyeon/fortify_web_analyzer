// /src/main/java/com/fortify/analyzer/controller/SearchController.java
package com.fortify.analyzer.controller;

import com.fortify.analyzer.entity.Rule;
import com.fortify.analyzer.service.SearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;
import java.util.Optional;

@Controller
public class SearchController {

    @Autowired
    private SearchService searchService;

    @GetMapping("/")
    public String indexPage(
            @RequestParam(name = "keyword", required = false) String keyword,
            @RequestParam(name = "ruleId", required = false) Long ruleId,
            Model model) {

        // 1. ruleId 파라미터가 있으면, 상세 보기 로직 수행
        if (ruleId != null) {
            Optional<Rule> ruleOptional = searchService.getRuleDetails(ruleId);
            if (ruleOptional.isPresent()) {
                model.addAttribute("selectedRule", ruleOptional.get());
                model.addAttribute("mappings", ruleOptional.get().getMappings());
            }
        } 
        // 2. keyword 파라미터가 있으면, 검색 로직 수행
        else if (keyword != null && !keyword.trim().isEmpty()) {
            List<Rule> foundRules = searchService.searchRulesByName(keyword);
            model.addAttribute("foundRules", foundRules);
            model.addAttribute("searchedTerm", keyword);
        }

        // 3. 아무 파라미터도 없으면 그냥 빈 페이지를 보여줌
        return "index"; // templates/index.html 파일을 렌더링
    }
}