import React from 'react';
import { CheckExecutionStatus, AssessmentStatus, FindingLifecycleStatus } from '../../types/api';

interface StatusBadgeProps {
  status: CheckExecutionStatus | AssessmentStatus | FindingLifecycleStatus | string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const s = (status || '').toUpperCase();

  let badgeClass = 'badge-info';
  if (s === 'PASS' || s === 'COMPLETED' || s === 'REMEDIATED') {
    badgeClass = 'badge-pass';
  } else if (s === 'FAIL' || s === 'FAILED' || s === 'ERROR' || s === 'OPEN') {
    badgeClass = 'badge-fail';
  } else if (s === 'MANUAL' || s === 'MANUAL_VERIFICATION' || s === 'SOURCE_REVIEW') {
    badgeClass = 'badge-manual';
  } else if (s === 'RUNNING' || s === 'QUEUED') {
    badgeClass = 'badge-running';
  } else if (s === 'CONFIRMED') {
    badgeClass = 'badge-high';
  } else if (s === 'ENVIRONMENT_OBSERVATION' || s === 'INFORMATIONAL') {
    badgeClass = 'badge-info';
  }

  return <span className={`badge ${badgeClass}`}>{s.replace(/_/g, ' ')}</span>;
};
