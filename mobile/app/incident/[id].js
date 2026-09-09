import { useCallback, useState } from "react";
import { useFocusEffect, useLocalSearchParams } from "expo-router";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import api, { apiError } from "../../src/api";
import { useAuth } from "../../src/auth";
import { colors, statusColors } from "../../src/theme";
import { Badge, Banner, Button, Card } from "../../src/ui";

export default function IncidentDetail() {
  const { id } = useLocalSearchParams();
  const { user } = useAuth();
  const [alert, setAlert] = useState(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [a, m] = await Promise.all([
        api.get(`/sos/${id}/`),
        api.get(`/incidents/messages/?alert=${id}`),
      ]);
      setAlert(a.data);
      setMessages(m.data.results || m.data);
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load this incident."));
    }
  }, [id]);

  useFocusEffect(useCallback(() => {
    load();
    const timer = setInterval(load, 8000);
    return () => clearInterval(timer);
  }, [load]));

  async function act(path, body) {
    setBusy(true);
    try {
      await api.post(`/sos/${id}/${path}/`, body || {});
      await load();
      setError("");
    } catch (e) {
      setError(apiError(e, "Action failed."));
    } finally {
      setBusy(false);
    }
  }

  async function send() {
    if (!draft.trim()) return;
    const text = draft.trim();
    setDraft("");
    try {
      await api.post("/incidents/messages/", { alert: Number(id), body: text });
      await load();
    } catch (e) {
      setError(apiError(e, "Message not sent."));
    }
  }

  if (!alert) {
    return (
      <View style={styles.center}>
        <Banner message={error} />
        {!error && <ActivityIndicator color={colors.primary} />}
      </View>
    );
  }

  const isResident = user?.id === alert.resident;
  const canRespond = !isResident && !alert.responder;
  const isResponder = user?.id === alert.responder;
  const isOpen = !["RESOLVED", "CLOSED", "CANCELLED"].includes(alert.status);

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      keyboardVerticalOffset={90}
    >
      <ScrollView contentContainerStyle={styles.scroll}>
        <Banner message={error} />

        <Card>
          <View style={styles.rowBetween}>
            <Text style={styles.title}>{alert.category_display}</Text>
            <Badge text={alert.status_display} color={statusColors[alert.status]} />
          </View>
          {!!alert.message && <Text style={styles.message}>{alert.message}</Text>}
          <Text style={styles.meta}>Resident: {alert.resident_name}</Text>
          {!!alert.resident_phone && <Text style={styles.meta}>Phone: {alert.resident_phone}</Text>}
          <Text style={styles.meta}>Location: {alert.flat_label || "not set"}</Text>
          {alert.latitude != null && (
            <Text style={styles.meta}>
              GPS: {alert.latitude.toFixed(5)}, {alert.longitude.toFixed(5)}
            </Text>
          )}
          <Text style={styles.meta}>Escalation tier: {alert.escalation_level}</Text>
          <Text style={styles.meta}>Raised: {new Date(alert.created_at).toLocaleString()}</Text>
          {!!alert.responder_name && (
            <Text style={styles.responder}>Responding: {alert.responder_name}</Text>
          )}
          {!!alert.resolution_notes && (
            <Text style={styles.resolution}>Resolution: {alert.resolution_notes}</Text>
          )}
        </Card>

        {isOpen && (
          <View style={styles.actions}>
            {canRespond && (
              <Button title="Accept & Respond" onPress={() => act("accept")} loading={busy} />
            )}
            {(isResponder || isResident) && (
              <Button
                title="Mark Resolved"
                variant="danger"
                onPress={() => act("resolve", { resolution_notes: "Assistance provided." })}
                loading={busy}
              />
            )}
          </View>
        )}

        <Text style={styles.threadTitle}>Incident Thread</Text>
        {messages.length === 0 && <Text style={styles.noMessages}>No messages yet.</Text>}
        {messages.map((m) => (
          <View
            key={m.id}
            style={[
              styles.bubble,
              m.is_system && styles.systemBubble,
              m.sender === user?.id && styles.ownBubble,
            ]}
          >
            {!m.is_system && <Text style={styles.sender}>{m.sender_name}</Text>}
            <Text style={m.is_system ? styles.systemText : styles.bubbleText}>{m.body}</Text>
            <Text style={styles.time}>{new Date(m.created_at).toLocaleTimeString()}</Text>
          </View>
        ))}
      </ScrollView>

      <View style={styles.composer}>
        <TextInput
          value={draft}
          onChangeText={setDraft}
          placeholder="Type a message"
          placeholderTextColor={colors.muted}
          style={styles.composerInput}
        />
        <Pressable onPress={send} style={styles.sendBtn}>
          <Text style={styles.sendText}>Send</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  center: { flex: 1, justifyContent: "center", padding: 20, backgroundColor: colors.bg },
  scroll: { padding: 20, paddingBottom: 20 },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  title: { color: colors.text, fontSize: 20, fontWeight: "800", flex: 1 },
  message: { color: colors.text, fontSize: 15, marginTop: 10, marginBottom: 6 },
  meta: { color: colors.muted, fontSize: 13, marginTop: 4 },
  responder: { color: colors.success, fontSize: 14, marginTop: 10, fontWeight: "600" },
  resolution: { color: colors.success, fontSize: 14, marginTop: 8 },
  actions: { gap: 4, marginBottom: 20 },
  threadTitle: { color: colors.text, fontSize: 17, fontWeight: "700", marginTop: 8, marginBottom: 12 },
  noMessages: { color: colors.muted, fontSize: 14, fontStyle: "italic" },
  bubble: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 12,
    marginBottom: 10, maxWidth: "88%", alignSelf: "flex-start",
  },
  ownBubble: { alignSelf: "flex-end", backgroundColor: colors.primary },
  systemBubble: { alignSelf: "center", backgroundColor: colors.surfaceAlt, maxWidth: "100%" },
  sender: { color: colors.muted, fontSize: 11, fontWeight: "700", marginBottom: 4 },
  bubbleText: { color: colors.text, fontSize: 15 },
  systemText: { color: colors.muted, fontSize: 13, fontStyle: "italic", textAlign: "center" },
  time: { color: colors.muted, fontSize: 10, marginTop: 6, opacity: 0.7 },
  composer: {
    flexDirection: "row", padding: 12, gap: 10,
    borderTopWidth: 1, borderTopColor: colors.border, backgroundColor: colors.surface,
  },
  composerInput: {
    flex: 1, backgroundColor: colors.bg, borderRadius: 20,
    paddingHorizontal: 16, paddingVertical: 10, color: colors.text, fontSize: 15,
  },
  sendBtn: {
    backgroundColor: colors.primary, borderRadius: 20,
    paddingHorizontal: 18, justifyContent: "center",
  },
  sendText: { color: "#fff", fontWeight: "700" },
});