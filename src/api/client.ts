import { ENV } from "../config/env";
import { getAccessToken } from "../auth/session";

export async function apiFetch(path: string, init: RequestInit = {}) {
  if (!ENV.apiBaseUrl) throw new Error("Missing API_BASE_URL in app.json extra.");
  const url = `${ENV.apiBaseUrl.replace(/\/$/, "")}${path.startsWith("/") ? "" : "/"}${path}`;

  const token = await getAccessToken();

  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  return fetch(url, { ...init, headers });
}
