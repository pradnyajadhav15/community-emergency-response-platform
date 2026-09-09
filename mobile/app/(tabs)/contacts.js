import { useCallback, useState } from "react";
import { useFocusEffect } from "expo-router";
import {
  Alert,
  Modal,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import api, { apiError } from "../../src/api";
import { colors } from "../../src/theme";
import { Badge, Banner, Button, Card, Field } from "../../src/ui";

const TIERS = [
  { level: 1, label: "Primary Guardian" },
  { level: 2, label: "Secondary Guardian" },
  { level: 3, label: "Emergency Contact" },
];

export default function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [modal, setModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    full_name: "", phone: "", email: "", relationship: "", escalation_level: 1,
  });

  const load = useCallback(async () => {
    setRefreshing(true);
    try {
      const { data } = await api.get("/auth/emergency-contacts/");
      setContacts(data.results || data);
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load contacts."));
    } finally {
      setRefreshing(false);
    }
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const set = (key) => (value) => setForm((f) => ({ ...f, [key]: value }));

  async function save() {
    if (!form.full_name || !form.phone) {
      setError("Name and phone are required.");
      return;
    }
    setSaving(true);
    try {
      const sameTier = contacts.filter((c) => c.escalation_level === form.escalation_level);
      await api.post("/auth/emergency-contacts/", {
        ...form,
        order: sameTier.length + 1,
      });
      setModal(false);
      setForm({ full_name: "", phone: "", email: "", relationship: "", escalation_level: 1 });
      setError("");
      load();
    } catch (e) {
      setError(apiError(e, "Could not save the contact."));
    } finally {
      setSaving(false);
    }
  }

  function remove(contact) {
    Alert.alert("Remove contact?", `${contact.full_name} will no longer be notified.`, [
      { text: "Cancel", style: "cancel" },
      {
        text: "Remove",
        style: "destructive",
        onPress: async () => {
          try {
            await api.delete(`/auth/emergency-contacts/${contact.id}/`);
            load();
          } catch (e) {
            setError(apiError(e, "Could not remove the contact."));
          }
        },
      },
    ]);
  }

  return (
    <>
      <ScrollView
        contentContainerStyle={styles.scroll}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={load} tintColor={colors.muted} />}
      >
        <Banner message={error} />

        {TIERS.map((tier) => {
          const list = contacts.filter((c) => c.escalation_level === tier.level);
          return (
            <View key={tier.level} style={styles.section}>
              <Text style={styles.tierLabel}>{tier.label}</Text>
              {list.length === 0 ? (
                <Text style={styles.none}>Nobody configured at this tier.</Text>
              ) : (
                list.map((c) => (
                  <Card key={c.id}>
                    <View style={styles.rowBetween}>
                      <Text style={styles.name}>{c.full_name}</Text>
                      <Badge
                        text={c.is_verified ? "VERIFIED" : "UNVERIFIED"}
                        color={c.is_verified ? colors.success : colors.warning}
                      />
                    </View>
                    <Text style={styles.meta}>{c.phone}</Text>
                    {!!c.relationship && <Text style={styles.meta}>{c.relationship}</Text>}
                    <Pressable onPress={() => remove(c)}>
                      <Text style={styles.remove}>Remove</Text>
                    </Pressable>
                  </Card>
                ))
              )}
            </View>
          );
        })}

        <Button title="Add Contact" onPress={() => setModal(true)} />
      </ScrollView>

      <Modal visible={modal} animationType="slide" transparent>
        <View style={styles.modalWrap}>
          <View style={styles.modalCard}>
            <ScrollView keyboardShouldPersistTaps="handled">
              <Text style={styles.modalTitle}>New Emergency Contact</Text>

              <Field label="Full Name" value={form.full_name} onChangeText={set("full_name")} placeholder="Their name" autoCapitalize="words" />
              <Field label="Phone" value={form.phone} onChangeText={set("phone")} placeholder="9876543210" keyboardType="phone-pad" />
              <Field label="Email (optional)" value={form.email} onChangeText={set("email")} placeholder="them@example.com" keyboardType="email-address" />
              <Field label="Relationship" value={form.relationship} onChangeText={set("relationship")} placeholder="Son, Daughter, Neighbour" autoCapitalize="words" />

              <Text style={styles.fieldLabel}>Escalation Tier</Text>
              <View style={styles.tierRow}>
                {TIERS.map((t) => (
                  <Pressable
                    key={t.level}
                    onPress={() => set("escalation_level")(t.level)}
                    style={[styles.tierChip, form.escalation_level === t.level && styles.tierChipActive]}
                  >
                    <Text style={[styles.tierText, form.escalation_level === t.level && styles.tierTextActive]}>
                      Tier {t.level}
                    </Text>
                  </Pressable>
                ))}
              </View>

              <Button title="Save Contact" onPress={save} loading={saving} />
              <Button title="Cancel" variant="ghost" onPress={() => setModal(false)} />
            </ScrollView>
          </View>
        </View>
      </Modal>
    </>
  );
}

const styles = StyleSheet.create({
  scroll: { padding: 20, paddingBottom: 40, flexGrow: 1 },
  section: { marginBottom: 20 },
  tierLabel: { color: colors.text, fontSize: 15, fontWeight: "700", marginBottom: 10 },
  none: { color: colors.muted, fontSize: 13, marginBottom: 8, fontStyle: "italic" },
  rowBetween: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  name: { color: colors.text, fontSize: 16, fontWeight: "700", flex: 1 },
  meta: { color: colors.muted, fontSize: 13, marginTop: 4 },
  remove: { color: colors.danger, fontSize: 13, marginTop: 10, fontWeight: "600" },
  modalWrap: { flex: 1, backgroundColor: "rgba(0,0,0,0.65)", justifyContent: "flex-end" },
  modalCard: {
    backgroundColor: colors.bg, borderTopLeftRadius: 20, borderTopRightRadius: 20,
    padding: 22, maxHeight: "88%",
  },
  modalTitle: { color: colors.text, fontSize: 20, fontWeight: "800", marginBottom: 18 },
  fieldLabel: { color: colors.muted, fontSize: 13, marginBottom: 8, fontWeight: "600" },
  tierRow: { flexDirection: "row", gap: 8, marginBottom: 18 },
  tierChip: {
    flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: "center",
    backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.border,
  },
  tierChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  tierText: { color: colors.muted, fontSize: 13, fontWeight: "600" },
  tierTextActive: { color: "#fff" },
});
