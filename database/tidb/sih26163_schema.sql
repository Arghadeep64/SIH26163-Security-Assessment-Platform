-- =============================================================================
-- SIH26163: Security Assessment of the World Monitor Application
-- Database Schema Definition (MySQL 8+ and TiDB Cloud Compatible)
-- Database Name: sih26163_db
-- =============================================================================

CREATE DATABASE IF NOT EXISTS sih26163_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sih26163_db;

-- -----------------------------------------------------------------------------
-- Table 1: assessments
-- Purpose: Stores security assessment and scanning sessions.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS assessments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    target_url VARCHAR(500) NOT NULL,
    target_type VARCHAR(50) DEFAULT 'LOCAL' COMMENT 'LOCAL, AUTHORIZED_REMOTE, DEMO',
    status VARCHAR(30) NOT NULL DEFAULT 'QUEUED' COMMENT 'QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED',
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    duration_seconds DECIMAL(10, 2) NULL,
    total_checks INT NOT NULL DEFAULT 0,
    passed_checks INT NOT NULL DEFAULT 0,
    failed_checks INT NOT NULL DEFAULT 0,
    manual_checks INT NOT NULL DEFAULT 0,
    error_checks INT NOT NULL DEFAULT 0,
    critical_findings INT NOT NULL DEFAULT 0,
    high_findings INT NOT NULL DEFAULT 0,
    medium_findings INT NOT NULL DEFAULT 0,
    low_findings INT NOT NULL DEFAULT 0,
    info_findings INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_assessments_status (status),
    INDEX idx_assessments_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 2: security_checks
-- Purpose: Stores individual security check results per assessment.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS security_checks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    assessment_id BIGINT NOT NULL,
    check_id VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(30) NOT NULL COMMENT 'PASS, FAIL, MANUAL, ERROR',
    severity VARCHAR(30) NULL COMMENT 'INFO, LOW, MEDIUM, HIGH, CRITICAL',
    description TEXT NULL,
    affected_component VARCHAR(500) NULL,
    confidence DECIMAL(5, 2) NULL,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_security_checks_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES assessments (id)
        ON DELETE CASCADE,
    INDEX idx_security_checks_assessment_id (assessment_id),
    INDEX idx_security_checks_status (status),
    INDEX idx_security_checks_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 3: findings
-- Purpose: Stores confirmed or potential security findings.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS findings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    assessment_id BIGINT NOT NULL,
    check_id BIGINT NULL,
    finding_code VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    severity VARCHAR(30) NOT NULL COMMENT 'INFO, LOW, MEDIUM, HIGH, CRITICAL',
    status VARCHAR(30) NOT NULL COMMENT 'OPEN, CONFIRMED, FALSE_POSITIVE, REMEDIATED, MANUAL_VERIFICATION',
    confidence DECIMAL(5, 2) NULL,
    cvss_score DECIMAL(3, 1) NULL,
    cvss_vector VARCHAR(255) NULL,
    description TEXT NULL,
    affected_component VARCHAR(500) NULL,
    impact TEXT NULL,
    reproduction_steps TEXT NULL,
    remediation TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_findings_finding_code UNIQUE (finding_code),
    CONSTRAINT fk_findings_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES assessments (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_findings_check
        FOREIGN KEY (check_id)
        REFERENCES security_checks (id)
        ON DELETE SET NULL,
    INDEX idx_findings_assessment_id (assessment_id),
    INDEX idx_findings_severity (severity),
    INDEX idx_findings_status (status),
    INDEX idx_findings_check_id (check_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 4: evidence
-- Purpose: Stores technical evidence supporting a check or finding.
-- Redaction: Sensitive secrets are strictly redacted before persistence.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS evidence (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    assessment_id BIGINT NOT NULL,
    check_id BIGINT NULL,
    finding_id BIGINT NULL,
    evidence_type VARCHAR(50) NOT NULL COMMENT 'HTTP_RESPONSE, HTTP_HEADER, SOURCE_CODE, CONFIGURATION, DEPENDENCY, POC_RESULT, SCREENSHOT, MANUAL',
    title VARCHAR(255) NULL,
    description TEXT NULL,
    request_data TEXT NULL,
    response_data TEXT NULL,
    source_file VARCHAR(500) NULL,
    source_line INT NULL,
    redacted BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evidence_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES assessments (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evidence_check
        FOREIGN KEY (check_id)
        REFERENCES security_checks (id)
        ON DELETE SET NULL,
    CONSTRAINT fk_evidence_finding
        FOREIGN KEY (finding_id)
        REFERENCES findings (id)
        ON DELETE SET NULL,
    INDEX idx_evidence_assessment_id (assessment_id),
    INDEX idx_evidence_finding_id (finding_id),
    INDEX idx_evidence_check_id (check_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Table 5: reports
-- Purpose: Stores metadata for generated assessment report files.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    assessment_id BIGINT NOT NULL,
    report_type VARCHAR(30) NOT NULL COMMENT 'HTML, JSON',
    file_name VARCHAR(255) NULL,
    file_path VARCHAR(500) NULL,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reports_assessment
        FOREIGN KEY (assessment_id)
        REFERENCES assessments (id)
        ON DELETE CASCADE,
    INDEX idx_reports_assessment_id (assessment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
