// /src/main/java/com/fortify/analyzer/entity/RulePack.java

package com.fortify.analyzer.entity;

import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity // 이 클래스가 데이터베이스 테이블과 매핑되는 JPA 엔티티임을 선언합니다.
@Table(name = "rule_packs") // 실제 데이터베이스에 생성될 테이블의 이름을 지정합니다.
@Getter // 각 필드의 Getter 메소드(예: getId(), getPackName())를 자동으로 생성합니다.
@Setter // 각 필드의 Setter 메소드(예: setId(...), setPackName(...))를 자동으로 생성합니다.
@NoArgsConstructor // 파라미터가 없는 기본 생성자를 자동으로 생성합니다. JPA는 이 생성자를 필요로 합니다.
public class RulePack {

    @Id // 이 필드가 테이블의 기본 키(Primary Key)임을 나타냅니다.
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 기본 키 값을 데이터베이스가 자동으로 생성(auto-increment)하도록 합니다.
    private Long id;

    @Column(nullable = false) // 'pack_name' 컬럼, null 값을 허용하지 않습니다.
    private String packName;

    @Column(nullable = false) // 'pack_id' 컬럼, null 값을 허용하지 않습니다.
    private String packId;

    @Column
    private String packVersion;

    @Column(unique = true, nullable = false, length = 1024) // 'location' 컬럼, 고유해야 하며 null 불허
    private String location;

    // '하나'의 룰팩은 '여러 개'의 룰을 가질 수 있다는 관계를 정의합니다. (One-To-Many)
    @OneToMany(mappedBy = "rulePack", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Rule> rules = new ArrayList<>();
}