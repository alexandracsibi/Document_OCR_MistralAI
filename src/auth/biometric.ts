import * as LocalAuthentication from "expo-local-authentication";

export async function canUseBiometrics(): Promise<boolean> {
  const hasHardware = await LocalAuthentication.hasHardwareAsync();
  const enrolled = await LocalAuthentication.isEnrolledAsync();
  return hasHardware && enrolled;
}

export async function biometricUnlock(): Promise<boolean> {
  const res = await LocalAuthentication.authenticateAsync({
    promptMessage: "Unlock",
    cancelLabel: "Cancel",
    disableDeviceFallback: false,
  });
  return !!res.success;
}
