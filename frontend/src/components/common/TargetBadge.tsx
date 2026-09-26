import React from 'react';
import { TargetType } from '../../types/api';

interface TargetBadgeProps {
  targetType: TargetType | string;
}

export const TargetBadge: React.FC<TargetBadgeProps> = ({ targetType }) => {
  const type = (targetType || 'LOCAL').toUpperCase();

  let style: React.CSSProperties = {
    background: 'rgba(6, 182, 212, 0.15)',
    color: '#38bdf8',
    border: '1px solid rgba(6, 182, 212, 0.3)',
    borderRadius: '4px',
    padding: '0.15rem 0.5rem',
    fontSize: '0.72rem',
    fontFamily: 'var(--font-mono)',
    fontWeight: 600,
    textTransform: 'uppercase',
  };

  if (type === 'DEMO') {
    style = {
      background: 'rgba(245, 158, 11, 0.15)',
      color: '#fbbf24',
      border: '1px solid rgba(245, 158, 11, 0.35)',
      borderRadius: '4px',
      padding: '0.15rem 0.5rem',
      fontSize: '0.72rem',
      fontFamily: 'var(--font-mono)',
      fontWeight: 600,
      textTransform: 'uppercase',
    };
  }

  return <span style={style}>{type === 'DEMO' ? 'CONTROLLED DEMO' : type}</span>;
};
