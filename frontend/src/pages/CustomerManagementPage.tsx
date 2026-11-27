import React from 'react';
import { Search, Filter } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge, Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Input } from '../components/ui';

export const CustomerManagementPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-navy">Customer Directory & Memory Store</h1>
          <p className="text-xs text-navy-muted">
            Module C • Working Context, Episodic Interaction Records, and Long-Term Semantic Customer Preferences
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="primary" size="sm">+ New Customer</Button>
        </div>
      </div>

      {/* Customer Directory Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <CardTitle>Customer Intelligence Registry</CardTitle>
              <CardDescription>
                Profiles grounded in multi-tier memory to ensure AI agents retain context without memory poisoning.
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <Input
                placeholder="Search customers by name, email, phone..."
                leftIcon={<Search className="w-3.5 h-3.5" />}
                className="w-64"
              />
              <Button size="sm" variant="outline">
                <Filter className="w-3 h-3 mr-1" /> Filter
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Customer Name</TableHead>
                <TableHead>Contact Info</TableHead>
                <TableHead>Business Mode</TableHead>
                <TableHead>Total Interactions</TableHead>
                <TableHead>Memory Status</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>
                  <div className="flex items-center space-x-2.5">
                    <div className="w-7 h-7 rounded-full bg-tealAccent-light text-tealAccent font-bold text-xs flex items-center justify-center">
                      SJ
                    </div>
                    <div>
                      <span className="font-semibold text-navy block">Sarah Jenkins</span>
                      <span className="text-[10px] text-navy-muted">ID: cust_99214</span>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <p className="text-navy">sarah.j@example.com</p>
                  <p className="text-[10px] text-navy-muted">+1 (555) 349-1823</p>
                </TableCell>
                <TableCell>
                  <Badge size="sm" variant="teal">Services (Appointments)</Badge>
                </TableCell>
                <TableCell>14 Conversations</TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Badge size="sm" variant="success" hasDot>Working</Badge>
                    <Badge size="sm" variant="blue">Episodic (6)</Badge>
                    <Badge size="sm" variant="neutral">Semantic (2)</Badge>
                  </div>
                </TableCell>
                <TableCell>
                  <Button size="sm" variant="outline">Inspect Memory</Button>
                </TableCell>
              </TableRow>

              <TableRow>
                <TableCell>
                  <div className="flex items-center space-x-2.5">
                    <div className="w-7 h-7 rounded-full bg-blueAccent-light text-blueAccent font-bold text-xs flex items-center justify-center">
                      MV
                    </div>
                    <div>
                      <span className="font-semibold text-navy block">Marcus Vance</span>
                      <span className="text-[10px] text-navy-muted">ID: cust_99215</span>
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <p className="text-navy">marcus.vance@company.net</p>
                  <p className="text-[10px] text-navy-muted">+1 (555) 882-9910</p>
                </TableCell>
                <TableCell>
                  <Badge size="sm" variant="blue">Products (Orders)</Badge>
                </TableCell>
                <TableCell>8 Conversations</TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    <Badge size="sm" variant="warning" hasDot>Escalated</Badge>
                    <Badge size="sm" variant="blue">Episodic (3)</Badge>
                  </div>
                </TableCell>
                <TableCell>
                  <Button size="sm" variant="outline">Inspect Memory</Button>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default CustomerManagementPage;
