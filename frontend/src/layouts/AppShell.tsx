import React, { useState, useEffect, ReactNode } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import Breadcrumbs from './Breadcrumbs';
import { checkBackendHealth } from '../services/apiClient';

interface AppShellProps {
  children: ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);
  const [apiConnected, setApiConnected] = useState<boolean>(false);

  useEffect(() => {
    let active = true;
    checkBackendHealth().then((ok) => {
      if (active) setApiConnected(ok);
    });
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-canvas flex text-navy transition-colors">
      {/* Navigation Sidebar */}
      <Sidebar
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Column */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header onToggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)} />

        <main className="flex-1 p-4 md:p-8 overflow-y-auto">
          <div className="max-w-7xl mx-auto">
            <Breadcrumbs />
            <div
              role="status"
              className="mb-4 px-3 py-2 rounded-standard bg-surface border border-border-subtle text-xs text-navy-secondary flex items-center justify-between"
            >
              <span>
                <strong className="font-semibold text-navy">Demo Data:</strong> Module views currently display simulated sample datasets.
              </span>
              <span className="font-mono text-[11px] text-navy-muted">
                {apiConnected ? 'API: Connected' : 'API: Demo/Offline'}
              </span>
            </div>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AppShell;
