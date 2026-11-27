import React from 'react';
import { Clock, Plus, PhoneCall, Mail, MessageSquare } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge, Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Tabs, TabList, TabTrigger, TabContent } from '../components/ui';

export const ComplaintsTicketsPage: React.FC = () => {

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-navy">Complaints & Ticket Management</h1>
          <p className="text-xs text-navy-muted">
            Module F & G • 8-Stage Ticket Lifecycle, Escalation Tracking, and Multi-Channel Customer Feedback
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="primary" size="sm">
            <Plus className="w-3.5 h-3.5 mr-1" /> Create Ticket
          </Button>
        </div>
      </div>

      {/* Lifecycle Status Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
        {[
          { label: 'New', count: 6, variant: 'neutral' as const },
          { label: 'Categorized', count: 4, variant: 'blue' as const },
          { label: 'Assigned', count: 5, variant: 'teal' as const },
          { label: 'In Progress', count: 8, variant: 'teal' as const },
          { label: 'Waiting Cust', count: 3, variant: 'warning' as const },
          { label: 'Escalated', count: 2, variant: 'danger' as const },
          { label: 'Resolved', count: 41, variant: 'success' as const },
          { label: 'Closed', count: 182, variant: 'neutral' as const },
        ].map((stage) => (
          <div key={stage.label} className="bg-surface rounded-card p-3 border border-border-subtle shadow-subtle text-center space-y-1">
            <span className="text-[10px] text-navy-muted uppercase font-bold block truncate">{stage.label}</span>
            <div className="text-lg font-bold text-navy">{stage.count}</div>
            <Badge size="sm" variant={stage.variant} className="mx-auto text-[9px] py-0">{stage.label}</Badge>
          </div>
        ))}
      </div>

      {/* Main Tickets & Feedback Views */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <div>
              <CardTitle>Active Support Tickets & Resolution Tracking</CardTitle>
              <CardDescription>
                Full lifecycle management with automated categorization, priority SLA monitoring, and customer feedback.
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Badge variant="teal" hasDot>SLA Target: 99.4%</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="tickets">
            <TabList>
              <TabTrigger value="tickets">All Tickets (28)</TabTrigger>
              <TabTrigger value="escalated">Escalated (2)</TabTrigger>
              <TabTrigger value="feedback">Feedback Responses (WhatsApp & Email)</TabTrigger>
            </TabList>

            <TabContent value="tickets">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Ticket ID</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Channel</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Lifecycle Stage</TableHead>
                    <TableHead>SLA Timer</TableHead>
                    <TableHead>Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell className="font-mono font-bold text-navy">TKT-8821</TableCell>
                    <TableCell>
                      <div>
                        <span className="font-semibold text-navy block">Marcus Vance</span>
                        <span className="text-[10px] text-navy-muted">Order #88412</span>
                      </div>
                    </TableCell>
                    <TableCell>Damaged shipment photo verification</TableCell>
                    <TableCell>
                      <span className="flex items-center gap-1 text-[11px] text-navy-secondary">
                        <MessageSquare className="w-3 h-3 text-tealAccent" /> Web Chat
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge size="sm" variant="danger">High</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge size="sm" variant="danger" hasDot>Escalated</Badge>
                    </TableCell>
                    <TableCell className="text-status-danger font-semibold text-[11px]">
                      <Clock className="w-3 h-3 inline mr-1" /> 24m remaining
                    </TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">Open Details</Button>
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell className="font-mono font-bold text-navy">TKT-8819</TableCell>
                    <TableCell>
                      <div>
                        <span className="font-semibold text-navy block">Sarah Jenkins</span>
                        <span className="text-[10px] text-navy-muted">Appt Reschedule</span>
                      </div>
                    </TableCell>
                    <TableCell>Change Thursday 2pm to Friday morning</TableCell>
                    <TableCell>
                      <span className="flex items-center gap-1 text-[11px] text-navy-secondary">
                        <PhoneCall className="w-3 h-3 text-status-success" /> WhatsApp
                      </span>
                    </TableCell>
                    <TableCell>
                      <Badge size="sm" variant="teal">Medium</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge size="sm" variant="teal" hasDot>In Progress</Badge>
                    </TableCell>
                    <TableCell className="text-status-success font-semibold text-[11px]">
                      <Clock className="w-3 h-3 inline mr-1" /> 2h 45m left
                    </TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">Open Details</Button>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TabContent>

            <TabContent value="feedback">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-3">
                <div className="p-4 rounded-standard bg-canvas border border-border-subtle space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-navy flex items-center gap-1.5">
                      <PhoneCall className="w-4 h-4 text-status-success" /> WhatsApp CSAT Delivery
                    </span>
                    <Badge size="sm" variant="success">Score: 4.8 / 5.0</Badge>
                  </div>
                  <p className="text-xs text-navy-muted">
                    Automated post-resolution WhatsApp surveys sent after ticket closure. 142 responses received this month.
                  </p>
                </div>

                <div className="p-4 rounded-standard bg-canvas border border-border-subtle space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs text-navy flex items-center gap-1.5">
                      <Mail className="w-4 h-4 text-blueAccent" /> Email CSAT Delivery
                    </span>
                    <Badge size="sm" variant="blue">Score: 4.6 / 5.0</Badge>
                  </div>
                  <p className="text-xs text-navy-muted">
                    Secure 1-click survey links sent via email. 94% customer resolution confirmation rate.
                  </p>
                </div>
              </div>
            </TabContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default ComplaintsTicketsPage;
