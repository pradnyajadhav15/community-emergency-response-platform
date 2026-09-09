import { useState } from "react";
import { ScrollView, StyleSheet, Switch, Text, View } from "react-native";

import api, { apiError } from "../../src/api";
import { useAuth } from "../../src/auth";
import { colors, roleLabels } from "../../src/theme";
import { Banner, Button, Card } from "../../src/ui";

export default function Profile() {
  const { user, signOut, refreshUser } = useAuth();
  const [available, setAvailable] = useState(user?.is_available ?? true);
  const [error, setError] = useState("");

  const isResponder = ["VOLUNTEER", "SECURITY"].includes(user?.role);

  async function toggle(value) {
    setAvailable(value);
    try {
      await api.post("/auth/availability/", { is_available: value });
      await refreshUser();
      setError("");
    } catch (e) {
      setAvailable(!value);
      setError(apiError(e, "Could not update availability."));
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      <Banner message={error} />

      <Card>
        <Text style={styles.name}>{user?.first_name || user?.username}</Text>
        <Text style={styles.role}>{roleLabels[user?.role] || user?.role}</Text>
      </Card>

      <Card>
        <Text style={styles.cardTitle}>Account</Text>
        <Text style={styles.detail}>Username: {user?.username}</Text>
        <Text style={styles.detail}>Email: {user?.email || "not set"}</Text>
        <Text style={styles.detail}>Phone: {user?.phone || "not set"}</Text>
      </Card>

      {isResponder && (
        <Card>
          <View style={styles.rowBetween}>
            <View style={{ flex: 1 }}>
              <Text style={styles.cardTitle}>Available to respond</Text>
              <Text style={styles.detail}>
                {available
                  ? "You will receive incident alerts."
                  : "You will not be routed new incidents."}
              </Text>
            </View>
            <Switch
              value={available}
              onValueChange={toggle}
              trackColor={{ true: colors.success, false: colors.border }}
            />
          </View>
        </Card>
      )}

      <Button title="Sign Out" variant="ghost" onPress={signOut} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { padding: 20, paddingBottom: 40, flexGrow: 1 },
  name: { color: colors.text, fontSize: 22, fontWeight: "800" },
  role: { color: colors.muted, fontSize: 14, marginTop: 4 },
  cardTitle: { color: colors.text, fontSize: 16, fontWeight: "700", marginBottom: 8 },
  detail: { color: colors.muted, fontSize: 14, marginBottom: 4 },
  rowBetween: { flexDirection: "row", alignItems: "center", gap: 12 },
});
