package com.fortify.analyzer.controller;

import com.fortify.analyzer.entity.Rule;
import com.fortify.analyzer.service.SearchService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;
import java.util.Optional;

@Controller
@RequiredArgsConstructor
public class SearchController {

    private final SearchService searchService;

    @GetMapping("/")
    public String searchPage(
            @RequestParam(name = "keyword", required = false) String keyword,
            @RequestParam(name = "ruleId", required = false) Long ruleId,
            Model model) {

        // 1. ruleId 파라미터가 있으면, 상세 보기 로직 수행
        if (ruleId != null) {
            Optional<Rule> ruleOptional = searchService.getRuleDetails(ruleId);
            if (ruleOptional.isPresent()) {
                model.addAttribute("selectedRule", ruleOptional.get());
                // 상세보기를 할 때도, 원래의 검색어와 결과 목록을 유지하기 위해 다시 전달
                if (keyword != null) {
                    List<Rule> foundRules = searchService.searchRulesByName(keyword);
                    model.addAttribute("foundRules", foundRules);
                    model.addAttribute("searchKeyword", keyword);
                }
            }
        } 
        // 2. keyword 파라미터가 있으면, 검색 로직 수행
        else if (keyword != null && !keyword.trim().isEmpty()) {
            List<Rule> foundRules = searchService.searchRulesByName(keyword);
            model.addAttribute("foundRules", foundRules);
            model.addAttribute("searchKeyword", keyword);
        }

        // 3. 아무 파라미터도 없으면 그냥 빈 페이지를 보여줌
        return "index";
    }
}