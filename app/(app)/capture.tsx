import { useState } from "react";
import { ActivityIndicator, Alert, Button, Image, View, Text } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";
import { Picker } from "@react-native-picker/picker";
import * as ImageManipulator from "expo-image-manipulator";

import { uploadToOcrService } from "../../src/api/endpoints";

const DOC_TYPES = [
  "ID_FRONT",
  "ID_BACK",
  "ID_OLD_FRONT",
  "ID_OLD_BACK",
  "DRIVING_LICENSE",
  "ADDRESS_CARD",
  "PASSPORT",
  "REGISTRATION",
  "COC",
] as const;

export default function Capture() {
  const router = useRouter();
  const [uri, setUri] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [docType, setDocType] = useState<(typeof DOC_TYPES)[number]>("ID_BACK");

  async function takePhoto() {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      Alert.alert("Permission required", "Camera permission is needed.");
      return;
    }

    const res = await ImagePicker.launchCameraAsync({
      quality: 0.9,
      allowsEditing: false,
    });

    if (!res.canceled && res.assets?.[0]?.uri) {
      setUri(res.assets[0].uri);
    }
  }

  async function onUpload() {
    if (!uri) return;
    setBusy(true);

    try {
      // TODO: replace with real user/tenant id later
      const uid = "dev-user-1";

      const optimized = await ImageManipulator.manipulateAsync(
        uri,
        [{ resize: { width: 2000 } }], // keeps aspect ratio
        { compress: 0.8, format: ImageManipulator.SaveFormat.JPEG }
      );
      const json = await uploadToOcrService({
        uri: optimized.uri,
        uid,
        docType,
        path: "/v1/process",
        filename: "scan.jpg",
        mimeType: "image/jpeg",
      });

      const pretty = JSON.stringify(json, null, 2);
      router.push({ pathname: "/result", params: { data: pretty } });

      // Optional: clear photo after successful upload
      // setUri(null);
    } catch (e: any) {
      Alert.alert("Upload failed", e?.message ?? "Unknown error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={{ flex: 1, padding: 16, justifyContent: "center", gap: 12 }}>
      <Text style={{ fontSize: 16, fontWeight: "600" }}>Document type</Text>
      <View style={{ borderWidth: 1, borderRadius: 10, overflow: "hidden" }}>
        <Picker selectedValue={docType} onValueChange={(v) => setDocType(v)}>
          {DOC_TYPES.map((t) => (
            <Picker.Item key={t} label={t} value={t} />
          ))}
        </Picker>
      </View>

      <Button title="Take photo" onPress={takePhoto} />

      {uri && (
        <>
          <Image source={{ uri }} style={{ width: "100%", height: 320, borderRadius: 12 }} />
          <Button title="Upload" onPress={onUpload} disabled={busy} />
        </>
      )}

      {busy && <ActivityIndicator />}
    </View>
  );
}