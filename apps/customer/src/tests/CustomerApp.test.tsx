import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { App } from '../App';

describe('Customer Banking App', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    document.documentElement.dir = 'ltr';
  });

  it('toggles Arabic RTL direction on language switch', () => {
    render(<App />);
    const toggle = screen.getByRole('button', { name: 'العربية' });
    fireEvent.click(toggle);
    expect(document.documentElement.dir).toBe('rtl');
    expect(screen.getByText('بوابة عملاء كونفيرسا بنك')).toBeInTheDocument();
  });

  it('renders populated state, handles background lock, and shows error state', async () => {
    const fetchMock = vi.fn().mockImplementation((url: string) => {
      if (url.endsWith('/api/v1/auth/login')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ success: true, data: { access_token: 'tok-cust', role: 'customer' } }),
        });
      }
      if (url.endsWith('/api/v1/accounts')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({
            success: true,
            data: [
              {
                id: 'a1',
                customer_id: 'c1',
                account_number_masked: '****1042',
                account_type: 'checking',
                currency: 'USD',
                balance_minor: 250000,
                status: 'active',
                created_at: '2026-01-01T00:00:00Z',
              },
            ],
          }),
        });
      }
      if (url.includes('/api/v1/transactions')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ success: true, data: { items: [] } }),
        });
      }
      if (url.endsWith('/api/v1/cards')) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ success: true, data: [] }),
        });
      }
      return Promise.resolve({
        ok: false,
        status: 500,
        json: async () => ({ success: false, error: { code: 'ERR', message: 'Backend down' } }),
      });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'layla@bank.local' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => expect(screen.getByText(/\*\*\*\*1042/)).toBeInTheDocument());
    expect(screen.getByText('No transactions found.')).toBeInTheDocument();

    // Simulate app going to background -> privacy shield + biometric lock
    Object.defineProperty(document, 'hidden', { configurable: true, value: true });
    fireEvent(document, new Event('visibilitychange'));
    await waitFor(() => expect(screen.getByLabelText('biometric-lock-screen')).toBeInTheDocument());
    expect(screen.queryByText(/\*\*\*\*1042/)).not.toBeInTheDocument();

    // Unlock restores view
    Object.defineProperty(document, 'hidden', { configurable: true, value: false });
    fireEvent.click(screen.getByRole('button', { name: /Unlock/i }));
    await waitFor(() => expect(screen.getByText(/\*\*\*\*1042/)).toBeInTheDocument());
  });

  it('displays error banner when login fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: async () => ({ success: false, error: { code: 'HTTP_401', message: 'Invalid credentials' } }),
      })
    );

    render(<App />);
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'bad@bank.local' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'wrongpass' } });
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('Invalid credentials'));
  });
});
