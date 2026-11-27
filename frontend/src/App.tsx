import React from 'react';
import { Router, Routes, Route } from './router';
import AppShell from './layouts/AppShell';

import AdminIntelligencePage from './pages/AdminIntelligencePage';
import AIChatAgentPage from './pages/AIChatAgentPage';
import KnowledgeBasePage from './pages/KnowledgeBasePage';
import BusinessDataHubPage from './pages/BusinessDataHubPage';
import CustomerManagementPage from './pages/CustomerManagementPage';
import ComplaintsTicketsPage from './pages/ComplaintsTicketsPage';
import IntegrationsToolsPage from './pages/IntegrationsToolsPage';
import CloudInfrastructurePage from './pages/CloudInfrastructurePage';
import EnterpriseAdminPage from './pages/EnterpriseAdminPage';
import DesignTokenPreview from './components/DesignTokenPreview';

export const App: React.FC = () => {
  return (
    <Router>
      <AppShell>
        <Routes>
          <Route path="/" element={<AdminIntelligencePage />} />
          <Route path="/chat" element={<AIChatAgentPage />} />
          <Route path="/knowledge" element={<KnowledgeBasePage />} />
          <Route path="/data-hub" element={<BusinessDataHubPage />} />
          <Route path="/customers" element={<CustomerManagementPage />} />
          <Route path="/tickets" element={<ComplaintsTicketsPage />} />
          <Route path="/integrations" element={<IntegrationsToolsPage />} />
          <Route path="/infrastructure" element={<CloudInfrastructurePage />} />
          <Route path="/admin" element={<EnterpriseAdminPage />} />
          <Route path="/tokens" element={<DesignTokenPreview />} />
          <Route path="*" element={<AdminIntelligencePage />} />
        </Routes>
      </AppShell>
    </Router>
  );
};

export default App;
