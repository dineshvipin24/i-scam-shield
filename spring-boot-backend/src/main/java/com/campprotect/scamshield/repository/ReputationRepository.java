package com.campprotect.scamshield.repository;

import com.campprotect.scamshield.model.CallerReputation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface ReputationRepository extends JpaRepository<CallerReputation, Long> {
    Optional<CallerReputation> findByPhoneNumber(String phoneNumber);
}
