import { useState } from "react";
import { useRouter } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { apiError } from "../src/api";
import { useAuth } from "../src/auth";
import { colors, roleLabels } from "../src/theme";
import { Banner, Button, Field } from "../src/ui";

const ROLES = ["RESIDENT", "GUARDIAN", "VOLUNTEER", "SECURITY"];

export default function Register() {
  const { signUp } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({
    username: "", email: "", first_name: "", phone: "",
    password: "", password2: "", role: "RESIDENT",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (key) => (value) => setForm((f) => ({ ...f, [key]: value }));

  async function submit() {
    if (!form.username || !form.password) {
      setError("Username and password are required.");
      return;
    }
    if (form.password !== form.password2) {
      setError("Passwords do not match.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await signUp(form);
      router.replace("/home");
    } catch (e) {
      setError(apiError(e, "Registration failed."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
      <Banner message={error} />

      <Field label="Username" value={form.username} onChangeText={set("username")} placeholder="yourname" />
      <Field label="Full Name" value={form.first_name} onChangeText={set("first_name")} placeholder="Your name" autoCapitalize="words" />
      <Field label="Email" value={form.email} onChangeText={set("email")} placeholder="you@example.com" keyboardType="email-address" />
      <Field label="Phone" value={form.phone} onChangeText={set("phone")} placeholder="9876543210" keyboardType="phone-pad" />

      <Text style={styles.label}>I am a</Text>
      <View style={styles.roleRow}>
        {ROLES.map((role) => (
          <Pressable
            key={role}
            onPress={() => set("role")(role)}
            style={[styles.roleChip, form.role === role && styles.roleChipActive]}
          >
            <Text style={[styles.roleText, form.role === role && styles.roleTextActive]}>
              {roleLabels[role]}
            </Text>
          </Pressable>
        ))}
      </View>

      <Field label="Password" value={form.password} onChangeText={set("password")} secureTextEntry placeholder="At least 8 characters" />
      <Field label="Confirm Password" value={form.password2} onChangeText={set("password2")} secureTextEntry placeholder="Repeat password" />

      <Button title="Create Account" onPress={submit} loading={loading} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { padding: 24, paddingBottom: 48, backgroundColor: colors.bg, flexGrow: 1 },
  label: { color: colors.muted, fontSize: 13, marginBottom: 8, fontWeight: "600" },
  roleRow: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 18 },
  roleChip: {
    paddingHorizontal: 14, paddingVertical: 9, borderRadius: 999,
    borderWidth: 1, borderColor: colors.border, backgroundColor: colors.surface,
  },
  roleChipActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  roleText: { color: colors.muted, fontSize: 14, fontWeight: "600" },
  roleTextActive: { color: "#fff" },
});
