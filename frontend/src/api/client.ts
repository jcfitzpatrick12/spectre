/**
 * Thin wrapper around the Spectre backend HTTP API.
 *
 * All backend responses use the JSend spec:
 *   success -> { status: 'success', data: <T> }
 *   fail    -> { status: 'fail',    data: <object with field errors> }
 *   error   -> { status: 'error',   message: <string>, code?: number }
 *
 * See backend/src/spectre_server/routes/_format_responses.py.
 *
 * Requests go through the Vite dev proxy: everything is prefixed with `/api`
 * which strips to the backend root (see vite.config.ts).
 */

export const API_BASE = '/api';

export class SpectreApiError extends Error {
  readonly status: 'fail' | 'error' | 'http';
  readonly httpStatus: number;
  readonly payload: unknown;

  constructor(
    message: string,
    status: 'fail' | 'error' | 'http',
    httpStatus: number,
    payload: unknown,
  ) {
    super(message);
    this.name = 'SpectreApiError';
    this.status = status;
    this.httpStatus = httpStatus;
    this.payload = payload;
  }
}

type JSendSuccess<T> = { status: 'success'; data: T };
type JSendFail = { status: 'fail'; data: unknown };
type JSendError = { status: 'error'; message: string; code?: number; data?: unknown };
type JSend<T> = JSendSuccess<T> | JSendFail | JSendError;

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  query?: Record<string, string | number | boolean | ReadonlyArray<string | number> | undefined | null>;
  body?: unknown;
  signal?: AbortSignal;
  /** Skip JSend unwrap; used for endpoints that return raw file streams. */
  raw?: boolean;
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const url = new URL(
    API_BASE + (path.startsWith('/') ? path : `/${path}`),
    window.location.origin,
  );
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v === undefined || v === null) continue;
      if (Array.isArray(v)) {
        for (const item of v) url.searchParams.append(k, String(item));
      } else {
        url.searchParams.set(k, String(v));
      }
    }
  }
  return url.pathname + url.search;
}

export async function spectreFetch<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const url = buildUrl(path, opts.query);
  const headers: Record<string, string> = {};
  let body: BodyInit | undefined;
  if (opts.body !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(opts.body);
  }

  const res = await fetch(url, {
    method: opts.method ?? 'GET',
    headers,
    body,
    signal: opts.signal,
  });

  if (opts.raw) {
    if (!res.ok) {
      throw new SpectreApiError(`HTTP ${res.status}`, 'http', res.status, null);
    }
    return res as unknown as T;
  }

  let payload: JSend<T> | null = null;
  try {
    payload = (await res.json()) as JSend<T>;
  } catch {
    throw new SpectreApiError(
      `Non-JSON response (HTTP ${res.status})`,
      'http',
      res.status,
      null,
    );
  }

  if (payload.status === 'success') {
    return payload.data;
  }
  if (payload.status === 'fail') {
    throw new SpectreApiError(
      `Request failed: ${JSON.stringify(payload.data)}`,
      'fail',
      res.status,
      payload.data,
    );
  }
  // 'error'
  throw new SpectreApiError(payload.message, 'error', res.status, payload.data ?? null);
}
