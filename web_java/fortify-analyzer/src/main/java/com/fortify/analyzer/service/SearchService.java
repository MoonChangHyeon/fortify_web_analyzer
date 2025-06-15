package com.fortify.analyzer.service;

import com.fortify.analyzer.entity.Rule;
import com.fortify.analyzer.repository.RuleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class SearchService {

    @Autowired
    private RuleRepository ruleRepository;

    // ✨ 중복 제거 로직이 포함된 검색 메소드
    public List<Rule> searchRulesByName(String keyword) {
        List<Rule> rawResults = ruleRepository.findByRuleNameContainingIgnoreCase(keyword);
        
        // LinkedHashMap을 사용하여 순서를 유지하면서 중복된 ruleName을 합칩니다.
        Map<String, Rule> distinctRules = new LinkedHashMap<>();
        for (Rule rule : rawResults) {
            distinctRules.putIfAbsent(rule.getRuleName(), rule);
        }
        
        return new ArrayList<>(distinctRules.values());
    }

    // ID로 특정 규칙의 상세 정보 가져오기
    public Optional<Rule> getRuleDetails(Long id) {
        return ruleRepository.findById(id);
    }
}