import React from 'react';
import {
  LayoutDashboard,
  ShieldPlus,
  History,
  AlertTriangle,
  CheckCircle2,
  FileText,
  BookOpen,
  Settings,
  Shield,
} from 'lucide-react';

export type NavTab =
  | 'dashboard'
  | 'world-monitor'
  | 'new-assessment'
  | 'assessments'
  | 'findings'
  | 'checks'
  | 'reports'
  | 'methodology'
  | 'settings';

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab }) => {
  const navItems: { id: NavTab; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18} /> },
    { id: 'world-monitor', label: 'World Monitor', icon: <Shield size={18} color="var(--accent-cyan)" /> },
    { id: 'new-assessment', label: 'New Assessment', icon: <ShieldPlus size={18} /> },
    { id: 'assessments', label: 'Assessments', icon: <History size={18} /> },
    { id: 'findings', label: 'Findings', icon: <AlertTriangle size={18} /> },
    { id: 'checks', label: 'Security Checks', icon: <CheckCircle2 size={18} /> },
    { id: 'reports', label: 'Reports', icon: <FileText size={18} /> },
    { id: 'methodology', label: 'Methodology', icon: <BookOpen size={18} /> },
    { id: 'settings', label: 'Settings', icon: <Settings size={18} /> },
  ];


  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">
          <Shield size={22} />
        </div>
        <div>
          <div className="sidebar-brand-title">SIH26163</div>
          <div className="sidebar-brand-subtitle">Security Platform</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`nav-item ${currentTab === item.id ? 'active' : ''}`}
            onClick={() => onSelectTab(item.id)}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-title">
          <Shield size={14} color="#06b6d4" />
          <span>SIH26163</span>
        </div>
        <div className="sidebar-footer-sub">World Monitor Security Assessment</div>
      </div>
    </aside>
  );
};
