import React, { useEffect, useState } from 'react';
import {
  apiRequest,
  applyDocumentDirection,
  BankAccount,
  BankCard,
  BankTransaction,
  BankTransfer,
  ChatResponse,
  formatMinorCurrency,
  Language,
  setAccessToken,
  translations,
} from '@shared/index';

export const App: React.FC = () => {
  const [lang, setLang] = useState<Language>('en');
  const t = translations[lang];

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLocked, setIsLocked] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [transactions, setTransactions] = useState<BankTransaction[]>([]);
  const [cards, setCards] = useState<BankCard[]>([]);

  const [fromAcct, setFromAcct] = useState('');
  const [toAcct, setToAcct] = useState('');
  const [amountMinor, setAmountMinor] = useState('1000');
  const [reference, setReference] = useState('');
  const [pendingIdempotencyKey, setPendingIdempotencyKey] = useState<string | null>(null);
  const [transferMsg, setTransferMsg] = useState<string | null>(null);

  const [chatInput, setChatInput] = useState('');
  const [chatReply, setChatReply] = useState<ChatResponse | null>(null);
  const [policyModalOpen, setPolicyModalOpen] = useState(false);

  useEffect(() => {
    applyDocumentDirection(lang);
  }, [lang]);

  // Mobile security: lock session & hide sensitive balances when app goes to background
  useEffect(() => {
    const onVisibilityChange = () => {
      if (document.hidden && isAuthenticated) {
        setIsLocked(true);
      }
    };
    document.addEventListener('visibilitychange', onVisibilityChange);
    return () => document.removeEventListener('visibilitychange', onVisibilityChange);
  }, [isAuthenticated]);

  // Accessibility: Escape closes open modal
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && policyModalOpen) {
        setPolicyModalOpen(false);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [policyModalOpen]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [acctList, txPage, cardList] = await Promise.all([
        apiRequest<BankAccount[]>('/api/v1/accounts'),
        apiRequest<{ items: BankTransaction[] }>('/api/v1/transactions?page=1&page_size=10'),
        apiRequest<BankCard[]>('/api/v1/cards'),
      ]);
      setAccounts(acctList);
      setTransactions(txPage.items);
      setCards(cardList);
      if (acctList.length > 0 && !fromAcct) {
        setFromAcct(acctList[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load banking data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokenRes = await apiRequest<{ access_token: string; role: string }>('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });
      if (tokenRes.role !== 'customer') {
        throw new Error('Customer portal accepts customer accounts only.');
      }
      setAccessToken(tokenRes.access_token);
      setIsAuthenticated(true);
      await loadDashboardData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setTransferMsg(null);
    const key = pendingIdempotencyKey || `xfer-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    setPendingIdempotencyKey(key);
    try {
      const res = await apiRequest<BankTransfer>('/api/v1/transfers', {
        method: 'POST',
        idempotencyKey: key,
        body: JSON.stringify({
          from_account_id: fromAcct,
          to_account_id: toAcct,
          amount_minor: Number(amountMinor),
          currency: 'USD',
          reference,
        }),
      });
      setPendingIdempotencyKey(null);
      setTransferMsg(`Transfer ${res.status} (${res.id})`);
      await loadDashboardData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Transfer failed (safe to retry with same key)');
    }
  };

  const handleCardToggle = async (card: BankCard) => {
    const nextStatus = card.status === 'active' ? 'blocked' : 'active';
    try {
      await apiRequest<BankCard>(`/api/v1/cards/${card.id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ status: nextStatus }),
      });
      await loadDashboardData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Card update failed');
    }
  };

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    try {
      const res = await apiRequest<ChatResponse>('/api/v1/chat', {
        method: 'POST',
        body: JSON.stringify({ message: chatInput }),
      });
      setChatReply(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat error');
    }
  };

  const handleLogout = () => {
    setAccessToken(null);
    setIsAuthenticated(false);
    setIsLocked(false);
    setAccounts([]);
    setTransactions([]);
    setCards([]);
  };

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', maxWidth: 960, margin: '0 auto', padding: 16 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>{t.appCustomerTitle}</h1>
        <div style={{ display: 'flex', gap: 8 }}>
          <button type="button" onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}>
            {t.languageToggle}
          </button>
          {isAuthenticated && (
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

      {!isAuthenticated ? (
        <form onSubmit={handleLogin} aria-label="customer-login-form">
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
      ) : isLocked ? (
        <section aria-label="biometric-lock-screen" style={{ padding: 24, border: '1px solid #cbd5e1' }}>
          <h2>{t.unlockTitle}</h2>
          <p>{t.privacyShield}</p>
          <button type="button" onClick={() => setIsLocked(false)}>
            {t.unlockButton}
          </button>
        </section>
      ) : loading ? (
        <p>{t.loading}</p>
      ) : (
        <main>
          <section aria-label="accounts-section">
            <h2>{t.accounts}</h2>
            {accounts.length === 0 ? (
              <p>{t.emptyAccounts}</p>
            ) : (
              <ul>
                {accounts.map((a) => (
                  <li key={a.id}>
                    {a.account_number_masked} ({a.account_type}) —{' '}
                    <strong>{formatMinorCurrency(a.balance_minor, a.currency, lang)}</strong>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section aria-label="transactions-section">
            <h2>{t.transactions}</h2>
            {transactions.length === 0 ? (
              <p>{t.emptyTransactions}</p>
            ) : (
              <ul>
                {transactions.map((tx) => (
                  <li key={tx.id}>
                    {tx.description} — {formatMinorCurrency(tx.amount_minor, tx.currency, lang)}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section aria-label="transfer-section">
            <h2>{t.transfer}</h2>
            <form onSubmit={handleTransfer}>
              <input
                aria-label="from-account"
                placeholder="From Account ID"
                value={fromAcct}
                onChange={(e) => setFromAcct(e.target.value)}
                required
              />
              <input
                aria-label="to-account"
                placeholder="To Account ID"
                value={toAcct}
                onChange={(e) => setToAcct(e.target.value)}
                required
              />
              <input
                aria-label="amount-minor"
                type="number"
                value={amountMinor}
                onChange={(e) => setAmountMinor(e.target.value)}
                required
              />
              <input
                aria-label="reference"
                placeholder={t.referenceLabel}
                value={reference}
                onChange={(e) => setReference(e.target.value)}
              />
              <button type="submit">{t.sendTransfer}</button>
            </form>
            {transferMsg && <p>{transferMsg}</p>}
          </section>

          <section aria-label="cards-section">
            <h2>{t.cards}</h2>
            {cards.map((c) => (
              <div key={c.id}>
                <span>
                  ****{c.card_last4} ({c.status})
                </span>
                <button type="button" onClick={() => handleCardToggle(c)}>
                  {c.status === 'active' ? t.blockCard : t.unblockCard}
                </button>
              </div>
            ))}
          </section>

          <section aria-label="chat-section">
            <h2>{t.aiAssistant}</h2>
            <form onSubmit={handleChat}>
              <input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder={t.askPlaceholder}
              />
              <button type="submit">{t.send}</button>
            </form>
            {chatReply && (
              <div>
                <p>{chatReply.reply}</p>
                {chatReply.citations.length > 0 && (
                  <button type="button" onClick={() => setPolicyModalOpen(true)}>
                    View Policy Citations ({chatReply.citations.length})
                  </button>
                )}
              </div>
            )}
          </section>

          {policyModalOpen && chatReply && (
            <div role="dialog" aria-modal="true" aria-label="policy-citations-modal">
              <h3>Policy Citations</h3>
              <ul>
                {chatReply.citations.map((c) => (
                  <li key={`${c.policy_id}-${c.page_number}`}>
                    {c.title} (p.{c.page_number}): {c.snippet}
                  </li>
                ))}
              </ul>
              <button type="button" onClick={() => setPolicyModalOpen(false)}>
                Close
              </button>
            </div>
          )}
        </main>
      )}
    </div>
  );
};
