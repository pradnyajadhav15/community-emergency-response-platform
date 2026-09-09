import { useCallback, useState } from "react";
import { useFocusEffect, useRouter } from "expo-router";
import {
  Alert,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import api, { apiError } from "../../src/api";
import { useAuth } from "../../src/auth";
import { getCurrentLocation } from "../../src/device";
import { colors, statusColors } from "../../src/theme";
import { Badge, Banner, Card } from "../../src/ui";

const CATEGORIES = [
  { key: "MEDICAL", label: "Medical", icon: "M" },
  { key: "FIRE", label: "Fire", icon: "F" },
  { key: "SECURITY", label: "Security", icon: "S" },
  { key: "ACCIDENT", label: "Accident", icon: "A" },
  { key: "FALL", label: "Fall", icon: "!" },
  { key: "OTHER", label: "Other", icon: "?" },
];

function ResidentSOS() {
  const router = useRouter();
  const [category, setCategory] = useState("MEDICAL");
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [active, setActive] = useState(null);

  const load = useCallback(() => {
    api
      .get("/sos/active/")
      .then(({ data }) => setActive(data[0] || null))
      .catch(() => {});
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  function confirmSend() {
    Alert.alert(
      "Send emergency alert?",
      "Your guardians, security staff, and nearby volunteers will be notified immediately.",
      [
        { text: "Cancel", style: "cancel" },
        { text: "Send SOS", style: "destructive", onPress: send },
      ]
    );
  }

  async function send() {
    setError("");
    setSending(true);
    try {
      const loc = await getCurrentLocation();
      const { data } = await api.post("/sos/", {
        category,
        message: message.trim(),
        latitude: loc.latitude,
        longitude: loc.longitude,
      });
      setMessage("");
      setActive(data);
      Alert.alert(
        "Alert sent",
        `${data.notifications_sent || 0} notification(s) dispatched. Help is being contacted.`
      );
    } catch (e) {
      setError(apiError(e, "Could not send the alert."));
    } finally {
      setSending(false);
    }
  }

  return (
    <ScrollView
      contentContainerStyle={styles.scroll}
      refreshControl={<RefreshControl refreshing={false} onRefresh={load} tintColor={colors.muted} />}
    >
      <Text style={styles.heading}>Emergency</Text>
      <Text style={styles.sub}>Choose a category, then tap SOS.</Text>

      <Banner message={error} />

      {active && (
        <Pressable onPress={() => router.push(`/incident/${active.id}`)}>
          <Card style={styles.activeCard}>
            <View style={styles.rowBetween}>
              <Text style={styles.activeTitle}>Active alert #{active.id}</Text>
              <Badge text={active.status_display} color={statusColors[active.status]} />
            </View>
            <Text style={styles.activeBody}>
              {active.category_display}
              {active.responder_name ? ` - ${active.responder_name} responding` : " - awaiting response"}
            </Text>
            <Text style={styles.tapHint}>Tap to open the incident</Text>
          </Card>
        </Pressable>
      )}

      <View style={styles.grid}>
        {CATEGORIES.map((c) => (
          <Pressable
            key={c.key}
            onPress={() => setCategory(c.key)}
            style={[styles.catChip, category === c.key && styles.catChipActive]}
          >
            <Text style={[styles.catLabel, category === c.key && styles.catLabelActive]}>
              {c.label}
            </Text>
          </Pressable>
        ))}
      </View>

      <TextInput
        value={message}
        onChangeText={setMessage}
        placeholder="What is happening? (optional)"
        placeholderTextColor={colors.muted}
        style={styles.messageInput}
        multiline
      />

      <Pressable
        onPress={confirmSend}
        disabled={sending}
        style={({ pressed }) => [styles.sosButton, pressed && styles.sosPressed]}
      >
        <Text style={styles.sosText}>{sending ? "..." : "SOS"}</Text>
        <Text style={styles.sosSub}>{sending ? "Contacting help" : "Tap to get help"}</Text>
      </Pressable>

      <Text style={styles.footNote}>
        Your location and flat number are attached automatically.
      </Text>
    </ScrollView>
  );
}

function ResponderList() {
  const router = useRouter();
  const [alerts, setAlerts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const { data } = await api.get("/sos/active/");
      setAlerts(data);
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load incidents."));
    } finally {
      setRefreshing(false);
    }
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  return (
    <ScrollView
      contentContainerStyle={styles.scroll}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={load} tintColor={colors.muted} />
      }
    >
      <Text style={styles.heading}>Active Incidents</Text>
      <Text style={styles.sub}>Pull down to refresh.</Text>

      <Banner message={error} />

      {alerts.length === 0 && !refreshing && (
        <Card>
          <Text style={styles.emptyTitle}>No active incidents</Text>
          <Text style={styles.emptyBody}>
            You will be notified when someone in your society needs assistance.
          </Text>
        </Card>
      )}

      {alerts.map((a) => (
        <Pressable key={a.id} onPress={() => router.push(`/incident/${a.id}`)}>
          <Card>
            <View style={styles.rowBetween}>
              <Text style={styles.alertTitle}>
                {a.category_display} - #{a.id}
              </Text>
              <Badge text={a.status_display} color={statusColors[a.status]} />
            </View>
            <Text style={styles.alertMeta}>{a.resident_name} - {a.flat_label || "location not set"}</Text>
            {!!a.message && <Text style={styles.alertMsg}>{a.message}</Text>}
            <Text style={styles.alertMeta}>
              Tier {a.escalation_level}
              {a.responder_name ? ` - ${a.responder_name} responding` : " - unclaimed"}
            </Text>
          </Card>
        </Pressable>
      ))}
    </ScrollView>
  );
}

export default function HomeTab() {
  const { user } = useAuth();
  return user?.role === "RESIDENT" ? <ResidentSOS /> : <ResponderList />;
}

const styles = StyleSheet.create({
  scroll: { padding: 20, paddingTop: 64, paddingBottom: 40, flexGrow: 1 },
  heading: { color: colors.text, fontSize: 28, fontWeight: "800" },
  sub: { color: colors.muted, fontSize: 14, marginTop: 4, marginBottom: 20 },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 10, marginBottom: 16 },
  catChip: {
    width: "31%", alignItems: "center", paddingVertical: 16, borderRadius: 12,
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
  },
  catChipActive: { borderColor: colors.danger, backgroundColor: "#450A0A" },
  catLabel: { color: colors.muted, fontSize: 13, fontWeight: "600" },
  catLabelActive: { color: colors.text },
  messageInput: {
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
    borderRadius: 12, padding: 14, color: colors.text, fontSize: 15,
    minHeight: 72, textAlignVertical: "top", marginBottom: 24,
  },
  sosButton: {
    backgroundColor: colors.danger, borderRadius: 999, aspectRatio: 1,
    width: "68%", alignSelf: "center", alignItems: "center", justifyContent: "center",
    shadowColor: colors.danger, shadowOpacity: 0.5, shadowRadius: 24,
    shadowOffset: { width: 0, height: 8 }, elevation: 12,
  },
  sosPressed: { backgroundColor: colors.dangerDark, transform: [{ scale: 0.97 }] },
  sosText: { color: "#fff", fontSize: 52, fontWeight: "900", letterSpacing: 3 },
  sosSub: { color: "#FECACA", fontSize: 13, marginTop: 6 },
  footNote: { color: colors.muted, fontSize: 12, textAlign: "center", marginTop: 22 },
  activeCard: { borderColor: colors.danger },
  activeTitle: { color: colors.text, fontSize: 16, fontWeight: "700" },
  activeBody: { color: colors.muted, fontSize: 14, marginTop: 6 },
  tapHint: { color: colors.primary, fontSize: 12, marginTop: 8 },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  alertTitle: { color: colors.text, fontSize: 16, fontWeight: "700", flex: 1 },
  alertMeta: { color: colors.muted, fontSize: 13, marginTop: 6 },
  alertMsg: { color: colors.text, fontSize: 14, marginTop: 8 },
  emptyTitle: { color: colors.text, fontSize: 16, fontWeight: "700" },
  emptyBody: { color: colors.muted, fontSize: 14, marginTop: 6, lineHeight: 20 },
});