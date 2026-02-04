import { del, getJson, setJson } from "../storage/secureStore";

const KEY = "pkce_v1";

type PkceState = {
  codeVerifier: string;
  createdAt: number;
};

export async function saveCodeVerifier(codeVerifier: string) {
  const payload: PkceState = { codeVerifier, createdAt: Date.now() };
  await setJson(KEY, payload);
}

export async function loadCodeVerifier(): Promise<string | null> {
  const payload = await getJson<PkceState>(KEY);
  if (!payload?.codeVerifier) return null;

  // optional: expire after 10 minutes
  if (Date.now() - payload.createdAt > 10 * 60 * 1000) {
    await del(KEY);
    return null;
  }
  return payload.codeVerifier;
}

export async function clearCodeVerifier() {
  await del(KEY);
}
