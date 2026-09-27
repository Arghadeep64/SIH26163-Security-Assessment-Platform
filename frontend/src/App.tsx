import React, { useState, useEffect } from 'react';
import { Sidebar, NavTab } from './components/common/Sidebar';
import { Topbar } from './components/common/Topbar';
import { SecurityNotice } from './components/common/SecurityNotice';

import { DashboardPage } from './pages/DashboardPage';
import { WorldMonitorPage } from './pages/WorldMonitorPage';
import { NewAssessmentPage } from './pages/NewAssessmentPage';
import { AssessmentsListPage } from './pages/AssessmentsListPage';
import { AssessmentDetailPage } from './pages/AssessmentDetailPage';
import { FindingsPage } from './pages/FindingsPage';
import { SecurityChecksPage } from './pages/SecurityChecksPage';
import { ReportsPage } from './pages/ReportsPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { SettingsPage } from './pages/SettingsPage';


import api from './services/api';
import './App.css';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [selectedAssessmentId, setSelectedAssessmentId] = useState<number | null>(null);
  const [dbConnected, setDbConnected] = useState<boolean>(false);
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const checkDbStatus = async () => {
    try {
      const res = await api.getDatabaseHealth();
      setDbConnected(res.database === 'connected');
    } catch {
      setDbConnected(false);
    }
  };

  useEffect(() => {
    checkDbStatus();
    const interval = setInterval(checkDbStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectTab = (tab: NavTab) => {
    setCurrentTab(tab);
    if (tab !== 'assessments') {
      setSelectedAssessmentId(null);
    }
  };

  const handleAssessmentCreated = (assessmentId: number) => {
    setSelectedAssessmentId(assessmentId);
    setCurrentTab('assessments');
  };

  const handleSelectAssessment = (id: number) => {
    setSelectedAssessmentId(id);
    setCurrentTab('assessments');
  };

  const getPageTitle = (): string => {
    if (currentTab === 'dashboard') return 'Security Operations Center Dashboard';
    if (currentTab === 'world-monitor') return 'World Monitor Security Assessment';
    if (currentTab === 'new-assessment') return 'Initiate New Security Assessment';
    if (currentTab === 'assessments') {
      return selectedAssessmentId
        ? `Assessment Session #${selectedAssessmentId}`
        : 'Assessment Audit History';
    }
    if (currentTab === 'findings') return 'Vulnerability Findings Registry';
    if (currentTab === 'checks') return 'Security Checks & Controls Matrix';
    if (currentTab === 'reports') return 'Security Assessment Reports';
    if (currentTab === 'methodology') return 'Defensive Assessment Methodology';
    if (currentTab === 'settings') return 'System Settings & Connectivity';
    return 'Security Assessment Platform';
  };

  const renderContent = () => {
    switch (currentTab) {
      case 'dashboard':
        return (
          <DashboardPage
            key={refreshKey}
            onNavigateWorldMonitor={() => setCurrentTab('world-monitor')}
            onNavigateNewAssessment={() => setCurrentTab('new-assessment')}
            onNavigateAssessmentDetail={(id) => handleSelectAssessment(id)}
            onNavigateAssessmentsList={() => setCurrentTab('assessments')}
            onNavigateFindings={() => setCurrentTab('findings')}
            onNavigateChecks={() => setCurrentTab('checks')}
            onNavigateReports={() => setCurrentTab('reports')}
          />
        );
      case 'world-monitor':
        return (
          <WorldMonitorPage
            key={refreshKey}
            onNavigateNewAssessment={() => setCurrentTab('new-assessment')}
            onNavigateAssessmentDetail={(id) => handleSelectAssessment(id)}
            onNavigateReports={() => setCurrentTab('reports')}
          />
        );
      case 'new-assessment':
        return (
          <NewAssessmentPage
            onAssessmentCreated={handleAssessmentCreated}
            onCancel={() => setCurrentTab('dashboard')}
          />
        );

      case 'assessments':
        if (selectedAssessmentId) {
          return (
            <AssessmentDetailPage
              key={`${selectedAssessmentId}-${refreshKey}`}
              assessmentId={selectedAssessmentId}
              onBack={() => setSelectedAssessmentId(null)}
            />
          );
        }
        return (
          <AssessmentsListPage
            key={refreshKey}
            onSelectAssessment={handleSelectAssessment}
            onNavigateNewAssessment={() => setCurrentTab('new-assessment')}
          />
        );
      case 'findings':
        return <FindingsPage key={refreshKey} />;
      case 'checks':
        return <SecurityChecksPage />;
      case 'reports':
        return <ReportsPage />;
      case 'methodology':
        return <MethodologyPage />;
      case 'settings':
        return <SettingsPage key={refreshKey} />;
      default:
        return (
          <DashboardPage
            onNavigateWorldMonitor={() => setCurrentTab('world-monitor')}
            onNavigateNewAssessment={() => setCurrentTab('new-assessment')}
            onNavigateAssessmentDetail={(id) => handleSelectAssessment(id)}
            onNavigateAssessmentsList={() => setCurrentTab('assessments')}
            onNavigateFindings={() => setCurrentTab('findings')}
            onNavigateChecks={() => setCurrentTab('checks')}
            onNavigateReports={() => setCurrentTab('reports')}
          />
        );
    }
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <Sidebar currentTab={currentTab} onSelectTab={handleSelectTab} />

      {/* Main Content Viewport */}
      <div className="main-wrapper">
        {/* Topbar */}
        <Topbar
          pageTitle={getPageTitle()}
          dbConnected={dbConnected}
          onRefresh={() => {
            checkDbStatus();
            setRefreshKey((k) => k + 1);
          }}
        />

        {/* Persistent Security Notice Banner */}
        <SecurityNotice />

        {/* Active Page View */}
        <main style={{ flex: 1 }}>{renderContent()}</main>
      </div>
    </div>
  );
};

export default App;
