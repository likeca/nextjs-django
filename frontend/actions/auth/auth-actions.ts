'use server';

/**
 * Auth server actions — every auth call to Django happens here, on the
 * Next.js server, over API_INTERNAL_BASE (container network). The browser
 * only ever talks to the Next.js origin.
 *
 * Tokens come back as cookies on the action response. They stay readable by
 * client JS (httpOnly: false) because lib/api/browser.ts attaches them to
 * proxied requests and reads the refresh token for its 401-retry flow.
 */
import { cookies, headers } from 'next/headers';

import { API_INTERNAL_BASE, ApiError, request } from '@/lib/api/client';
import { serverTry } from '@/lib/api/server';
import type { AuthUser } from '@/lib/auth-client';

const ACCESS = 'access_token';
const REFRESH = 'refresh_token';
const ACCESS_MAX_AGE = 60 * 30; // matches SimpleJWT access lifetime
const REFRESH_MAX_AGE = 60 * 60 * 24 * 7;

export type AuthResult<T> = { ok: true; data: T } | { ok: false; error: string };

function errMessage(e: unknown): string {
  if (e instanceof ApiError) return e.message;
  return e instanceof Error ? e.message : 'Request failed';
}

async function setTokenCookies(access: string, refresh?: string) {
  const store = await cookies();
  const h = await headers();
  const secure = (h.get('x-forwarded-proto') ?? '').includes('https');
  const base = { path: '/', sameSite: 'lax', secure, httpOnly: false } as const;
  store.set(ACCESS, access, { ...base, maxAge: ACCESS_MAX_AGE });
  if (refresh) store.set(REFRESH, refresh, { ...base, maxAge: REFRESH_MAX_AGE });
}

async function clearTokenCookies() {
  const store = await cookies();
  store.delete(ACCESS);
  store.delete(REFRESH);
}

interface LoginPayload {
  access?: string;
  refresh?: string;
  user?: AuthUser;
  twoFactorRequired?: boolean;
  preAuthToken?: string;
}

export async function loginAction(input: {
  email: string;
  password: string;
}): Promise<AuthResult<{ user?: AuthUser; twoFactorRequired?: boolean; preAuthToken?: string }>> {
  try {
    const res = await request<LoginPayload>('/api/auth/login/', {
      method: 'POST',
      body: input,
      baseUrl: API_INTERNAL_BASE,
    });
    // 2FA-enabled account: no tokens yet — hand the pre-auth token back.
    if (res.twoFactorRequired && res.preAuthToken) {
      return { ok: true, data: { twoFactorRequired: true, preAuthToken: res.preAuthToken } };
    }
    await setTokenCookies(res.access!, res.refresh);
    return { ok: true, data: { user: res.user } };
  } catch (e) {
    return { ok: false, error: errMessage(e) };
  }
}

export async function signupAction(input: {
  email: string;
  name: string;
  password: string;
}): Promise<AuthResult<{ user: AuthUser | null }>> {
  try {
    const res = await request<{ access?: string; refresh?: string; user?: AuthUser }>(
      '/api/auth/registration/',
      {
        method: 'POST',
        body: {
          email: input.email,
          name: input.name,
          password1: input.password,
          password2: input.password,
        },
        baseUrl: API_INTERNAL_BASE,
      },
    );
    if (res.access) await setTokenCookies(res.access, res.refresh);
    return { ok: true, data: { user: res.user ?? null } };
  } catch (e) {
    return { ok: false, error: errMessage(e) };
  }
}

export async function logoutAction(): Promise<AuthResult<null>> {
  await serverTry('/api/auth/logout/', { method: 'POST' }); // best-effort
  await clearTokenCookies();
  return { ok: true, data: null };
}

/** Session lookup for useSession — reads the JWT cookie server-side. */
export async function getSessionAction(): Promise<AuthUser | null> {
  const store = await cookies();
  if (!store.get(ACCESS)?.value) return null;
  const res = await serverTry<AuthUser>('/api/auth/user/');
  return 'data' in res ? res.data : null;
}

export async function changePasswordAction(input: {
  currentPassword: string;
  newPassword: string;
}): Promise<AuthResult<unknown>> {
  const res = await serverTry('/api/auth/password/change/', {
    method: 'POST',
    body: {
      old_password: input.currentPassword,
      new_password1: input.newPassword,
      new_password2: input.newPassword,
    },
  });
  return 'error' in res ? { ok: false, error: res.error } : { ok: true, data: res.data };
}

export async function requestPasswordResetAction(input: {
  email: string;
}): Promise<AuthResult<unknown>> {
  const res = await serverTry('/api/auth/password/reset/', { method: 'POST', body: input });
  return 'error' in res ? { ok: false, error: res.error } : { ok: true, data: res.data };
}

export async function resetPasswordAction(input: {
  uid: string;
  token: string;
  newPassword: string;
}): Promise<AuthResult<unknown>> {
  const res = await serverTry('/api/auth/password/reset/confirm/', {
    method: 'POST',
    body: {
      uid: input.uid,
      token: input.token,
      new_password1: input.newPassword,
      new_password2: input.newPassword,
    },
  });
  return 'error' in res ? { ok: false, error: res.error } : { ok: true, data: res.data };
}

// ─── Email OTP ────────────────────────────────────────────────────────────────
export async function otpSendAction(input: {
  email: string;
  type?: string;
}): Promise<AuthResult<unknown>> {
  const res = await serverTry('/api/auth/otp/send/', { method: 'POST', body: input });
  return 'error' in res ? { ok: false, error: res.error } : { ok: true, data: res.data };
}

export async function otpVerifyAction(input: {
  email: string;
  otp: string;
  type?: string;
}): Promise<AuthResult<unknown>> {
  const res = await serverTry('/api/auth/otp/verify/', { method: 'POST', body: input });
  return 'error' in res ? { ok: false, error: res.error } : { ok: true, data: res.data };
}

// ─── TOTP 2FA ─────────────────────────────────────────────────────────────────
export async function twoFactorEnableAction(input: {
  password: string;
}): Promise<AuthResult<{ totpURI: string; backupCodes: string[] }>> {
  const res = await serverTry<{ totpURI: string; backupCodes: string[] }>('/api/auth/2fa/enable/', {
    method: 'POST',
    body: input,
  });
  return 'error' in res ? { ok: false, error: res.error } : { ok: true, data: res.data };
}

/** Confirm/activate enrollment while already authenticated. */
export async function twoFactorVerifyAction(input: { code: string }): Promise<AuthResult<unknown>> {
  const res = await serverTry('/api/auth/2fa/verify/', { method: 'POST', body: input });
  return 'error' in res ? { ok: false, error: res.error } : { ok: true, data: res.data };
}

/** Complete a 2FA login: exchange preAuthToken + code for JWTs. */
export async function twoFactorLoginVerifyAction(input: {
  preAuthToken: string;
  code: string;
}): Promise<AuthResult<{ user: AuthUser }>> {
  try {
    const res = await request<{ access: string; refresh: string; user: AuthUser }>(
      '/api/auth/2fa/login-verify/',
      { method: 'POST', body: input, baseUrl: API_INTERNAL_BASE },
    );
    await setTokenCookies(res.access, res.refresh);
    return { ok: true, data: { user: res.user } };
  } catch (e) {
    return { ok: false, error: errMessage(e) };
  }
}

export async function twoFactorDisableAction(input: {
  password: string;
}): Promise<AuthResult<unknown>> {
  const res = await serverTry('/api/auth/2fa/disable/', { method: 'POST', body: input });
  return 'error' in res ? { ok: false, error: res.error } : { ok: true, data: res.data };
}
