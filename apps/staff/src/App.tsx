import React, { useEffect, useState } from 'react';
import {
  apiRequest,
  applyDocumentDirection,
  AuditEntry,
  BankTransfer,
  CustomerMasked,
  formatMinorCurrency,
  Language,
  PolicyDocument,
  RiskAlert,
  setAccessToken,
  translations,
  UserRole,
} from '@shared/index';

const STAFF_IDLE_TIMEOUT_MS = 10 * 60 * 1000;

export const App: React.FC = () => {
  const [lang, setLang] = useState<Language>('en');
  const t = translations[lang];

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [accessReason, setAccessReason] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [customers, setCustomers] = useState<CustomerMasked[]>([]);

  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [approvals, setApprovals] = useState<BankTransfer[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditEntry[]>([]);
  const [chainValid, setChainValid] = useState<string | null>(null);
  const [policies, setPolicies] = useState<PolicyDocument[]>([]);

  useEffect(() => {
    applyDocumentDirection(lang);
  }, [lang]);

  // Staff session idle timeout (default 10 minutes)
  useEffect(() => {
    if (!role) return;
    let timer = setTimeout(() => {
      setAccessToken(null);
      setRole(null);
      setError('Staff session expired after 10 minutes idle.');
    }, STAFF_IDLE_TIMEOUT_MS);

    const resetTimer = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        setAccessToken(null);
        setRole(null);
      }, STAFF_IDLE_TIMEOUT_MS);
    };
    window.addEventListener('keydown', resetTimer);
    window.addEventListener('pointerdown', resetTimer);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('keydown', resetTimer);
      window.removeEventListener('pointerdown', resetTimer);
    };
  }, [role]);

  const loadRoleWorkspace = async (staffRole: UserRole) => {
    setLoading(true);
    setError(null);
    try {
      const pols = await apiRequest<PolicyDocument[]>('/api/v1/policies');
      setPolicies(pols);

      if (staffRole === 'risk_officer' || staffRole === 'admin') {
        const [riskList, appList, audList] = await Promise.all([
          apiRequest<RiskAlert[]>('/api/v1/risk/alerts'),
          apiRequest<BankTransfer[]>('/api/v1/approvals'),
          apiRequest<AuditEntry[]>('/api/v1/audit'),
        ]);
        setAlerts(riskList);
        setApprovals(appList);
        setAuditLogs(audList);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load staff workspace');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await apiRequest<{ access_token: string; role: UserRole }>('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      if (res.role === 'customer') {
        throw new Error('Staff portal refuses customer credentials.');
      }
      setAccessToken(res.access_token);
      setRole(res.role);
      await loadRoleWorkspace(res.role);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Staff login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomerSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!accessReason.trim()) {
      setError('Written access reason is required.');
      return;
    }
    try {
      const res = await apiRequest<CustomerMasked[]>(
        `/api/v1/customers/search?q=${encodeURIComponent(searchQuery)}`,
        { accessReason }
      );
      setCustomers(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Customer search failed');
    }
  };

  const handleDecision = async (transferId: string, decision: 'approve' | 'reject') => {
    try {
      await apiRequest<BankTransfer>(`/api/v1/approvals/${transferId}/${decision}`, {
        method: 'POST',
        body: JSON.stringify({ reason: `${decision} via staff portal` }),
      });
      if (role) await loadRoleWorkspace(role);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Decision failed');
    }
  };

  const handleVerifyAudit = async () => {
    try {
      const res = await apiRequest<{ valid: boolean; checked_count: number }>('/api/v1/audit/verify');
      setChainValid(res.valid ? `Valid (${res.checked_count} entries)` : 'Tamper detected');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Audit verification failed');
    }
  };

  const handleLogout = () => {
    setAccessToken(null);
    setRole(null);
    setCustomers([]);
    setAlerts([]);
    setApprovals([]);
    setAuditLogs([]);
  };

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', maxWidth: 1080, margin: '0 auto', padding: 16 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h1>{t.appStaffTitle}</h1>
          <small>{t.idleWarning}</small>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button type="button" onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}>
            {t.languageToggle}
          </button>
          {role && (
            <button type="button" onClick={handleLogout}>
              {t.signOut}
            </button>
          )}
        </div>
      </header>

      {error && (
        <div role="alert" style={{ background: '#fee2e2', color: '#991b1b', padding: 12, marginBottom: 12 }}>
          {error}
        </div>
      )}

      {!role ? (
        <form onSubmit={handleLogin} aria-label="staff-login-form">
          <label>
            {t.email}
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label>
            {t.password}
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          <button type="submit" disabled={loading}>
            {t.signIn}
          </button>
        </form>
      ) : loading ? (
        <p>{t.loading}</p>
      ) : role === 'hr' || role === 'marketing' ? (
        <main aria-label="department-restricted-view">
          <p>{t.departmentRestricted}</p>
          <h2>{t.policies}</h2>
          {policies.length === 0 ? (
            <p>{t.emptyPolicies}</p>
          ) : (
            <ul>
              {policies.map((p) => (
                <li key={p.id}>
                  {p.title} ({p.status})
                </li>
              ))}
            </ul>
          )}
        </main>
      ) : (
        <main>
          {(role === 'employee' || role === 'risk_officer' || role === 'admin') && (
            <section aria-label="customer-search-section">
              <h2>{t.searchCustomers}</h2>
              <form onSubmit={handleCustomerSearch}>
                <input
                  aria-label="access-reason"
                  placeholder={t.staffReasonLabel}
                  value={accessReason}
                  onChange={(e) => setAccessReason(e.target.value)}
                />
                <input
                  aria-label="search-query"
                  placeholder="Customer name"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <button type="submit">{t.searchCustomers}</button>
              </form>
              <ul>
                {customers.map((c) => (
                  <li key={c.id}>
                    {c.name} — {c.national_id_masked} ({c.tier})
                  </li>
                ))}
              </ul>
            </section>
          )}

          {(role === 'risk_officer' || role === 'admin') && (
            <>
              <section aria-label="risk-alerts-section">
                <h2>{t.riskAlerts}</h2>
                {alerts.length === 0 ? (
                  <p>{t.emptyAlerts}</p>
                ) : (
                  <ul>
                    {alerts.map((a) => (
                      <li key={a.id}>
                        [{a.severity}] {a.summary} (score: {a.risk_score})
                      </li>
                    ))}
                  </ul>
                )}
              </section>

              <section aria-label="approvals-section">
                <h2>{t.approvalsQueue}</h2>
                {approvals.length === 0 ? (
                  <p>{t.emptyApprovals}</p>
                ) : (
                  <ul>
                    {approvals.map((ap) => (
                      <li key={ap.id}>
                        {formatMinorCurrency(ap.amount_minor, ap.currency, lang)} — {ap.reference || ap.id}
                        {role === 'admin' && (
                          <>
                            <button type="button" onClick={() => handleDecision(ap.id, 'approve')}>
                              {t.approve}
                            </button>
                            <button type="button" onClick={() => handleDecision(ap.id, 'reject')}>
                              {t.reject}
                            </button>
                          </>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </section>

              <section aria-label="audit-section">
                <h2>{t.auditLog}</h2>
                <button type="button" onClick={handleVerifyAudit}>
                  {t.verifyChain}
                </button>
                {chainValid && <p>{chainValid}</p>}
                <ul>
                  {auditLogs.slice(0, 10).map((log) => (
                    <li key={log.id}>
                      {log.event_type} ({log.status}) — {log.target_resource}
                    </li>
                  ))}
                </ul>
              </section>
            </>
          )}
        </main>
      )}
    </div>
  );
};
