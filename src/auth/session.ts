import { del, getJson, setJson } from "../storage/secureStore";
import { ENV } from "../config/env";

const KEY = "session_v1";

export type Session = {
  accessToken?: string;
  idToken?: string;
  refreshToken?: string;
  tokenType?: string;
  scope?: string;
  expiresAt?: number; // epoch ms
  audience?: string;  // store what used (optional)
};

export async function loadSession(): Promise<Session | null> {
  return getJson<Session>(KEY);
}

export async function saveSession(s: Session): Promise<void> {
  await setJson(KEY, s);
}

export async function clearSession(): Promise<void> {
  await del(KEY);
}

export async function hasSession(): Promise<boolean> {
  const s = await loadSession();
  return !!(s?.refreshToken || s?.accessToken || s?.idToken);
}

export function isExpired(s: Session | null): boolean {
  if (!s?.expiresAt) return false; // treat unknown as "not expired" for MVP
  return Date.now() >= s.expiresAt;
}

/**
 * Returns an access token if present. For API calls, prefer an audience token if configured.
 * Later you can enforce "must have audience token" for API calls.
 */
export async function getAccessToken(): Promise<string | undefined> {
  const s = await loadSession();
  if (!s?.accessToken) return undefined;

  // If you configured an audience, you *likely* want that token for API calls.
  // We store the audience used at login time; if mismatch, treat as missing.
  if (ENV.auth0Audience && s.audience && s.audience !== ENV.auth0Audience) return undefined;

  if (isExpired(s)) return s.accessToken; // MVP: no refresh yet; we’ll add refresh next
  return s.accessToken;
}
