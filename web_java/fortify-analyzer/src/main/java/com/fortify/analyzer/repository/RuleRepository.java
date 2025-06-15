package com.fortify.analyzer.repository;

import com.fortify.analyzer.entity.Rule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional; // ✨ 이 줄이 추가되었습니다!

@Repository
public interface RuleRepository extends JpaRepository<Rule, Long> {

    List<Rule> findByRuleNameContainingIgnoreCase(String keyword);

    Optional<Rule> findByRuleName(String ruleName);
}