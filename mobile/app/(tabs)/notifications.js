import { useCallback, useState } from "react";
import { useFocusEffect, useRouter } from "expo-router";
import { Pressable, RefreshControl, ScrollView, StyleSheet, Text } from "react-native";

import api, { apiError } from "../../src/api";
import { colors } from "../../src/theme";
import { Banner, Card } from "../../src/ui";

export default function Notifications() {
  const router = useRouter();
  const [items, setItems] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const { data } = await api.get("/notifications/");
      setItems(data.results || data);
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load notifications."));
    } finally {
      setRefreshing(false);
    }
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  async function open(item) {
    try {
      await api.post(`/notifications/${item.id}/mark-read/`);
    } catch {}
    router.push(`/incident/${item.alert}`);
  }

  return (
    <ScrollView
      contentContainerStyle={styles.scroll}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} tintColor={colors.muted} />}
    >
      <Banner message={error} />
      {items.length === 0 && !refreshing && (
        <Card>
          <Text style={styles.emptyTitle}>Inbox empty</Text>
          <Text style={styles.emptyBody}>Emergency alerts sent to you will appear here.</Text>
        </Card>
      )}
      {items.map((n) => (
        <Pressable key={n.id} onPress={() => open(n)}>
          <Card style={n.status !== "READ" && styles.unread}>
            <Text style={styles.title}>{n.title}</Text>
            <Text style={styles.body}>{n.body}</Text>
            <Text style={styles.meta}>
              {n.audience_display} · {new Date(n.created_at).toLocaleString()}
            </Text>
          </Card>
        </Pressable>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { padding: 20, paddingBottom: 40, flexGrow: 1 },
  unread: { borderColor: colors.primary },
  title: { color: colors.text, fontSize: 16, fontWeight: "700" },
  body: { color: colors.muted, fontSize: 14, marginTop: 6, lineHeight: 20 },
  meta: { color: colors.muted, fontSize: 12, marginTop: 8 },
  emptyTitle: { color: colors.text, fontSize: 16, fontWeight: "700" },
  emptyBody: { color: colors.muted, fontSize: 14, marginTop: 6 },
});
