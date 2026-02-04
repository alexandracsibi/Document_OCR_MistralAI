import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack screenOptions={{ headerTitleAlign: "center" }}>
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="(auth)/login" options={{ title: "Sign in" }} />
      <Stack.Screen name="(lock)/unlock" options={{ title: "Unlock" }} />
      <Stack.Screen name="(app)/home" options={{ title: "Home" }} />
      <Stack.Screen name="(app)/capture" options={{ title: "Capture" }} />
      <Stack.Screen name="(app)/result" options={{ title: "Result" }} />
    </Stack>
  );
}
