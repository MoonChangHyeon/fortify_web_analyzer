// /src/main/java/com/fortify/analyzer/service/SearchService.java
package com.fortify.analyzer.service;

import com.fortify.analyzer.entity.Rule;
import com.fortify.analyzer.repository.RuleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

@Service
public class SearchService {

    @Autowired
    private RuleRepository ruleRepository;

    // 키워드로 규칙 목록 검색
    public List<Rule> searchRulesByName(String keyword) {
        return ruleRepository.findByRuleNameContaining(keyword);
    }

    // ID로 특정 규칙의 상세 정보 가져오기
    public Optional<Rule> getRuleDetails(Long id) {
        return ruleRepository.findById(id);
    }
}