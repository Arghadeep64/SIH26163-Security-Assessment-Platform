import React from 'react';

interface StatCardProps {
  title: string;
  value: number | string;
  description?: string;
  icon?: React.ReactNode;
  color?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  description,
  icon,
  color,
}) => {
  return (
    <div className="stat-card">
      <div className="stat-card-title">
        <span>{title}</span>
        {icon && <span style={{ color: color || 'var(--text-muted)' }}>{icon}</span>}
      </div>
      <div className="stat-card-value" style={{ color: color || 'var(--text-bright)' }}>
        {value}
      </div>
      {description && <div className="stat-card-desc">{description}</div>}
    </div>
  );
};
