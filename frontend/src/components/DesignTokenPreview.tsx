import React, { useState } from 'react';
import {
  Sun,
  Moon,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Info,
  Shield,
  Layers,
  Palette,
  Type,
  LayoutGrid,
} from 'lucide-react';

export const DesignTokenPreview: React.FC = () => {
  const [isDark, setIsDark] = useState<boolean>(false);

  const toggleTheme = () => {
    setIsDark(!isDark);
    if (!isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <div className={`min-h-screen bg-canvas text-navy transition-colors duration-200 p-6 md:p-10 ${isDark ? 'dark' : ''}`}>
      <div className="max-w-6xl mx-auto space-y-10">
        
        {/* Header Bar */}
        <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-border-subtle">
          <div className="flex items-center space-x-3">
            <div className="w-11 h-11 rounded-card bg-tealAccent-light border border-tealAccent-border flex items-center justify-center text-tealAccent">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-bold tracking-tight text-navy">
                  BankingAIPlatform Design System
                </h1>
                <span className="px-2.5 py-0.5 rounded-pill text-xs font-semibold bg-tealAccent-light text-tealAccent border border-tealAccent-border">
                  Task 1.2
                </span>
              </div>
              <p className="text-sm text-navy-muted">
                Semantic Design Tokens Preview — Light-grey Canvas, White Cards, Navy Text, Teal & Blue Accents
              </p>
            </div>
          </div>

          <button
            onClick={toggleTheme}
            type="button"
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-standard text-sm font-medium bg-surface border border-border-subtle shadow-subtle hover:bg-surface-subdued text-navy transition"
            aria-label="Toggle light/dark theme"
          >
            {isDark ? (
              <>
                <Sun className="w-4 h-4 text-status-warning" />
                <span>Light Mode</span>
              </>
            ) : (
              <>
                <Moon className="w-4 h-4 text-navy-secondary" />
                <span>Dark Mode</span>
              </>
            )}
          </button>
        </header>

        {/* Section 1: Color Palette Tokens */}
        <section className="space-y-4">
          <div className="flex items-center space-x-2">
            <Palette className="w-5 h-5 text-tealAccent" />
            <h2 className="text-lg font-bold text-navy">1. Semantic Color Tokens</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Primary Accent (Teal) */}
            <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-3">
              <span className="text-xs font-semibold text-navy-muted uppercase tracking-wider">Primary Accent</span>
              <div className="h-14 rounded-standard bg-tealAccent flex items-center justify-center text-white font-semibold text-sm">
                Teal Accent (#0D9488)
              </div>
              <div className="flex justify-between items-center text-xs text-navy-secondary">
                <span>Light Tint:</span>
                <span className="px-2 py-0.5 rounded bg-tealAccent-light text-tealAccent font-mono">bg-tealAccent-light</span>
              </div>
              <div className="flex justify-between items-center text-xs text-navy-secondary">
                <span>Hover State:</span>
                <span className="px-2 py-0.5 rounded bg-tealAccent-hover text-white font-mono">tealAccent-hover</span>
              </div>
            </div>

            {/* Secondary Accent (Blue) */}
            <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-3">
              <span className="text-xs font-semibold text-navy-muted uppercase tracking-wider">Secondary Accent</span>
              <div className="h-14 rounded-standard bg-blueAccent flex items-center justify-center text-white font-semibold text-sm">
                Blue Accent (#2563EB)
              </div>
              <div className="flex justify-between items-center text-xs text-navy-secondary">
                <span>Light Tint:</span>
                <span className="px-2 py-0.5 rounded bg-blueAccent-light text-blueAccent font-mono">bg-blueAccent-light</span>
              </div>
              <div className="flex justify-between items-center text-xs text-navy-secondary">
                <span>Hover State:</span>
                <span className="px-2 py-0.5 rounded bg-blueAccent-hover text-white font-mono">blueAccent-hover</span>
              </div>
            </div>

            {/* Canvas & Surface */}
            <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-3">
              <span className="text-xs font-semibold text-navy-muted uppercase tracking-wider">Surfaces & Canvas</span>
              <div className="h-14 rounded-standard bg-canvas border border-border-subtle flex items-center justify-center text-navy font-semibold text-sm">
                Canvas (#F8FAFC)
              </div>
              <div className="flex justify-between items-center text-xs text-navy-secondary">
                <span>Card Surface:</span>
                <span className="px-2 py-0.5 rounded bg-surface border border-border-subtle text-navy font-mono">#FFFFFF</span>
              </div>
              <div className="flex justify-between items-center text-xs text-navy-secondary">
                <span>Subdued Surface:</span>
                <span className="px-2 py-0.5 rounded bg-surface-subdued text-navy font-mono">#F1F5F9</span>
              </div>
            </div>

            {/* Typography (Navy) */}
            <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-3">
              <span className="text-xs font-semibold text-navy-muted uppercase tracking-wider">Navy Typography</span>
              <div className="h-14 rounded-standard bg-navy-900 flex items-center justify-center text-white font-semibold text-sm">
                Navy (#0B1D33)
              </div>
              <div className="flex justify-between items-center text-xs text-navy-secondary">
                <span>Secondary Text:</span>
                <span className="font-medium text-navy-secondary">#334E68</span>
              </div>
              <div className="flex justify-between items-center text-xs text-navy-muted">
                <span>Muted Text:</span>
                <span className="font-medium text-navy-muted">#627D98</span>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: Typography Hierarchy & Contrast */}
        <section className="space-y-4">
          <div className="flex items-center space-x-2">
            <Type className="w-5 h-5 text-tealAccent" />
            <h2 className="text-lg font-bold text-navy">2. Typography Hierarchy (Inter / Accessible Contrast)</h2>
          </div>

          <div className="bg-surface rounded-card p-6 border border-border-subtle shadow-card space-y-4">
            <div className="border-b border-border-subtle pb-3">
              <span className="text-xs font-mono text-navy-muted">Heading 1 — 28px Bold / Tracking Tight</span>
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-navy">
                Intelligent Customer Operations & Analytics
              </h1>
            </div>
            <div className="border-b border-border-subtle pb-3">
              <span className="text-xs font-mono text-navy-muted">Heading 2 — 20px SemiBold</span>
              <h2 className="text-xl font-semibold text-navy">
                Autonomous AI Agent Orchestration & Knowledge Retrieval
              </h2>
            </div>
            <div className="border-b border-border-subtle pb-3">
              <span className="text-xs font-mono text-navy-muted">Body Regular — 14px Text Secondary</span>
              <p className="text-sm text-navy-secondary leading-relaxed">
                BankingAIPlatform seamlessly harmonizes multi-tenant AI customer support, document intelligence, customer memory, and external business data sources like Google Sheets and relational databases.
              </p>
            </div>
            <div>
              <span className="text-xs font-mono text-navy-muted">Caption / Meta — 12px Text Muted</span>
              <p className="text-xs text-navy-muted font-medium">
                Tenant ID: tenant_enterprise_01 • Last synced: 2 minutes ago • Status: Connected
              </p>
            </div>
          </div>
        </section>

        {/* Section 3: Cards, Elevations & Rounded Radii */}
        <section className="space-y-4">
          <div className="flex items-center space-x-2">
            <LayoutGrid className="w-5 h-5 text-tealAccent" />
            <h2 className="text-lg font-bold text-navy">3. Rounded Cards & Restrained Elevations</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-surface rounded-card p-6 border border-border-subtle shadow-subtle space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-navy uppercase tracking-wider">
                <Layers className="w-4 h-4 text-tealAccent" />
                <span>Base Card (12px Radius)</span>
              </div>
              <p className="text-xs text-navy-secondary">
                Subtle shadow and clean border for default content containers, lists, and form panels.
              </p>
            </div>

            <div className="bg-surface rounded-card p-6 border border-border-subtle shadow-card hover:shadow-card-hover transition-shadow space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-navy uppercase tracking-wider">
                <Layers className="w-4 h-4 text-blueAccent" />
                <span>Hoverable Card</span>
              </div>
              <p className="text-xs text-navy-secondary">
                Card with interactive hover elevation for actionable dashboard widgets and ticket items.
              </p>
            </div>

            <div className="bg-surface rounded-modal p-6 border border-border-subtle shadow-elevation space-y-2">
              <div className="flex items-center space-x-2 text-xs font-bold text-navy uppercase tracking-wider">
                <Shield className="w-4 h-4 text-tealAccent" />
                <span>Modal / Dialog (16px Radius)</span>
              </div>
              <p className="text-xs text-navy-secondary">
                Deeper elevation and 16px radius for flyouts, modals, and focused configuration drawers.
              </p>
            </div>
          </div>
        </section>

        {/* Section 4: Component States & Status Badges */}
        <section className="space-y-4">
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-tealAccent" />
            <h2 className="text-lg font-bold text-navy">4. Component States, Badges & Buttons</h2>
          </div>

          <div className="bg-surface rounded-card p-6 border border-border-subtle shadow-card space-y-6">
            {/* Buttons */}
            <div>
              <span className="text-xs font-semibold text-navy-muted uppercase tracking-wider block mb-3">
                Button States
              </span>
              <div className="flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  className="px-4 py-2 rounded-standard text-sm font-semibold bg-tealAccent text-white hover:bg-tealAccent-hover shadow-subtle transition"
                >
                  Primary Teal
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded-standard text-sm font-semibold bg-blueAccent text-white hover:bg-blueAccent-hover shadow-subtle transition"
                >
                  Secondary Blue
                </button>
                <button
                  type="button"
                  className="px-4 py-2 rounded-standard text-sm font-medium bg-surface border border-border-subtle text-navy hover:bg-surface-subdued shadow-subtle transition"
                >
                  Outline Neutral
                </button>
                <button
                  type="button"
                  disabled
                  className="px-4 py-2 rounded-standard text-sm font-medium bg-surface-subdued text-navy-muted border border-border-subtle cursor-not-allowed opacity-60"
                >
                  Disabled
                </button>
              </div>
            </div>

            {/* Status Badges */}
            <div className="border-t border-border-subtle pt-6">
              <span className="text-xs font-semibold text-navy-muted uppercase tracking-wider block mb-3">
                Semantic Status Badges
              </span>
              <div className="flex flex-wrap items-center gap-3">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-xs font-medium bg-status-success-bg text-status-success border border-status-success-border">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Active / Connected
                </span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-xs font-medium bg-status-warning-bg text-status-warning border border-status-warning-border">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  Syncing / Pending
                </span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-xs font-medium bg-status-danger-bg text-status-danger border border-status-danger-border">
                  <XCircle className="w-3.5 h-3.5" />
                  Quarantined / Failed
                </span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-xs font-medium bg-status-info-bg text-status-info border border-status-info-border">
                  <Info className="w-3.5 h-3.5" />
                  Information
                </span>
              </div>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
};

export default DesignTokenPreview;
