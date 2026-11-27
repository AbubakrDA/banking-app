export type Language = 'en' | 'ar';

export type UserRole =
  | 'customer'
  | 'employee'
  | 'risk_officer'
  | 'admin'
  | 'hr'
  | 'marketing';

export interface BankAccount {
  id: string;
  customer_id: string;
  account_number_masked: string;
  account_type: string;
  currency: string;
  balance_minor: number;
  status: string;
  created_at: string;
}

export interface BankTransaction {
  id: string;
  account_id: string;
  customer_id: string;
  tx_type: string;
  amount_minor: number;
  currency: string;
  description: string;
  counterparty_masked?: string | null;
  occurred_at: string;
}

export interface BankTransfer {
  id: string;
  from_account_id: string;
  to_account_id: string;
  customer_id: string;
  requested_by_user_id: string;
  amount_minor: number;
  currency: string;
  reference?: string | null;
  status: string;
  risk_score: number;
  idempotency_key?: string | null;
  is_cross_border: boolean;
  created_at: string;
}

export interface BankCard {
  id: string;
  account_id: string;
  customer_id: string;
  card_last4: string;
  card_type: string;
  status: 'active' | 'blocked';
  created_at: string;
}

export interface CustomerMasked {
  id: string;
  name: string;
  email_masked?: string | null;
  national_id_masked: string;
  tier: string;
}

export interface RiskAlert {
  id: string;
  customer_id: string;
  account_id?: string | null;
  transfer_id?: string | null;
  severity: string;
  risk_score: number;
  summary: string;
  status: string;
  created_at: string;
}

export interface PolicyDocument {
  id: string;
  title: string;
  filename: string;
  status: 'pending' | 'approved' | 'rejected';
  uploaded_by_user_id: string;
  page_count: number;
  created_at: string;
}

export interface AuditEntry {
  id: string;
  actor_id: string;
  actor_role: string;
  event_type: string;
  target_resource: string;
  status: string;
  prev_hash?: string | null;
  event_hash: string;
  created_at: string;
}

export interface ChatResponse {
  reply: string;
  language: string;
  intent: string;
  citations: Array<{
    policy_id: string;
    title: string;
    page_number: number;
    snippet: string;
  }>;
  blocked: boolean;
  tool_used?: string | null;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
  } | null;
}
