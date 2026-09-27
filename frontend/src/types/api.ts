/**
 * TypeScript definitions for SIH26163 Security Assessment Platform.
 * Matches backend Pydantic schemas and database models.
 */

export type TargetType = 'LOCAL' | 'DEMO' | 'AUTHORIZED_REMOTE';

export type AssessmentStatus = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export type CheckExecutionStatus = 'PASS' | 'FAIL' | 'MANUAL' | 'ERROR';

export type SeverityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type FindingLifecycleStatus =
  | 'OPEN'
  | 'CONFIRMED'
  | 'FALSE_POSITIVE'
  | 'REMEDIATED'
  | 'MANUAL_VERIFICATION'
  | 'ENVIRONMENT_OBSERVATION'
  | 'SOURCE_REVIEW'
  | 'INFORMATIONAL';

export type EvidenceType =
  | 'HTTP_RESPONSE'
  | 'HTTP_HEADER'
  | 'SOURCE_CODE'
  | 'CONFIGURATION'
  | 'DEPENDENCY'
  | 'POC_RESULT'
  | 'SCREENSHOT'
  | 'MANUAL';

export interface Assessment {
  id: number;
  target_url: string;
  target_type: TargetType;
  status: AssessmentStatus;
  started_at?: string | null;
  completed_at?: string | null;
  duration_seconds?: number | null;
  total_checks?: number;
  passed_checks?: number;
  failed_checks?: number;
  manual_checks?: number;
  error_checks?: number;
  critical_findings?: number;
  high_findings?: number;
  medium_findings?: number;
  low_findings?: number;
  info_findings?: number;
  created_at?: string | null;
}

export interface SecurityCheck {
  id: number;
  assessment_id: number;
  check_id: string;
  category: string;
  title: string;
  status: CheckExecutionStatus;
  severity?: SeverityLevel | null;
  description?: string | null;
  affected_component?: string | null;
  confidence?: number | null;
  started_at?: string | null;
  completed_at?: string | null;
}

export interface Finding {
  id: number;
  assessment_id: number;
  check_id?: number | null;
  finding_code: string;
  title: string;
  category: string;
  severity: SeverityLevel;
  status: FindingLifecycleStatus;
  confidence?: number | null;
  cvss_score?: number | null;
  cvss_vector?: string | null;
  description?: string | null;
  affected_component?: string | null;
  impact?: string | null;
  reproduction_steps?: string | null;
  remediation?: string | null;
  created_at?: string | null;
}

export interface Evidence {
  id: number;
  assessment_id: number;
  check_id?: number | null;
  finding_id?: number | null;
  evidence_type: EvidenceType;
  title?: string | null;
  description?: string | null;
  request_data?: string | null;
  response_data?: string | null;
  source_file?: string | null;
  source_line?: number | null;
  redacted: boolean;
  created_at?: string | null;
}

export interface ScanCreateRequest {
  target_url: string;
  target_type: TargetType;
}

export interface ScanCreateResponse {
  assessment_id: number;
  status: AssessmentStatus;
}

export interface DatabaseHealthResponse {
  status: string;
  database: 'connected' | 'disconnected';
}

export interface SystemHealthResponse {
  status: string;
}

export interface ServiceStatusResponse {
  project: string;
  status: string;
}

export interface CheckCatalogItem {
  id: string;
  name: string;
  category: string;
  type: 'AUTOMATED' | 'MANUAL';
  description: string;
  method: string;
  baseline: string;
}

export type ReportFormat = 'HTML' | 'PDF';

export interface Report {
  id: number;
  assessment_id: number;
  report_type: ReportFormat;
  file_name?: string | null;
  file_path?: string | null;
  generated_at?: string | null;
  created_at?: string | null;
}

export interface ReportGenerateRequest {
  report_type: ReportFormat;
}

export interface WorldMonitorOverview {
  project: string;
  primary_target: {
    name: string;
    production_url: string;
    repository_url: string;
    cloned_source_path: string;
    commit: string;
    source_present_locally: boolean;
    assessment_mode: string;
  };
  assessment_verdict: {
    statement: string;
    status: string;
    production_findings_count: number;
    controlled_demo_findings_count: number;
    environment_observations_count: number;
  };
  latest_assessment?: {
    id: number;
    target_url: string;
    target_type: TargetType;
    status: AssessmentStatus;
    total_checks: number;
    passed_checks: number;
    failed_checks: number;
    manual_checks: number;
    error_checks: number;
    duration_seconds?: number | null;
    created_at?: string | null;
  } | null;
  security_domains_assessed: Array<{
    domain: string;
    status: string;
    provider?: string;
    controls?: string;
  }>;
}

export interface WorldMonitorSourceAuditCategory {
  category: string;
  component: string;
  source_files: string[];
  verified_controls: string[];
  assessment_verdict: string;
}

export interface WorldMonitorSourceAudit {
  repository: string;
  commit: string;
  audit_categories: WorldMonitorSourceAuditCategory[];
}

