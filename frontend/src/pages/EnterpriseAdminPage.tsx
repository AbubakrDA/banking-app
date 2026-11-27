import React from 'react';
import { Card, CardContent, Button, Badge, Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Input, Tabs, TabList, TabTrigger, TabContent } from '../components/ui';

export const EnterpriseAdminPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-navy">Enterprise Administration</h1>
          <p className="text-xs text-navy-muted">
            Module J • Tenant Profile, Corporate Branding, Role-Based Access Control, and Immutable Audit Trail
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="teal">Tenant Admin Mode</Badge>
          <Button variant="primary" size="sm">Save Changes</Button>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="branding">
            <TabList>
              <TabTrigger value="branding">Organization & Branding</TabTrigger>
              <TabTrigger value="users">Users & Roles (RBAC)</TabTrigger>
              <TabTrigger value="audit">Security & Audit Logs</TabTrigger>
            </TabList>

            {/* Tab 1: Organization & Branding */}
            <TabContent value="branding">
              <div className="space-y-6 max-w-2xl py-2">
                <div className="space-y-4">
                  <Input
                    label="Company / Organization Name"
                    defaultValue="Acme Global Ltd"
                    helperText="Appears on all customer-facing chat widgets, emails, and PDF reports."
                  />
                  <Input
                    label="Primary Support Domain"
                    defaultValue="support.acmeglobal.com"
                    helperText="Custom domain mapped to BankingAIPlatform CDN."
                  />
                  <div className="space-y-1">
                    <label className="block text-xs font-semibold text-navy">Company Logo</label>
                    <div className="p-4 rounded-standard bg-canvas border border-border-default flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-standard bg-tealAccent-light border border-tealAccent-border text-tealAccent font-bold flex items-center justify-center">
                          AG
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-navy">acme_logo_primary.svg</p>
                          <p className="text-[10px] text-navy-muted">Vector SVG • 48x48px</p>
                        </div>
                      </div>
                      <Button size="sm" variant="outline">Replace Logo</Button>
                    </div>
                  </div>
                </div>
              </div>
            </TabContent>

            {/* Tab 2: Users & RBAC */}
            <TabContent value="users">
              <div className="space-y-4 py-2">
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-xs text-navy">Staff & Role Allocations</h3>
                  <Button size="sm" variant="outline">+ Invite User</Button>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Staff Member</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Permissions Scope</TableHead>
                      <TableHead>2FA Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell className="font-semibold text-navy">Alex Chen (alex@banking-ai-platform.internal)</TableCell>
                      <TableCell><Badge size="sm" variant="blue">Org Admin</Badge></TableCell>
                      <TableCell className="text-navy-secondary text-xs">Full Tenant Access & Security Controls</TableCell>
                      <TableCell><Badge size="sm" variant="success" hasDot>Enforced</Badge></TableCell>
                      <TableCell><Button size="sm" variant="outline">Edit</Button></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-semibold text-navy">Jessica Taylor (jess@banking-ai-platform.internal)</TableCell>
                      <TableCell><Badge size="sm" variant="teal">Support Agent</Badge></TableCell>
                      <TableCell className="text-navy-secondary text-xs">Chat Workspace & Ticket Management</TableCell>
                      <TableCell><Badge size="sm" variant="success" hasDot>Enforced</Badge></TableCell>
                      <TableCell><Button size="sm" variant="outline">Edit</Button></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </TabContent>

            {/* Tab 3: Security & Audit Logs */}
            <TabContent value="audit">
              <div className="space-y-4 py-2">
                <div className="flex justify-between items-center">
                  <h3 className="font-bold text-xs text-navy">Immutable Tenant Security Event Stream</h3>
                  <Button size="sm" variant="outline">Export Audit Trail (CSV)</Button>
                </div>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp (UTC)</TableHead>
                      <TableHead>Event Action</TableHead>
                      <TableHead>Actor</TableHead>
                      <TableHead>Target Resource</TableHead>
                      <TableHead>Security Result</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell className="font-mono text-[11px] text-navy-muted">2026-11-24 07:18:22</TableCell>
                      <TableCell className="font-semibold text-navy">SYNC_DATA_SOURCE</TableCell>
                      <TableCell>System Scheduler</TableCell>
                      <TableCell className="font-mono text-xs">GoogleSheets:Stock</TableCell>
                      <TableCell><Badge size="sm" variant="success" hasDot>SUCCESS</Badge></TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="font-mono text-[11px] text-navy-muted">2026-11-24 06:44:10</TableCell>
                      <TableCell className="font-semibold text-navy">LOGIN_SUCCESS</TableCell>
                      <TableCell>alex@banking-ai-platform.internal</TableCell>
                      <TableCell className="font-mono text-xs">Keycloak OIDC</TableCell>
                      <TableCell><Badge size="sm" variant="success" hasDot>VERIFIED</Badge></TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </TabContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default EnterpriseAdminPage;
