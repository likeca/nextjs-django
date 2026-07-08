"use client";

/**
 * Django-backed auth client. Drop-in replacement for the former better-auth
 * client: exposes the same surface (signIn / signUp / signOut / useSession /
 * changePassword / emailOtp) so existing components keep working, but talks to
 * the Django dj-rest-auth + SimpleJWT endpoints.
 *
 * Token storage + transparent refresh live in lib/api/browser.ts.
 */
import { useCallback, useSyncExternalStore } from "react";

import { ApiError, API_BASE, request } from "./api/client";
import { clearTokens, getAccessToken, storeTokens } from "./api/browser";

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  emailVerified: boolean;
  image: string | null;
  phone: string | null;
  isAdmin: boolean;
  roleId: string | null;
  role: { id: string; name: string } | null;
}

export interface Session {
  user: AuthUser;
}

type Result<T> = { data: T; error: null } | { data: null; error: { message: string } };

function ok<T>(data: T): Result<T> {
  return { data, error: null };
}
function fail<T = null>(e: unknown): Result<T> {
  const message =
    e instanceof ApiError ? e.message : e instanceof Error ? e.message : "Request failed";
  return { data: null, error: { message } };
}

// ─── Session store (replaces better-auth's reactive useSession) ───────────────
let sessionState: { data: Session | null; isPending: boolean } = {
  data: null,
  isPending: true,
};
const listeners = new Set<() => void>();
let fetched = false;

function emit() {
  for (const l of listeners) l();
}
function setSession(data: Session | null, isPending = false) {
  sessionState = { data, isPending };
  emit();
}

export async function fetchSession(): Promise<Session | null> {
  if (!getAccessToken()) {
    setSession(null, false);
    return null;
  }
  try {
    const user = await request<AuthUser>("/api/auth/user/", {
      token: getAccessToken(),
      baseUrl: API_BASE,
    });
    const session = { user };
    setSession(session, false);
    return session;
  } catch {
    setSession(null, false);
    return null;
  }
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  if (!fetched) {
    fetched = true;
    void fetchSession();
  }
  return () => listeners.delete(cb);
}
function getSnapshot() {
  return sessionState;
}
const SERVER_SNAPSHOT = { data: null, isPending: true };

/** better-auth-compatible hook: `const { data: session, isPending } = useSession()`. */
export function useSession() {
  const state = useSyncExternalStore(subscribe, getSnapshot, () => SERVER_SNAPSHOT);
  const refetch = useCallback(() => fetchSession(), []);
  return { ...state, error: null, refetch };
}

// Holds the short-lived pre-auth token between password-check and 2FA-verify at login.
let pendingPreAuthToken: string | null = null;

// ─── signIn / signUp / signOut ────────────────────────────────────────────────
export const signIn = {
  async email({ email, password }: { email: string; password: string; callbackURL?: string }) {
    try {
      const res = await request<{
        access?: string;
        refresh?: string;
        user?: AuthUser;
        twoFactorRequired?: boolean;
        preAuthToken?: string;
      }>("/api/auth/login/", { method: "POST", body: { email, password }, baseUrl: API_BASE });

      // 2FA-enabled account: no tokens yet — surface the redirect the login form expects.
      if (res.twoFactorRequired && res.preAuthToken) {
        pendingPreAuthToken = res.preAuthToken;
        return ok({ twoFactorRedirect: true });
      }

      storeTokens(res.access!, res.refresh);
      if (res.user) setSession({ user: res.user }, false);
      return ok({ user: res.user });
    } catch (e) {
      return fail(e);
    }
  },
};

export const signUp = {
  async email({
    email,
    password,
    name,
  }: {
    email: string;
    password: string;
    name: string;
    callbackURL?: string;
  }) {
    try {
      const res = await request<{ access?: string; refresh?: string; user?: AuthUser }>(
        "/api/auth/registration/",
        {
          method: "POST",
          body: { email, name, password1: password, password2: password },
          baseUrl: API_BASE,
        },
      );
      if (res.access) {
        storeTokens(res.access, res.refresh);
        if (res.user) setSession({ user: res.user }, false);
      }
      return ok({ user: res.user ?? null });
    } catch (e) {
      return fail(e);
    }
  },
};

