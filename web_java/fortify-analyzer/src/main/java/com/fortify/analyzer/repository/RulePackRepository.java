// /src/main/java/com/fortify/analyzer/repository/RulePackRepository.java
package com.fortify.analyzer.repository;

import java.util.Optional;
import com.fortify.analyzer.entity.RulePack;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RulePackRepository extends JpaRepository<RulePack, Long> {
    // 파일 경로(location)로 RulePack을 찾는 커스텀 메소드
    Optional<RulePack> findByLocation(String location);
}