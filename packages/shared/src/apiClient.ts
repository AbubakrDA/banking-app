import { ApiEnvelope, Language } from './types';

// In-memory token store only — never persisted to localStorage or sessionStorage.
let inMemoryToken: string | null = null;

export function setAccessToken(token: string | null): void {
  inMemoryToken = token;
}

export function getAccessToken(): string | null {
  return inMemoryToken;
}

export function formatMinorCurrency(
  amountMinor: number,
  currency: string,
  lang: Language = 'en'
): string {
  const major = amountMinor / 100;
  try {
    return new Intl.NumberFormat(lang === 'ar' ? 'ar-EG' : 'en-US', {
      style: 'currency',
      currency,
    }).format(major);
  } catch {
    return `${currency} ${major.toFixed(2)}`;
  }
}

export interface RequestOptions extends RequestInit {
  accessReason?: string;
  idempotencyKey?: string;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const baseUrl =
    (typeof import.meta !== 'undefined' &&
      (import.meta as unknown as { env?: Record<string, string> }).env
        ?.VITE_API_BASE_URL) ||
    'http://127.0.0.1:8000';

  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }
  if (inMemoryToken) {
    headers.set('Authorization', `Bearer ${inMemoryToken}`);
  }
  if (options.accessReason) {
    headers.set('X-Access-Reason', options.accessReason);
  }
  if (options.idempotencyKey) {
    headers.set('Idempotency-Key', options.idempotencyKey);
  }

  const res = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
  });

  const payload = (await res.json()) as ApiEnvelope<T>;
  if (!res.ok || !payload.success) {
    throw new Error(payload.error?.message || `HTTP ${res.status}`);
  }
  return payload.data as T;
}
