import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { App } from '../App';

describe('Staff Operations App', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    document.documentElement.dir = 'ltr';
  });

  it('refuses customer login on staff portal', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ success: true, data: { access_token: 'tok-cust', role: 'customer' } }),
      })
    );

    render(<App />);
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'layla@bank.local' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() =>
      expect(screen.getByRole('alert')).toHaveTextContent('Staff portal refuses customer credentials.')
    );
  });

  it('renders restricted policy-only view for HR role and never shows accounts or balances', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.endsWith('/api/v1/auth/login')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true, data: { access_token: 'tok-hr', role: 'hr' } }),
          });
        }
        if (url.endsWith('/api/v1/policies')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              success: true,
              data: [
                {
                  id: 'p1',
                  title: 'HR Conduct Policy',
                  filename: 'hr.pdf',
                  status: 'approved',
                  uploaded_by_user_id: 'admin_1',
                  page_count: 1,
                  created_at: '2026-01-01T00:00:00Z',
                },
              ],
            }),
          });
        }
        return Promise.resolve({ ok: false, status: 403, json: async () => ({ success: false }) });
      })
    );

    render(<App />);
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'hr@bank.local' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => expect(screen.getByLabelText('department-restricted-view')).toBeInTheDocument());
    expect(screen.getByText(/HR Conduct Policy/)).toBeInTheDocument();
    expect(screen.queryByLabelText('risk-alerts-section')).not.toBeInTheDocument();
  });

  it('renders risk officer alerts and requires written reason for customer search', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockImplementation((url: string) => {
        if (url.endsWith('/api/v1/auth/login')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ success: true, data: { access_token: 'tok-risk', role: 'risk_officer' } }),
          });
        }
        return Promise.resolve({
          ok: true,
          json: async () => ({ success: true, data: [] }),
        });
      })
    );

    render(<App />);
    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'risk@bank.local' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => expect(screen.getByText('No active risk alerts.')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: 'Search Customers' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Written access reason is required.');
  });
});
