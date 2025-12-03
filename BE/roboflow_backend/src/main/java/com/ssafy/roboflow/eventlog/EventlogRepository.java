// src/main/java/com/ssafy/roboflow/eventlog/EventlogRepository.java
package com.ssafy.roboflow.eventlog;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

@Repository
public interface EventlogRepository extends JpaRepository<EventlogEntity, Long>,
        JpaSpecificationExecutor<EventlogEntity> {
}
