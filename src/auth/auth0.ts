import * as AuthSession from "expo-auth-session";
import * as WebBrowser from "expo-web-browser";
import Constants from "expo-constants";
import { ENV } from "../config/env";

WebBrowser.maybeCompleteAuthSession();

export function isExpoGo(): boolean {
  const c: any = Constants as any;

  // Newer field (preferred)
  if (c.executionEnvironment) {
    // Expo Go is typically "storeClient"
    return c.executionEnvironment === "storeClient";
  }
   // Older field (deprecated but still present sometimes)
  if (c.appOwnership) {
    return c.appOwnership === "expo";
  }

  return false;
}

export function getRedirectUri(): string {
  // For Expo Go we use proxy via promptAsync({ useProxy: true }).
  // Here we keep a normal redirect URI (no useProxy flag), so TypeScript is happy.
  return AuthSession.makeRedirectUri({
    scheme: "ocrservice",
    path: "callback",
  });
}

export function getIssuerUrl(): string | null {
  const d = (ENV.auth0Domain || "").trim();
  if (!d) return null;
  return `https://${d}`;
}

export function buildAuthRequestConfig(): AuthSession.AuthRequestConfig {
  const clientId = (ENV.auth0ClientId || "").trim();
  if (!clientId) throw new Error("Missing AUTH0_CLIENT_ID in app.json extra.");

  const extraParams: Record<string, string> = {};
  if ((ENV.auth0Audience || "").trim()) extraParams.audience = ENV.auth0Audience.trim();

  return {
    clientId,
    redirectUri: getRedirectUri(),
    scopes: ["openid", "profile", "email", "offline_access"],
    responseType: AuthSession.ResponseType.Code,
    usePKCE: true,
    extraParams,
  };
}
