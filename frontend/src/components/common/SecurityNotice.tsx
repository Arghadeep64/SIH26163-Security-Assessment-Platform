import React from 'react';
import { ShieldAlert } from 'lucide-react';

export const SecurityNotice: React.FC = () => {
  return (
    <div className="security-notice-banner">
      <div className="security-notice-content">
        <ShieldAlert size={16} />
        <span className="security-notice-badge">Authorized Security Testing Only</span>
        <span>
          This platform is designed for authorized/local security assessment. Production systems
          must not be scanned without explicit authorization.
        </span>
      </div>
    </div>
  );
};
