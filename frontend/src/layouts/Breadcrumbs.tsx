import React from 'react';
import { useRouter } from '../router/hooks';
import { ChevronRight, Home } from 'lucide-react';

const routeLabels: Record<string, string> = {
  '/': 'Admin Intelligence',
  '/chat': 'AI Chat Agent',
  '/knowledge': 'Knowledge Base',
  '/data-hub': 'Business Data Hub',
  '/customers': 'Customer Management',
  '/tickets': 'Complaints & Tickets',
  '/integrations': 'Integrations & Tools',
  '/infrastructure': 'Cloud & Infrastructure',
  '/admin': 'Enterprise Administration',
  '/tokens': 'Design Tokens Preview',
};

export const Breadcrumbs: React.FC = () => {
  const { path, navigate } = useRouter();
  const currentLabel = routeLabels[path] || 'Overview';

  return (
    <nav aria-label="Breadcrumb" className="flex items-center space-x-2 text-xs text-navy-muted mb-6">
      <button
        type="button"
        onClick={() => navigate('/')}
        className="flex items-center gap-1 hover:text-navy transition font-medium"
      >
        <Home className="w-3.5 h-3.5 text-navy-muted" />
        <span>Platform</span>
      </button>

      <ChevronRight className="w-3 h-3 text-border-default" />

      <span className="font-semibold text-navy">
        {currentLabel}
      </span>
    </nav>
  );
};

export default Breadcrumbs;
