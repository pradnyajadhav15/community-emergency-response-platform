import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";

import { colors } from "./theme";

export function Field({ label, ...props }) {
  return (
    <View style={styles.fieldWrap}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        placeholderTextColor={colors.muted}
        style={styles.input}
        autoCapitalize="none"
        {...props}
      />
    </View>
  );
}

export function Button({ title, onPress, loading, variant = "primary", disabled }) {
  const bg =
    variant === "danger" ? colors.danger : variant === "ghost" ? "transparent" : colors.primary;
  return (
    <Pressable
      onPress={onPress}
      disabled={loading || disabled}
      style={({ pressed }) => [
        styles.button,
        { backgroundColor: bg, opacity: pressed || disabled ? 0.7 : 1 },
        variant === "ghost" && styles.ghost,
      ]}
    >
      {loading ? (
        <ActivityIndicator color="#fff" />
      ) : (
        <Text style={styles.buttonText}>{title}</Text>
      )}
    </Pressable>
  );
}

export function Banner({ message, type = "error" }) {
  if (!message) return null;
  const bg = type === "error" ? "#7F1D1D" : "#14532D";
  return (
    <View style={[styles.banner, { backgroundColor: bg }]}>
      <Text style={styles.bannerText}>{message}</Text>
    </View>
  );
}

export function Badge({ text, color }) {
  return (
    <View style={[styles.badge, { backgroundColor: color }]}>
      <Text style={styles.badgeText}>{text}</Text>
    </View>
  );
}

export function Card({ children, style }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

const styles = StyleSheet.create({
  fieldWrap: { marginBottom: 14 },
  label: { color: colors.muted, fontSize: 13, marginBottom: 6, fontWeight: "600" },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: colors.text,
    fontSize: 16,
  },
  button: {
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 8,
  },
  ghost: { borderWidth: 1, borderColor: colors.border },
  buttonText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  banner: { borderRadius: 10, padding: 12, marginBottom: 14 },
  bannerText: { color: "#fff", fontSize: 14 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 999, alignSelf: "flex-start" },
  badgeText: { color: "#fff", fontSize: 11, fontWeight: "700", letterSpacing: 0.5 },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: 12,
  },
});
