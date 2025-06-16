package com.fortify.analyzer.controller;

import com.fortify.analyzer.dto.RuleDto;
import com.fortify.analyzer.dto.RulePackInfoDto;
import com.fortify.analyzer.entity.ExternalMapping;
import com.fortify.analyzer.entity.Rule;
import com.fortify.analyzer.repository.RulePackRepository;
import com.fortify.analyzer.service.SearchService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.stream.Collectors;

/**
 * JSON 기반 REST API를 제공하는 컨트롤러입니다.
 */
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class ApiController {

    private final RulePackRepository rulePackRepository;
    private final SearchService searchService;

    /**
     * 모든 룰팩 정보를 최신 버전 순서로 반환합니다.
     */
    @GetMapping("/rulepacks")
    public List<RulePackInfoDto> listRulePacks() {
        return rulePackRepository
                .findAll(Sort.by(Sort.Direction.DESC, "packVersion"))
                .stream()
                .map(pack -> new RulePackInfoDto(
                        pack.getId(),
                        pack.getPackName(),
                        pack.getPackVersion(),
                        pack.getLocation()))
                .toList();
    }

    /**
     * 키워드로 룰을 검색합니다.
     */
    @GetMapping("/rules/search")
    public List<RuleDto> searchRules(@RequestParam("keyword") String keyword) {
        return searchService.searchRulesByName(keyword)
                .stream()
                .map(this::convertRuleToDto)
                .toList();
    }

    /**
     * 특정 ID의 룰 상세 정보를 반환합니다.
     */
    @GetMapping("/rules/{id}")
    public RuleDto ruleDetails(@PathVariable Long id) {
        return searchService.getRuleDetails(id)
                .map(this::convertRuleToDto)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    }

    private RuleDto convertRuleToDto(Rule rule) {
        List<String> mappings = rule.getMappings().stream()
                .map(ExternalMapping::getStandardInfo)
                .collect(Collectors.toList());
        return new RuleDto(
                rule.getId(),
                rule.getRuleName(),
                rule.getRulePack().getId(),
                rule.getRulePack().getPackName(),
                mappings);
    }
}
