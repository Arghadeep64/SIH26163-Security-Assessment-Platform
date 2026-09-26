import React from 'react';
import { SeverityLevel } from '../../types/api';

interface SeverityBadgeProps {
  severity?: SeverityLevel | string | null;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  const sev = (severity || 'INFO').toUpperCase();

  let badgeClass = 'badge-info';
  if (sev === 'CRITICAL') badgeClass = 'badge-critical';
  else if (sev === 'HIGH') badgeClass = 'badge-high';
  else if (sev === 'MEDIUM') badgeClass = 'badge-medium';
  else if (sev === 'LOW') badgeClass = 'badge-low';

  return <span className={`badge ${badgeClass}`}>{sev}</span>;
};
