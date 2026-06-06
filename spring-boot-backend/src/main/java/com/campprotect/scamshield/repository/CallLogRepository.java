package com.campprotect.scamshield.repository;

import com.campprotect.scamshield.model.CallLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface CallLogRepository extends JpaRepository<CallLog, Long> {
    Optional<CallLog> findByCallSid(String callSid);
}
