// /src/main/java/com/fortify/analyzer/repository/RuleRepository.java
package com.fortify.analyzer.repository;

import com.fortify.analyzer.entity.Rule;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RuleRepository extends JpaRepository<Rule, Long> {
    // 이 인터페이스는 비어있어도 JpaRepository의 기본 기능을 모두 상속받습니다.
}