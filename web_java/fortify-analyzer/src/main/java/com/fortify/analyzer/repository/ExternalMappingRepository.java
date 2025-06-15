package com.fortify.analyzer.repository;

import com.fortify.analyzer.entity.ExternalMapping;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ExternalMappingRepository extends JpaRepository<ExternalMapping, Long> {
    List<ExternalMapping> findByRule_RuleNameContainingIgnoreCase(String keyword);
}