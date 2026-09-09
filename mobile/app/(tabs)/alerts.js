import { useCallback, useState } from "react";
import { useFocusEffect, useRouter } from "expo-router";
import { Pressable, RefreshControl, ScrollView, StyleSheet, Text, View } from "react-native";

import api, { apiError } from "../../src/api";
import { colors, statusColors } from "../../src/theme";
import { Badge, Banner, Card } from "../../src/ui";

export default function Alerts() {
  const router = useRouter();
  const [alerts, setAlerts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const { data } = await api.get("/sos/");
      setAlerts(data.results || data);
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load your alerts."));
    } finally {
      setRefreshing(false);
    }
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  return (
    <ScrollView
      contentContainerStyle={styles.scroll}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} tintColor={colors.muted} />}
    >
      <Banner message={error} />
      {alerts.length === 0 && !refreshing && (
        <Card>
          <Text style={styles.emptyTitle}>No alerts yet</Text>
          <Text style={styles.emptyBody}>Alerts you raise will appear here.</Text>
        </Card>
      )}
      {alerts.map((a) => (
        <Pressable key={a.id} onPress={() => router.push(`/incident/${a.id}`)}>
          <Card>
            <View style={styles.rowBetween}>
              <Text style={styles.title}>{a.category_display} · #{a.id}</Text>
              <Badge text={a.status_display} color={statusColors[a.status]} />
            </View>
            {!!a.message && <Text style={styles.body}>{a.message}</Text>}
            <Text style={styles.meta}>
              {new Date(a.created_at).toLocaleString()} · tier {a.escalation_level}
            </Text>
            {!!a.responder_name && (
              <Text style={styles.meta}>Responder: {a.responder_name}</Text>
            )}
          </Card>
        </Pressable>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { padding: 20, paddingBottom: 40, flexGrow: 1 },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  title: { color: colors.text, fontSize: 16, fontWeight: "700", flex: 1 },
  body: { color: colors.text, fontSize: 14, marginTop: 8 },
  meta: { color: colors.muted, fontSize: 12, marginTop: 6 },
  emptyTitle: { color: colors.text, fontSize: 16, fontWeight: "700" },
  emptyBody: { color: colors.muted, fontSize: 14, marginTop: 6 },
});
