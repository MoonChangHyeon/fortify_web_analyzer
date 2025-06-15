// /src/main/java/com/fortify/analyzer/repository/RuleRepository.java
package com.fortify.analyzer.repository;

import com.fortify.analyzer.entity.Rule;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List; // List import 추가

public interface RuleRepository extends JpaRepository<Rule, Long> {
    
    // ✨ 이 메소드를 추가합니다. ✨
    // Spring Data JPA가 메소드 이름을 분석하여 "ruleName에 특정 문자열이 포함된(Containing) 모든 Rule을 찾아달라"는
    // SQL 쿼리(WHERE rule_name LIKE '%keyword%')를 자동으로 생성해줍니다.
    List<Rule> findByRuleNameContaining(String keyword);
}