import { useEffect, useState } from "react";
import { Button, Text, View } from "react-native";
import { useRouter } from "expo-router";
import { canUseBiometrics, biometricUnlock } from "../../src/auth/biometric";
import { clearSession } from "../../src/auth/session";

export default function Unlock() {
  const router = useRouter();
  const [supported, setSupported] = useState<boolean | null>(null);

  useEffect(() => {
    (async () => {
        const ok = await canUseBiometrics();
        setSupported(ok);
        if (!ok) router.replace("/home"); // auto-skip if no biometrics
    })();
  }, [router]);

  async function onUnlock() {
    if (supported === false) {
      router.replace("/home");
      return;
    }
    const ok = await biometricUnlock();
    if (ok) router.replace("/home");
  }

  async function onReLogin() {
    await clearSession();
    router.replace("/login");
  }

  return (
    <View style={{ flex: 1, padding: 16, justifyContent: "center", gap: 12 }}>
      <Text style={{ fontSize: 20, fontWeight: "600" }}>Unlock</Text>
      <Button title="Unlock with biometrics" onPress={onUnlock} />
      <Button title="Sign in again" onPress={onReLogin} />
      <Text style={{ opacity: 0.7 }}>
        Biometrics: {supported === null ? "checking…" : supported ? "available" : "not available (fallback)"}
      </Text>
    </View>
  );
}
