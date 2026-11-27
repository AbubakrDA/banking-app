import React, { useState } from 'react';
import { Database, Sheet, FileSpreadsheet, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui';

export const BusinessDataHubPage: React.FC = () => {
  const [businessMode, setBusinessMode] = useState<'products' | 'services' | 'hybrid'>('hybrid');
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  const handleSync = () => {
    setIsSyncing(true);
    setTimeout(() => setIsSyncing(false), 800);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-navy">Business Data Hub</h1>
          <p className="text-xs text-navy-muted">
            Module E • External Data Source Connectors, Google Sheets, and Relational Synchronization
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={handleSync} isLoading={isSyncing}>
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
            Sync All Sources
          </Button>
          <Button variant="primary" size="sm">
            + Add Data Source
          </Button>
        </div>
      </div>

      {/* Business Model Configuration Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Organization Business Model Configuration</CardTitle>
              <CardDescription>
                Select the operational model for this tenant. This determines whether inventory, bookings, or both are active across AI tools.
              </CardDescription>
            </div>
            <Badge variant="teal">Spec §3 Compliant</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              onClick={() => setBusinessMode('products')}
              className={`p-4 rounded-standard border cursor-pointer transition ${
                businessMode === 'products'
                  ? 'border-tealAccent bg-tealAccent-light/50 ring-2 ring-tealAccent/20'
                  : 'border-border-subtle bg-surface hover:bg-surface-hover'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-sm text-navy">Products Only</span>
                {businessMode === 'products' && <CheckCircle2 className="w-4 h-4 text-tealAccent" />}
              </div>
              <p className="text-xs text-navy-muted">
                SKUs, catalog, stock quantities, suppliers, physical orders and deliveries.
              </p>
            </div>

            <div
              onClick={() => setBusinessMode('services')}
              className={`p-4 rounded-standard border cursor-pointer transition ${
                businessMode === 'services'
                  ? 'border-tealAccent bg-tealAccent-light/50 ring-2 ring-tealAccent/20'
                  : 'border-border-subtle bg-surface hover:bg-surface-hover'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-sm text-navy">Services Only</span>
                {businessMode === 'services' && <CheckCircle2 className="w-4 h-4 text-tealAccent" />}
              </div>
              <p className="text-xs text-navy-muted">
                Service catalog, durations, staff allocation, bookings, and appointment calendar.
              </p>
            </div>

            <div
              onClick={() => setBusinessMode('hybrid')}
              className={`p-4 rounded-standard border cursor-pointer transition ${
                businessMode === 'hybrid'
                  ? 'border-tealAccent bg-tealAccent-light/50 ring-2 ring-tealAccent/20'
                  : 'border-border-subtle bg-surface hover:bg-surface-hover'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-sm text-navy">Products & Services (Hybrid)</span>
                {businessMode === 'hybrid' && <CheckCircle2 className="w-4 h-4 text-tealAccent" />}
              </div>
              <p className="text-xs text-navy-muted">
                Unified model supporting inventory management alongside service appointments.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Connected Connectors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sheet className="w-5 h-5 text-status-success" />
              <span className="font-bold text-xs text-navy">Google Sheets API</span>
            </div>
            <Badge size="sm" variant="success" hasDot>Connected</Badge>
          </div>
          <p className="text-xs text-navy-secondary">
            Spreadsheet: <span className="font-semibold text-navy">Acme Inventory & Pricing 2026</span>
          </p>
          <div className="flex justify-between items-center text-[11px] text-navy-muted pt-2 border-t border-border-subtle">
            <span>Mode: Read-Only (OAuth)</span>
            <span>Synced 8m ago</span>
          </div>
        </div>

        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileSpreadsheet className="w-5 h-5 text-blueAccent" />
              <span className="font-bold text-xs text-navy">Excel & CSV Uploads</span>
            </div>
            <Badge size="sm" variant="blue">Active</Badge>
          </div>
          <p className="text-xs text-navy-secondary">
            File: <span className="font-semibold text-navy">staff_schedules_q4.xlsx</span>
          </p>
          <div className="flex justify-between items-center text-[11px] text-navy-muted pt-2 border-t border-border-subtle">
            <span>284 records parsed</span>
            <span>Validated</span>
          </div>
        </div>

        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-tealAccent" />
              <span className="font-bold text-xs text-navy">PostgreSQL Operational DB</span>
            </div>
            <Badge size="sm" variant="teal" hasDot>Primary</Badge>
          </div>
          <p className="text-xs text-navy-secondary">
            Internal PostgreSQL database maintaining tenants, users, and audit records.
          </p>
          <div className="flex justify-between items-center text-[11px] text-navy-muted pt-2 border-t border-border-subtle">
            <span>Row-Level Security</span>
            <span>Healthy</span>
          </div>
        </div>
      </div>

      {/* Synchronized Tables Matrix */}
      <Card>
        <CardHeader>
          <CardTitle>Synchronized Business Data Records</CardTitle>
          <CardDescription>
            Data tables actively available to AI Agents through the governed Tool Gateway.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Data Entity</TableHead>
                <TableHead>Source Connector</TableHead>
                <TableHead>Record Count</TableHead>
                <TableHead>Freshness</TableHead>
                <TableHead>Quality Status</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-semibold text-navy">Products & Inventory</TableCell>
                <TableCell className="text-navy-muted">Google Sheets (Worksheet: Stock)</TableCell>
                <TableCell>1,420 SKUs</TableCell>
                <TableCell>Synced 8m ago</TableCell>
                <TableCell>
                  <Badge size="sm" variant="success" hasDot>0 Missing Values</Badge>
                </TableCell>
                <TableCell>
                  <Button size="sm" variant="outline">Inspect Schema</Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-semibold text-navy">Service Appointments</TableCell>
                <TableCell className="text-navy-muted">Internal Bookings Engine</TableCell>
                <TableCell>482 Appointments</TableCell>
                <TableCell>Live (Real-time)</TableCell>
                <TableCell>
                  <Badge size="sm" variant="success" hasDot>Consistent Dates</Badge>
                </TableCell>
                <TableCell>
                  <Button size="sm" variant="outline">Inspect Schema</Button>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-semibold text-navy">Staff & Specialists</TableCell>
                <TableCell className="text-navy-muted">Excel Upload (staff_schedules.xlsx)</TableCell>
                <TableCell>38 Providers</TableCell>
                <TableCell>Updated Yesterday</TableCell>
                <TableCell>
                  <Badge size="sm" variant="warning" hasDot>
                    <AlertCircle className="w-3 h-3 mr-0.5 inline" /> 2 Unassigned Hours
                  </Badge>
                </TableCell>
                <TableCell>
                  <Button size="sm" variant="outline">Inspect Schema</Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default BusinessDataHubPage;
