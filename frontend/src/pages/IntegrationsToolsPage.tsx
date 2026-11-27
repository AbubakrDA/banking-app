import React from 'react';
import { ShieldCheck, Zap, Lock, AlertTriangle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui';

export const IntegrationsToolsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-navy">Tool Gateway & Integrations Registry</h1>
          <p className="text-xs text-navy-muted">
            Specification §6 • Governed Tool Execution, Risk Classification, MCP Server Proxies, and Human Approval
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="teal" hasDot>Tool Gateway Active</Badge>
          <Button variant="primary" size="sm">+ Register Tool</Button>
        </div>
      </div>

      {/* Tool Risk Tier Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-xs text-navy flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-status-success" /> LOW Risk Tools
            </span>
            <Badge size="sm" variant="success">Auto-Approved</Badge>
          </div>
          <p className="text-xs text-navy-muted">
            Read-only queries: knowledge search, order status check, product catalog lookup, appointment availability.
          </p>
        </div>

        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-xs text-navy flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-status-warning" /> MEDIUM Risk Tools
            </span>
            <Badge size="sm" variant="warning">Controlled</Badge>
          </div>
          <p className="text-xs text-navy-muted">
            Controlled state changes: reschedule appointments, update customer address, generate return label.
          </p>
        </div>

        <div className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-xs text-navy flex items-center gap-1.5">
              <Lock className="w-4 h-4 text-status-danger" /> HIGH Risk Tools
            </span>
            <Badge size="sm" variant="danger">Human Gate</Badge>
          </div>
          <p className="text-xs text-navy-muted">
            Privileged / financial actions: issue refund, cancel subscription, delete account. Mandatory human approval required.
          </p>
        </div>
      </div>

      {/* Registered Tools Table */}
      <Card>
        <CardHeader>
          <CardTitle>Registered Tool Registry (`/api/v1/tools/execute`)</CardTitle>
          <CardDescription>
            Every tool is validated with Pydantic v2 schemas and isolated from raw SQL execution.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Tool Identifier</TableHead>
                <TableHead>Target Subsystem</TableHead>
                <TableHead>Risk Classification</TableHead>
                <TableHead>Schema Validation</TableHead>
                <TableHead>Human Approval</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-mono font-bold text-navy">check_service_availability</TableCell>
                <TableCell>Business Data Hub (Appointments)</TableCell>
                <TableCell>
                  <Badge size="sm" variant="success">LOW</Badge>
                </TableCell>
                <TableCell>
                  <Badge size="sm" variant="teal">Pydantic v2 Schema</Badge>
                </TableCell>
                <TableCell className="text-navy-muted text-[11px]">Automatic</TableCell>
                <TableCell>
                  <Badge size="sm" variant="success" hasDot>Active</Badge>
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-mono font-bold text-navy">query_knowledge_base</TableCell>
                <TableCell>Knowledge Base RAG (pgvector)</TableCell>
                <TableCell>
                  <Badge size="sm" variant="success">LOW</Badge>
                </TableCell>
                <TableCell>
                  <Badge size="sm" variant="teal">Pydantic v2 Schema</Badge>
                </TableCell>
                <TableCell className="text-navy-muted text-[11px]">Automatic</TableCell>
                <TableCell>
                  <Badge size="sm" variant="success" hasDot>Active</Badge>
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-mono font-bold text-navy">reschedule_appointment</TableCell>
                <TableCell>Business Data Hub (Bookings)</TableCell>
                <TableCell>
                  <Badge size="sm" variant="warning">MEDIUM</Badge>
                </TableCell>
                <TableCell>
                  <Badge size="sm" variant="teal">Pydantic v2 Schema</Badge>
                </TableCell>
                <TableCell className="text-navy font-semibold text-[11px]">Policy Evaluated</TableCell>
                <TableCell>
                  <Badge size="sm" variant="success" hasDot>Active</Badge>
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell className="font-mono font-bold text-navy">issue_order_refund</TableCell>
                <TableCell>Financial / Payments Connector</TableCell>
                <TableCell>
                  <Badge size="sm" variant="danger">HIGH</Badge>
                </TableCell>
                <TableCell>
                  <Badge size="sm" variant="teal">Pydantic v2 Schema</Badge>
                </TableCell>
                <TableCell className="text-status-danger font-bold text-[11px]">
                  <AlertTriangle className="w-3 h-3 inline mr-1" /> Mandatory Review
                </TableCell>
                <TableCell>
                  <Badge size="sm" variant="danger" hasDot>Gated</Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default IntegrationsToolsPage;