export async function signOut() {
  try {
    await request("/api/auth/logout/", {
      method: "POST",
      token: getAccessToken(),
      baseUrl: API_BASE,
    });
  } catch {
    // ignore — we clear locally regardless
  }
  clearTokens();
  setSession(null, false);
}

// ─── changePassword (dj-rest-auth) ────────────────────────────────────────────
export async function changePassword({
  currentPassword,
  newPassword,
}: {
  currentPassword: string;
  newPassword: string;
  revokeOtherSessions?: boolean;
}) {
  try {
    const data = await request("/api/auth/password/change/", {
      method: "POST",
      token: getAccessToken(),
      baseUrl: API_BASE,
      body: {
        old_password: currentPassword,
        new_password1: newPassword,
        new_password2: newPassword,
      },
    });
    return ok(data);
  } catch (e) {
    return fail(e);
  }
}

// ─── Password reset (dj-rest-auth) ────────────────────────────────────────────
export async function requestPasswordReset({ email }: { email: string }) {
  try {
    const data = await request("/api/auth/password/reset/", {
      method: "POST",
      baseUrl: API_BASE,
      body: { email },
    });
    return ok(data);
  } catch (e) {
    return fail(e);
  }
}

export async function resetPassword({
  uid,
  token,
  newPassword,
}: {
  uid: string;
  token: string;
  newPassword: string;
}) {
  try {
    const data = await request("/api/auth/password/reset/confirm/", {
      method: "POST",
      baseUrl: API_BASE,
      body: { uid, token, new_password1: newPassword, new_password2: newPassword },
    });
    return ok(data);
  } catch (e) {
    return fail(e);
  }
}

// ─── Email OTP (Django: /api/auth/otp/*) ──────────────────────────────────────
export const emailOtp = {
  async sendVerificationOtp({ email, type }: { email: string; type?: string }) {
    try {
      const data = await request("/api/auth/otp/send/", {
        method: "POST",
        baseUrl: API_BASE,
        body: { email, type },
      });
      return ok(data);
    } catch (e) {
      return fail(e);
    }
  },
  async verifyEmail({ email, otp, type }: { email: string; otp: string; type?: string }) {
    try {
      const data = await request("/api/auth/otp/verify/", {
        method: "POST",
        baseUrl: API_BASE,
        body: { email, otp, type },
      });
      return ok(data);
    } catch (e) {
      return fail(e);
    }
  },
};

// ─── TOTP 2FA (Django: /api/auth/2fa/*) ───────────────────────────────────────
const twoFactor = {
  /** Begin enrollment: returns { totpURI, backupCodes }. */
  async enable({ password }: { password: string }) {
    try {
      const data = await request<{ totpURI: string; backupCodes: string[] }>(
        "/api/auth/2fa/enable/",
        { method: "POST", token: getAccessToken(), baseUrl: API_BASE, body: { password } },
      );
      return ok(data);
    } catch (e) {
      return fail(e);
    }
  },
  /**
   * Verify a TOTP code. Two contexts:
   *  - During login (a preAuthToken is pending): exchange code+token for JWTs.
   *  - In profile settings (already authenticated): confirm/activate enrollment.
   */
  async verifyTotp({ code }: { code: string }) {
    try {
      if (pendingPreAuthToken) {
        const res = await request<{ access: string; refresh: string; user: AuthUser }>(
          "/api/auth/2fa/login-verify/",
          { method: "POST", baseUrl: API_BASE, body: { preAuthToken: pendingPreAuthToken, code } },
        );
        pendingPreAuthToken = null;
        storeTokens(res.access, res.refresh);
        if (res.user) setSession({ user: res.user }, false);
        return ok({ user: res.user });
      }

      const data = await request("/api/auth/2fa/verify/", {
        method: "POST",
        token: getAccessToken(),
        baseUrl: API_BASE,
        body: { code },
      });
      return ok(data);
    } catch (e) {
      return fail(e);
    }
  },
  async disable({ password }: { password: string }) {
    try {
      const data = await request("/api/auth/2fa/disable/", {
        method: "POST",
        token: getAccessToken(),
        baseUrl: API_BASE,
        body: { password },
      });
      return ok(data);
    } catch (e) {
      return fail(e);
    }
  },
};

// Aggregate object mirroring `authClient.*` usage in components.
export const authClient = {
  signIn,
  signUp,
  signOut,
  useSession,
  changePassword,
  requestPasswordReset,
  resetPassword,
  emailOtp,
  twoFactor,
};
