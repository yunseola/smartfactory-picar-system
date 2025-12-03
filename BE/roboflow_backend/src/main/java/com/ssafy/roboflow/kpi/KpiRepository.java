// src/main/java/com/ssafy/roboflow/kpi/KpiRepository.java
package com.ssafy.roboflow.kpi;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface KpiRepository extends JpaRepository<KpiEntity, Long> {
}
