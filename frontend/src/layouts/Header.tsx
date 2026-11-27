import React, { useState } from 'react';
import {
  Bell,
  Search,
  Building2,
  ChevronDown,
  Sun,
  Moon,
  Menu,
  CheckCircle2,
} from 'lucide-react';

interface HeaderProps {
  onToggleMobileMenu?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleMobileMenu }) => {
  const [isDark, setIsDark] = useState<boolean>(() => {
    if (typeof document !== 'undefined') {
      return document.documentElement.classList.contains('dark');
    }
    return false;
  });
  const [showNotifications, setShowNotifications] = useState<boolean>(false);
  const [showUserMenu, setShowUserMenu] = useState<boolean>(false);

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (nextDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <header className="h-16 bg-surface border-b border-border-subtle px-4 md:px-8 flex items-center justify-between sticky top-0 z-30 transition-colors shadow-subtle">
      {/* Left: Mobile Toggle & Tenant Context */}
      <div className="flex items-center space-x-3 md:space-x-4">
        {onToggleMobileMenu && (
          <button
            type="button"
            onClick={onToggleMobileMenu}
            className="md:hidden p-2 rounded-standard text-navy-secondary hover:bg-surface-subdued transition"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        {/* Tenant Switcher Context Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-standard bg-canvas border border-border-subtle text-xs">
          <Building2 className="w-3.5 h-3.5 text-tealAccent" />
          <span className="font-semibold text-navy">Acme Global Ltd</span>
          <span className="hidden sm:inline text-navy-muted">|</span>
          <span className="hidden sm:inline text-navy-muted font-mono">tenant_prod_01</span>
          <ChevronDown className="w-3 h-3 text-navy-muted" />
        </div>
      </div>

      {/* Center: Quick Search Bar */}
      <div className="hidden lg:flex items-center w-80 relative">
        <Search className="w-4 h-4 text-navy-muted absolute left-3 pointer-events-none" />
        <input
          type="text"
          placeholder="Search conversations, KB, tickets..."
          className="w-full pl-9 pr-4 py-1.5 rounded-standard bg-canvas border border-border-subtle text-xs text-navy placeholder:text-navy-muted focus:outline-none focus:border-border-focus transition"
        />
      </div>

      {/* Right: Actions, Theme, Notifications, User Profile */}
      <div className="flex items-center space-x-2 md:space-x-3">
        {/* Theme Toggle */}
        <button
          type="button"
          onClick={toggleTheme}
          className="p-2 rounded-standard text-navy-secondary hover:bg-surface-subdued transition"
          aria-label="Toggle theme"
        >
          {isDark ? (
            <Sun className="w-4 h-4 text-status-warning" />
          ) : (
            <Moon className="w-4 h-4 text-navy-muted" />
          )}
        </button>

        {/* Notifications Popover Trigger */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-standard text-navy-secondary hover:bg-surface-subdued relative transition"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4 text-navy-muted" />
            <span className="w-2 h-2 rounded-full bg-tealAccent absolute top-1.5 right-1.5" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-72 bg-surface rounded-card border border-border-subtle shadow-elevation p-4 z-50 text-xs space-y-3">
              <div className="flex items-center justify-between border-b border-border-subtle pb-2">
                <span className="font-bold text-navy">Notifications</span>
                <span className="text-tealAccent font-medium text-[11px]">Mark read</span>
              </div>
              <div className="flex items-start space-x-2 text-navy-secondary">
                <CheckCircle2 className="w-4 h-4 text-status-success shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-navy">Google Sheets Synced</p>
                  <p className="text-navy-muted text-[11px]">Products table synced 4 minutes ago</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Profile Dropdown Trigger */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-2 pl-2 pr-1 py-1 rounded-standard hover:bg-surface-subdued transition"
            aria-label="User Profile"
          >
            <div className="w-7 h-7 rounded-full bg-tealAccent-light border border-tealAccent-border text-tealAccent font-bold text-xs flex items-center justify-center">
              AC
            </div>
            <div className="hidden md:block text-left text-xs">
              <span className="font-semibold text-navy block leading-tight">Alex Chen</span>
              <span className="text-[10px] text-navy-muted block">Support Lead</span>
            </div>
            <ChevronDown className="w-3 h-3 text-navy-muted hidden md:block" />
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-52 bg-surface rounded-card border border-border-subtle shadow-elevation p-2 z-50 text-xs space-y-1">
              <div className="px-3 py-2 border-b border-border-subtle mb-1">
                <p className="font-bold text-navy">Alex Chen</p>
                <p className="text-navy-muted text-[11px]">alex@banking-ai-platform.internal</p>
                <span className="inline-block mt-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blueAccent-light text-blueAccent">
                  Role: Org Admin
                </span>
              </div>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 rounded-standard hover:bg-surface-subdued text-navy transition"
              >
                Profile Settings
              </button>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 rounded-standard hover:bg-surface-subdued text-navy transition"
              >
                Security & 2FA
              </button>
              <div className="border-t border-border-subtle my-1" />
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 rounded-standard hover:bg-status-danger-bg text-status-danger transition"
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
