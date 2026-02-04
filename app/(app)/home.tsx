import { Button, View } from "react-native";
import { useRouter } from "expo-router";
import { clearSession } from "../../src/auth/session";

export default function Home() {
  const router = useRouter();

  return (
    <View style={{ flex: 1, padding: 16, justifyContent: "center", gap: 12 }}>
      <Button title="Capture photo" onPress={() => router.push("/capture")} />
      <Button
        title="Logout"
        onPress={async () => {
          await clearSession();
          router.replace("/login");
        }}
      />
    </View>
  );
}
