import React from 'react';
import { UploadCloud, Search, FileText, CheckCircle2, Clock, Filter } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Button, Badge, Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Tabs, TabList, TabTrigger, TabContent } from '../components/ui';

export const KnowledgeBasePage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-navy">Knowledge Base & RAG Index</h1>
          <p className="text-xs text-navy-muted">
            Module D • Document Management, Embeddings, Hybrid Retrieval, and Citation Tracking
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="primary" size="sm">
            <UploadCloud className="w-3.5 h-3.5 mr-1.5" />
            Upload New Document
          </Button>
        </div>
      </div>

      {/* Upload Dropzone Card */}
      <div className="bg-surface rounded-card p-6 border-2 border-dashed border-border-default hover:border-tealAccent transition text-center space-y-2 cursor-pointer shadow-subtle">
        <div className="w-10 h-10 rounded-full bg-tealAccent-light border border-tealAccent-border text-tealAccent flex items-center justify-center mx-auto">
          <UploadCloud className="w-5 h-5" />
        </div>
        <h3 className="font-bold text-xs text-navy">Upload Knowledge Files to Ingest</h3>
        <p className="text-[11px] text-navy-muted max-w-md mx-auto">
          Drag and drop PDF, DOCX, TXT, CSV, or Markdown files here. Files are automatically chunked, embedded via approved models, and stored in pgvector.
        </p>
        <span className="inline-block text-[10px] text-navy-secondary font-medium">
          Supported: PDF, DOCX, TXT, CSV, XLSX, MD, HTML • Max 25MB per document
        </span>
      </div>

      {/* Collections Tabs & Document Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div>
              <CardTitle>Ingested Knowledge Collections</CardTitle>
              <CardDescription>
                Documents chunked and indexed into pgvector for hybrid retrieval with reranking.
              </CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-navy-muted absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  placeholder="Filter documents..."
                  className="pl-8 pr-3 py-1 rounded-standard bg-canvas border border-border-default text-xs text-navy focus:outline-none"
                />
              </div>
              <Button size="sm" variant="outline">
                <Filter className="w-3 h-3 mr-1" /> Collections
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all">
            <TabList>
              <TabTrigger value="all">All Documents (18)</TabTrigger>
              <TabTrigger value="policies">Policies & FAQs (6)</TabTrigger>
              <TabTrigger value="products">Product Manuals (8)</TabTrigger>
              <TabTrigger value="services">Service SOPs (4)</TabTrigger>
            </TabList>

            <TabContent value="all">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Document Title</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Chunks</TableHead>
                    <TableHead>Embeddings Status</TableHead>
                    <TableHead>Freshness</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-status-danger" />
                        <div>
                          <span className="font-semibold text-navy block">Return_Refund_Policy_2026.pdf</span>
                          <span className="text-[10px] text-navy-muted">1.2 MB • PDF Document</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>Policies & FAQs</TableCell>
                    <TableCell>34 Chunks</TableCell>
                    <TableCell>
                      <Badge size="sm" variant="success" hasDot>
                        <CheckCircle2 className="w-3 h-3 mr-1 inline" /> Indexed (pgvector)
                      </Badge>
                    </TableCell>
                    <TableCell className="text-navy-muted text-[11px]">Updated 2d ago</TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">View Chunks</Button>
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-blueAccent" />
                        <div>
                          <span className="font-semibold text-navy block">Dental_Implants_Care_Guide.docx</span>
                          <span className="text-[10px] text-navy-muted">840 KB • DOCX Document</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>Service SOPs</TableCell>
                    <TableCell>52 Chunks</TableCell>
                    <TableCell>
                      <Badge size="sm" variant="success" hasDot>
                        <CheckCircle2 className="w-3 h-3 mr-1 inline" /> Indexed (pgvector)
                      </Badge>
                    </TableCell>
                    <TableCell className="text-navy-muted text-[11px]">Updated 1w ago</TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">View Chunks</Button>
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-tealAccent" />
                        <div>
                          <span className="font-semibold text-navy block">Warranty_Terms_Q4.md</span>
                          <span className="text-[10px] text-navy-muted">140 KB • Markdown Document</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>Policies & FAQs</TableCell>
                    <TableCell>12 Chunks</TableCell>
                    <TableCell>
                      <Badge size="sm" variant="teal" hasDot>
                        <Clock className="w-3 h-3 mr-1 inline" /> Re-indexing
                      </Badge>
                    </TableCell>
                    <TableCell className="text-navy-muted text-[11px]">Updated 1h ago</TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">View Chunks</Button>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TabContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default KnowledgeBasePage;
