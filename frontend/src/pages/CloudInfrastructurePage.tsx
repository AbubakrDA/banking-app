import React from 'react';
import { Server, Activity, ShieldCheck, Database, HardDrive, CheckCircle2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge } from '../components/ui';

export const CloudInfrastructurePage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-navy">Cloud & Infrastructure Dashboard</h1>
          <p className="text-xs text-navy-muted">
            Specification §8 & §14 • Service Health, Container Telemetry, Multi-Tenant Storage Quotas, and Disaster Recovery
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="success" hasDot>All Systems Operational</Badge>
          <Button variant="outline" size="sm">Backup Now</Button>
        </div>
      </div>

      {/* Services Health Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { name: 'FastAPI Application Gateway', type: 'ECS Fargate Container', status: 'Healthy', latency: '24ms', icon: Activity },
          { name: 'PostgreSQL 16 + pgvector', type: 'Primary Relational DB', status: 'Healthy', latency: '8ms', icon: Database },
          { name: 'Redis 7 Cache & Broker', type: 'ElastiCache Instance', status: 'Healthy', latency: '2ms', icon: Server },
          { name: 'Celery Background Task Workers', type: 'Distributed Workers (4x)', status: 'Active', latency: '0 queue lag', icon: Server },
          { name: 'MinIO / S3 Object Storage', type: 'Private Tenant Buckets', status: 'Healthy', latency: 'Quota: 14% used', icon: HardDrive },
          { name: 'ClamAV Malware Quarantine Pipeline', type: 'Security Container', status: 'Scanning Ready', latency: '100% clean', icon: ShieldCheck },
        ].map((svc) => {
          const Icon = svc.icon;
          return (
            <div key={svc.name} className="bg-surface rounded-card p-5 border border-border-subtle shadow-card space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-navy flex items-center gap-1.5">
                  <Icon className="w-4 h-4 text-tealAccent" /> {svc.name}
                </span>
                <Badge size="sm" variant="success" hasDot>{svc.status}</Badge>
              </div>
              <p className="text-[11px] text-navy-muted">{svc.type}</p>
              <div className="pt-2 border-t border-border-subtle flex justify-between text-[10px] text-navy-secondary">
                <span>Metrics:</span>
                <span className="font-mono font-semibold">{svc.latency}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Disaster Recovery & Backup Plan */}
      <Card>
        <CardHeader>
          <CardTitle>Automated Backup & Disaster Recovery (RPO / RTO)</CardTitle>
          <CardDescription>
            Continuous automated database snapshots, encrypted multi-region replication, and automated recovery runbooks.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
            <div className="p-4 rounded-standard bg-canvas border border-border-subtle space-y-1 text-xs">
              <span className="font-bold text-navy block">Recovery Point Objective (RPO)</span>
              <p className="text-xl font-bold text-tealAccent">&lt; 1 Hour</p>
              <p className="text-navy-muted text-[11px]">Automated incremental WAL archiving</p>
            </div>
            <div className="p-4 rounded-standard bg-canvas border border-border-subtle space-y-1 text-xs">
              <span className="font-bold text-navy block">Recovery Time Objective (RTO)</span>
              <p className="text-xl font-bold text-blueAccent">&lt; 4 Hours</p>
              <p className="text-navy-muted text-[11px]">Automated infrastructure spin-up</p>
            </div>
            <div className="p-4 rounded-standard bg-canvas border border-border-subtle space-y-1 text-xs">
              <span className="font-bold text-navy block">Last Validated Backup</span>
              <p className="text-xl font-bold text-status-success flex items-center gap-1">
                <CheckCircle2 className="w-5 h-5" /> Verified Clean
              </p>
              <p className="text-navy-muted text-[11px]">Snapshot taken today at 04:00 UTC</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CloudInfrastructurePage;
