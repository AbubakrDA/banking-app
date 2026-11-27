import React, { useState } from 'react';
import {
  Search,
  Paperclip,
  Send,
  AlertTriangle,
  User,
  Brain,
  History,
  Tag,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { Badge, Button } from '../components/ui';

interface MockConversation {
  id: string;
  customerName: string;
  preview: string;
  time: string;
  status: 'active' | 'escalated' | 'resolved';
  sentiment: 'positive' | 'neutral' | 'frustrated';
}

const mockConversations: MockConversation[] = [
  {
    id: 'conv-101',
    customerName: 'Sarah Jenkins',
    preview: 'How do I reschedule my dental appointment for tomorrow?',
    time: '2m ago',
    status: 'active',
    sentiment: 'neutral',
  },
  {
    id: 'conv-102',
    customerName: 'Marcus Vance',
    preview: 'Received damaged shipment for Order #88412 with photo attached.',
    time: '14m ago',
    status: 'escalated',
    sentiment: 'frustrated',
  },
  {
    id: 'conv-103',
    customerName: 'Elena Rostova',
    preview: 'Thank you, the invoice copy was received correctly!',
    time: '1h ago',
    status: 'resolved',
    sentiment: 'positive',
  },
];

export const AIChatAgentPage: React.FC = () => {
  const [selectedConv, setSelectedConv] = useState<MockConversation>(mockConversations[0]);
  const [inputMessage, setInputMessage] = useState<string>('');

  return (
    <div className="space-y-4">
      {/* Page Title & Status */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-2">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-navy">
            AI Customer Support Chat Workspace
          </h1>
          <p className="text-xs text-navy-muted">
            Module A • Autonomous Multi-Turn Agent with Controlled Handover & Customer Memory
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="teal" hasDot>
            BankingAIPlatform Agent Live
          </Badge>
          <Badge variant="neutral">
            Business Mode: Products & Services
          </Badge>
        </div>
      </div>

      {/* 3-Column Support Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 h-[calc(100vh-210px)] min-h-[580px]">
        {/* Left Column: Conversation Queue (3 cols) */}
        <div className="lg:col-span-3 bg-surface rounded-card border border-border-subtle shadow-card flex flex-col overflow-hidden">
          <div className="p-3 border-b border-border-subtle space-y-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-navy-muted absolute left-2.5 top-2.5 pointer-events-none" />
              <input
                type="text"
                placeholder="Search conversations..."
                className="w-full pl-8 pr-3 py-1.5 rounded-standard bg-canvas border border-border-default text-xs text-navy placeholder:text-navy-muted focus:outline-none focus:border-border-focus"
              />
            </div>
            <div className="flex items-center gap-1 text-[11px]">
              <span className="px-2 py-0.5 rounded-standard bg-tealAccent-light text-tealAccent font-semibold cursor-pointer">
                All (3)
              </span>
              <span className="px-2 py-0.5 rounded-standard text-navy-muted hover:bg-surface-subdued cursor-pointer">
                Active
              </span>
              <span className="px-2 py-0.5 rounded-standard text-navy-muted hover:bg-surface-subdued cursor-pointer">
                Escalated
              </span>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-border-subtle">
            {mockConversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => setSelectedConv(conv)}
                className={`p-3 text-left cursor-pointer transition ${
                  selectedConv.id === conv.id
                    ? 'bg-tealAccent-light/60 border-l-4 border-tealAccent'
                    : 'hover:bg-surface-hover'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-xs text-navy truncate">
                    {conv.customerName}
                  </span>
                  <span className="text-[10px] text-navy-muted">{conv.time}</span>
                </div>
                <p className="text-[11px] text-navy-secondary line-clamp-2 leading-relaxed">
                  {conv.preview}
                </p>
                <div className="flex items-center gap-1.5 mt-2">
                  <Badge
                    size="sm"
                    variant={
                      conv.status === 'active'
                        ? 'teal'
                        : conv.status === 'escalated'
                        ? 'danger'
                        : 'success'
                    }
                  >
                    {conv.status}
                  </Badge>
                  {conv.sentiment === 'frustrated' && (
                    <span className="text-[10px] text-status-danger font-medium flex items-center gap-0.5">
                      <AlertTriangle className="w-3 h-3" /> Sentiment
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Center Column: Live Conversation Window (6 cols) */}
        <div className="lg:col-span-6 bg-surface rounded-card border border-border-subtle shadow-card flex flex-col overflow-hidden">
          {/* Conversation Header */}
          <div className="p-3.5 border-b border-border-subtle flex items-center justify-between bg-surface-subdued/50">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-full bg-navy-100 text-navy font-bold text-xs flex items-center justify-center">
                {selectedConv.customerName.charAt(0)}
              </div>
              <div>
                <h3 className="font-bold text-xs text-navy">{selectedConv.customerName}</h3>
                <span className="text-[10px] text-navy-muted">
                  Channel: Support Web Chat • Verified Customer
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button size="sm" variant="outline">
                Assign Agent
              </Button>
              <Button size="sm" variant="secondary">
                Handover to Human
              </Button>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-canvas/40">
            {/* Customer Message */}
            <div className="flex items-start space-x-2.5 max-w-[85%]">
              <div className="w-7 h-7 rounded-full bg-navy-200 text-navy font-bold text-xs flex items-center justify-center shrink-0">
                SJ
              </div>
              <div className="bg-surface rounded-card p-3.5 border border-border-subtle shadow-subtle text-xs text-navy leading-relaxed space-y-1">
                <span className="font-semibold text-[11px] text-navy-muted block">
                  Sarah Jenkins • 10:14 AM
                </span>
                <p>
                  Hi there, I have an appointment scheduled for tomorrow at 2:00 PM with Dr. Harris. Can I reschedule this to Friday morning instead?
                </p>
              </div>
            </div>

            {/* AI Agent Response */}
            <div className="flex items-start space-x-2.5 max-w-[85%] ml-auto flex-row-reverse space-x-reverse">
              <div className="w-7 h-7 rounded-full bg-tealAccent text-white font-bold text-xs flex items-center justify-center shrink-0 shadow-subtle">
                AI
              </div>
              <div className="bg-tealAccent-light/70 rounded-card p-3.5 border border-tealAccent-border text-xs text-navy leading-relaxed space-y-2">
                <div className="flex items-center justify-between text-[11px] text-tealAccent font-semibold">
                  <span>BankingAIPlatform AI Agent</span>
                  <span className="flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" /> Grounded in Business Hub
                  </span>
                </div>
                <p>
                  Hello Sarah! I checked Dr. Harris’s schedule in our Business Data Hub. He has two available openings on Friday:
                </p>
                <ul className="list-disc list-inside space-y-0.5 text-navy-secondary">
                  <li>Friday at 9:30 AM</li>
                  <li>Friday at 11:00 AM</li>
                </ul>
                <p>
                  Would either of those times work for you? Once confirmed, I can update your appointment automatically.
                </p>
                <div className="pt-1 flex items-center gap-1.5 text-[10px] text-navy-muted">
                  <Tag className="w-3 h-3 text-tealAccent" />
                  <span>Sources: appointments_calendar, service_policy.pdf</span>
                </div>
              </div>
            </div>
          </div>

          {/* Message Input Box */}
          <div className="p-3 border-t border-border-subtle bg-surface">
            <div className="flex items-center space-x-2">
              <button
                type="button"
                className="p-2 rounded-standard text-navy-muted hover:bg-surface-subdued hover:text-navy transition"
                title="Attach Document or Image (JPG, PNG, PDF)"
              >
                <Paperclip className="w-4 h-4" />
              </button>
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type instructions or respond to customer..."
                className="flex-1 py-2 px-3 rounded-standard bg-canvas border border-border-default text-xs text-navy focus:outline-none focus:border-border-focus"
              />
              <Button size="md" variant="primary">
                <Send className="w-3.5 h-3.5 mr-1" />
                Send
              </Button>
            </div>
            <div className="flex items-center justify-between text-[10px] text-navy-muted mt-1.5 px-1">
              <span>Enter to send • Model: Controlled Agent Orchestration</span>
              <span className="text-tealAccent font-medium flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" /> RAG & Memory Active
              </span>
            </div>
          </div>
        </div>

        {/* Right Column: Customer Context & Memory (3 cols) */}
        <div className="lg:col-span-3 bg-surface rounded-card border border-border-subtle shadow-card p-4 space-y-4 overflow-y-auto">
          <div className="flex items-center space-x-2 border-b border-border-subtle pb-3">
            <User className="w-4 h-4 text-tealAccent" />
            <h3 className="font-bold text-xs text-navy">Customer Context & Memory</h3>
          </div>

          {/* Profile Card */}
          <div className="p-3 rounded-standard bg-canvas border border-border-subtle space-y-1.5 text-xs">
            <span className="text-[10px] font-semibold text-navy-muted uppercase">Customer Profile</span>
            <p className="font-bold text-navy">{selectedConv.customerName}</p>
            <p className="text-[11px] text-navy-muted">sarah.j@example.com</p>
            <p className="text-[11px] text-navy-muted">+1 (555) 349-1823</p>
            <div className="pt-1 flex gap-1">
              <Badge size="sm" variant="blue">Tier: Premium</Badge>
              <Badge size="sm" variant="neutral">3 Orders</Badge>
            </div>
          </div>

          {/* Working Memory */}
          <div className="space-y-1.5 text-xs">
            <div className="flex items-center space-x-1.5 font-semibold text-navy">
              <Brain className="w-3.5 h-3.5 text-tealAccent" />
              <span>Working Memory</span>
            </div>
            <div className="p-2.5 rounded-standard bg-surface-subdued text-[11px] text-navy-secondary leading-relaxed">
              Seeking to reschedule Thursday 2:00 PM appointment with Dr. Harris to Friday morning.
            </div>
          </div>

          {/* Episodic Memory */}
          <div className="space-y-1.5 text-xs">
            <div className="flex items-center space-x-1.5 font-semibold text-navy">
              <History className="w-3.5 h-3.5 text-blueAccent" />
              <span>Episodic Memory</span>
            </div>
            <div className="space-y-1.5 text-[11px]">
              <div className="p-2 rounded-standard bg-canvas border border-border-subtle">
                <span className="font-semibold text-navy block">Order #77124 Delivered</span>
                <span className="text-navy-muted text-[10px]">Nov 12, 2026 • Dental Floss Pack</span>
              </div>
              <div className="p-2 rounded-standard bg-canvas border border-border-subtle">
                <span className="font-semibold text-navy block">Inquiry: Insurance Policy</span>
                <span className="text-navy-muted text-[10px]">Oct 28, 2026 • Resolved by AI</span>
              </div>
            </div>
          </div>

          {/* Semantic Memory */}
          <div className="space-y-1.5 text-xs">
            <span className="font-semibold text-navy block">Semantic Preferences</span>
            <div className="flex flex-wrap gap-1">
              <Badge size="sm" variant="neutral">Prefers Morning Appts</Badge>
              <Badge size="sm" variant="neutral">Email Confirmations</Badge>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIChatAgentPage;
