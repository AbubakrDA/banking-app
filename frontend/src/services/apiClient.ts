/**
 * Typed API client foundation for BankingAIPlatform.
 * Uses in-memory token storage (never localStorage) to mitigate XSS token theft.
 */

const DEFAULT_API_BASE = 'http://localhost:8000/api/v1';

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) || DEFAULT_API_BASE;

let inMemoryAccessToken: string | null = null;

export function setInMemoryAccessToken(token: string | null): void {
  inMemoryAccessToken = token;
}

export function clearInMemoryAccessToken(): void {
  inMemoryAccessToken = null;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error: { code: string; message: string; details?: unknown } | null;
  meta: { request_id?: string | null; tenant_id?: string | null };
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit = {},
  timeoutMs = 10000
): Promise<ApiEnvelope<T>> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const headers = new Headers(init.headers);
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json');
  }
  if (inMemoryAccessToken && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${inMemoryAccessToken}`);
  }

  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers,
      credentials: 'include',
      signal: controller.signal,
    });
    return (await res.json()) as ApiEnvelope<T>;
  } finally {
    clearTimeout(timer);
  }
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await apiFetch<{ status: string }>('/health', { method: 'GET' }, 3000);
    return Boolean(res.success);
  } catch {
    return false;
  }
}
