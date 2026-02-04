import { useLocalSearchParams } from "expo-router";
import { ScrollView, Text, View } from "react-native";

export default function Result() {
  const params = useLocalSearchParams();
  const raw = typeof params.data === "string" ? params.data : "";

  return (
    <ScrollView style={{ flex: 1 }}>
      <View style={{ padding: 16, gap: 12 }}>
        <Text style={{ fontSize: 20, fontWeight: "600" }}>Server response</Text>
        <Text selectable style={{ fontFamily: "monospace" }}>
          {raw || "(no data)"}
        </Text>
      </View>
    </ScrollView>
  );
}
