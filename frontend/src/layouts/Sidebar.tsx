import React, { useState } from 'react';
import { NavLink } from '../router';
import {
  Sparkles,
  BarChart3,
  MessageSquare,
  BookOpen,
  Database,
  Users,
  LifeBuoy,
  Cpu,
  Cloud,
  Settings,
  Palette,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';

interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: React.FC<{ className?: string }>;
  badge?: string;
}

const navItems: NavigationItem[] = [
  { id: 'intelligence', label: 'Admin Intelligence', path: '/', icon: BarChart3 },
  { id: 'chat', label: 'AI Chat Agent', path: '/chat', icon: MessageSquare, badge: 'Live' },
  { id: 'knowledge', label: 'Knowledge Base', path: '/knowledge', icon: BookOpen },
  { id: 'data-hub', label: 'Business Data Hub', path: '/data-hub', icon: Database },
  { id: 'customers', label: 'Customer Management', path: '/customers', icon: Users },
  { id: 'tickets', label: 'Complaints & Tickets', path: '/tickets', icon: LifeBuoy },
  { id: 'integrations', label: 'Integrations & Tools', path: '/integrations', icon: Cpu },
  { id: 'infrastructure', label: 'Cloud & Infrastructure', path: '/infrastructure', icon: Cloud },
  { id: 'admin', label: 'Enterprise Administration', path: '/admin', icon: Settings },
  { id: 'tokens', label: 'Design Tokens', path: '/tokens', icon: Palette, badge: 'T1.2' },
];

interface SidebarProps {
  isMobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isMobileOpen, onCloseMobile }) => {
  const [collapsed, setCollapsed] = useState<boolean>(false);

  return (
    <>
      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-navy-900/40 backdrop-blur-sm z-40 md:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        aria-label="Primary navigation sidebar"
        className={`fixed md:sticky top-0 left-0 h-screen bg-surface border-r border-border-subtle flex flex-col justify-between z-50 transition-all duration-300 shadow-subtle ${
          collapsed ? 'w-20' : 'w-64'
        } ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}
      >
        {/* Brand Header */}
        <div>
          <div className="h-16 px-4 flex items-center justify-between border-b border-border-subtle">
            <div className="flex items-center space-x-3 overflow-hidden">
              <div className="w-9 h-9 rounded-standard bg-tealAccent-light border border-tealAccent-border text-tealAccent flex items-center justify-center shrink-0">
                <Sparkles className="w-5 h-5" />
              </div>
              {!collapsed && (
                <div className="truncate">
                  <span className="text-base font-bold text-navy tracking-tight block">
                    BankingAIPlatform
                  </span>
                  <span className="text-[10px] text-tealAccent font-semibold tracking-wider uppercase block">
                    Enterprise AI
                  </span>
                </div>
              )}
            </div>

            <button
              type="button"
              onClick={() => setCollapsed(!collapsed)}
              className="hidden md:flex p-1.5 rounded-standard text-navy-muted hover:bg-surface-subdued hover:text-navy transition"
              aria-label={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
            >
              {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          </div>

          {/* Navigation Links List */}
          <nav aria-label="Main Navigation" className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.id}
                  to={item.path}
                  onClick={onCloseMobile}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-3 py-2.5 rounded-standard text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-tealAccent-light text-tealAccent border-l-4 border-tealAccent shadow-subtle'
                        : 'text-navy-secondary hover:bg-surface-subdued hover:text-navy'
                    } ${collapsed ? 'justify-center' : ''}`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                  {!collapsed && item.badge && (
                    <span className="ml-auto px-1.5 py-0.5 rounded-pill text-[10px] font-bold bg-navy-50 text-navy-700">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Footer: Operational Status */}
        <div className="p-3 border-t border-border-subtle bg-canvas/60">
          <div className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-2'}`}>
            <ShieldCheck className="w-4 h-4 text-status-success shrink-0" />
            {!collapsed && (
              <div className="text-[11px] truncate">
                <span className="font-semibold text-navy block">Operational</span>
                <span className="text-navy-muted block text-[10px]">AI Agents Ready</span>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
