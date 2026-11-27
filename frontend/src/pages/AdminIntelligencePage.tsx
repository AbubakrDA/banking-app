import React from 'react';
import { BarChart3, TrendingUp, Users, MessageSquare, AlertCircle, ArrowUpRight } from 'lucide-react';

export const AdminIntelligencePage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-navy">
            Admin Intelligence & Executive Analytics
          </h1>
          <p className="text-xs text-navy-muted">
            Phase 11 Platform Module • High-level organizational KPIs, AI performance, and query insights
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 rounded-pill text-xs font-semibold bg-tealAccent-light text-tealAccent border border-tealAccent-border">
            Module I Placeholder
          </span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-2">
          <div className="flex items-center justify-between text-xs text-navy-muted">
            <span className="font-medium">Total Conversations</span>
            <MessageSquare className="w-4 h-4 text-tealAccent" />
          </div>
          <div className="text-2xl font-bold text-navy">1,284</div>
          <div className="flex items-center space-x-1 text-xs text-status-success font-medium">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>+14.2% vs last week</span>
          </div>
        </div>

        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-2">
          <div className="flex items-center justify-between text-xs text-navy-muted">
            <span className="font-medium">AI Automation Rate</span>
            <BarChart3 className="w-4 h-4 text-blueAccent" />
          </div>
          <div className="text-2xl font-bold text-navy">88.4%</div>
          <div className="flex items-center space-x-1 text-xs text-status-success font-medium">
            <ArrowUpRight className="w-3.5 h-3.5" />
            <span>Target: &gt;85%</span>
          </div>
        </div>

        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-2">
          <div className="flex items-center justify-between text-xs text-navy-muted">
            <span className="font-medium">Active Customers</span>
            <Users className="w-4 h-4 text-tealAccent" />
          </div>
          <div className="text-2xl font-bold text-navy">642</div>
          <div className="text-xs text-navy-muted font-medium">Across 3 business channels</div>
        </div>

        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-2">
          <div className="flex items-center justify-between text-xs text-navy-muted">
            <span className="font-medium">Human Escalations</span>
            <AlertCircle className="w-4 h-4 text-status-warning" />
          </div>
          <div className="text-2xl font-bold text-navy">24</div>
          <div className="text-xs text-status-warning font-medium">1.8% of total volume</div>
        </div>
      </div>

      {/* Main Content Card */}
      <div className="bg-surface rounded-card p-6 border border-border-subtle shadow-card space-y-4">
        <h2 className="text-lg font-bold text-navy">System Intelligence Overview</h2>
        <p className="text-sm text-navy-secondary leading-relaxed">
          The full Admin Intelligence dashboard, scheduled executive reporting, AI Insights, and the Analytics Copilot will be implemented in <strong>Phase 11</strong> under strict Harness Engineering controls.
        </p>
        <div className="p-4 rounded-standard bg-canvas border border-border-subtle text-xs text-navy-muted">
          Active Layout: Collapsible Sidebar • Responsive Navigation Shell • Unified Design Tokens
        </div>
      </div>
    </div>
  );
};

export default AdminIntelligencePage;
