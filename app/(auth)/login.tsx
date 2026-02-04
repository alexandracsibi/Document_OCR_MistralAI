import * as AuthSession from "expo-auth-session";
import { useEffect } from "react";
import { Button, Text, View } from "react-native";
import { useRouter } from "expo-router";

import { ENV } from "../../src/config/env";
import { buildAuthRequestConfig, getIssuerUrl, isExpoGo } from "../../src/auth/auth0";
import { saveSession } from "../../src/auth/session";

export default function Login() {
  const router = useRouter();

  const auth0Ready = !!ENV.auth0Domain && !!ENV.auth0ClientId;

  const issuerUrl = getIssuerUrl();
  const discovery = AuthSession.useAutoDiscovery(issuerUrl ?? "");

  // Always call hooks; cfg is only valid when auth0Ready
  const cfg = auth0Ready ? buildAuthRequestConfig() : ({} as any);

  const [request, response, promptAsync] = AuthSession.useAuthRequest(cfg, discovery);

  async function devSignIn() {
    await saveSession({
      accessToken: "dev-token",
      expiresAt: Date.now() + 7 * 24 * 60 * 60 * 1000,
    });
    router.replace("/unlock");
  }

  useEffect(() => {
    (async () => {
      if (!auth0Ready) return;
      if (!response || response.type !== "success") return;
      if (!discovery) return;

      const cfgReal = buildAuthRequestConfig();

      const code = response.params.code;
      if (!code) return;

      // PKCE verifier must exist for code exchange
      const verifier = request?.codeVerifier;
      if (!verifier) {
        console.warn("Missing codeVerifier (PKCE). This often happens on unstable redirects in Expo Go.");
        return;
      }

      const token = await AuthSession.exchangeCodeAsync(
        {
          clientId: cfgReal.clientId,
          code,
          redirectUri: cfgReal.redirectUri,
          extraParams: { code_verifier: verifier },
        },
        discovery
      );

      await saveSession({
        accessToken: token.accessToken,
        idToken: token.idToken,
        refreshToken: (token as any).refreshToken,
        tokenType: token.tokenType,
        scope: token.scope,
        expiresAt: token.expiresIn ? Date.now() + token.expiresIn * 1000 : undefined,
        audience: ENV.auth0Audience || undefined,
      });

      router.replace("/unlock");
    })().catch((e) => {
      console.error("Auth0 login failed:", e);
    });
  }, [auth0Ready, response, discovery, request, router]);

  return (
    <View style={{ flex: 1, padding: 16, justifyContent: "center", gap: 12 }}>
      <Text style={{ fontSize: 20, fontWeight: "600" }}>Sign in</Text>

      <Button title="Dev sign-in (skip Auth0 for now)" onPress={devSignIn} />

      {auth0Ready ? (
        <Button
          title="Continue with Auth0"
          disabled={!request}
          onPress={() => (promptAsync as any)({ useProxy: isExpoGo() })}
        />
      ) : (
        <Text style={{ opacity: 0.7 }}>
          Auth0 not configured yet. Set AUTH0_DOMAIN and AUTH0_CLIENT_ID in app.json.
        </Text>
      )}

      <Text style={{ opacity: 0.7 }}>
        Audience: {ENV.auth0Audience ? "API mode" : "Identity-only mode"}
      </Text>

      {auth0Ready && (
        <Text selectable style={{ opacity: 0.7 }}>
          Redirect: {cfg.redirectUri}
        </Text>
      )}
    </View>
  );
}
