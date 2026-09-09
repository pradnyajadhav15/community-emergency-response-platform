import { Redirect } from "expo-router";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

import { useAuth } from "../src/auth";
import { colors } from "../src/theme";

export default function Index() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <View style={styles.center}>
        <Text style={styles.brand}>CERP</Text>
        <Text style={styles.tag}>Community Emergency Response</Text>
        <ActivityIndicator color={colors.primary} style={{ marginTop: 24 }} />
      </View>
    );
  }

  return <Redirect href={user ? "/home" : "/login"} />;
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.bg },
  brand: { color: colors.text, fontSize: 44, fontWeight: "800", letterSpacing: 4 },
  tag: { color: colors.muted, fontSize: 14, marginTop: 8 },
});
