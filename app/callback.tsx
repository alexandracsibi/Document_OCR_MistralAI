import * as AuthSession from "expo-auth-session";
import { useEffect, useMemo } from "react";
import { ActivityIndicator, Text, View } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";

import { ENV } from "../src/config/env";
import { buildAuthRequestConfig, getIssuerUrl } from "../src/auth/auth0";
import { loadCodeVerifier, clearCodeVerifier } from "../src/auth/pkce";
import { saveSession } from "../src/auth/session";

export default function Callback() {
  const router = useRouter();
  const params = useLocalSearchParams<{ code?: string; state?: string; error?: string; error_description?: string }>();

  const issuerUrl = getIssuerUrl();
  const discovery = AuthSession.useAutoDiscovery(issuerUrl ?? "");

  const auth0Ready = !!ENV.auth0Domain && !!ENV.auth0ClientId;

  const cfg = useMemo(() => {
    if (!auth0Ready) return null;
    return buildAuthRequestConfig();
  }, [auth0Ready]);

  useEffect(() => {
    (async () => {
      if (!auth0Ready || !issuerUrl || !discovery || !cfg) {
        router.replace("/login");
        return;
      }

      if (params.error) {
        // auth0 returned an error
        router.replace("/login");
        return;
      }

      const code = params.code;
      if (!code) {
        router.replace("/login");
        return;
      }

      const codeVerifier = await loadCodeVerifier();
      if (!codeVerifier) {
        // can't exchange without verifier (expired or not saved)
        router.replace("/login");
        return;
      }

      const token = await AuthSession.exchangeCodeAsync(
        {
          clientId: cfg.clientId,
          code,
          redirectUri: cfg.redirectUri,
          extraParams: { code_verifier: codeVerifier },
        },
        discovery
      );

      await clearCodeVerifier();

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
    })();
  }, [auth0Ready, issuerUrl, discovery, cfg, params, router]);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 16 }}>
      <ActivityIndicator />
      <Text style={{ marginTop: 12, opacity: 0.7 }}>Finishing sign-in…</Text>
    </View>
  );
}