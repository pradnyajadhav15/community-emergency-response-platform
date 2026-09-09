import { useState } from "react";
import { Link, useRouter } from "expo-router";
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { apiError } from "../src/api";
import { useAuth } from "../src/auth";
import { colors } from "../src/theme";
import { Banner, Button, Field } from "../src/ui";

export default function Login() {
  const { signIn } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (!username || !password) {
      setError("Enter both your username and password.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await signIn(username.trim(), password);
      router.replace("/home");
    } catch (e) {
      setError(apiError(e, "Login failed. Check your credentials."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Text style={styles.brand}>CERP</Text>
          <Text style={styles.tag}>Community Emergency Response</Text>
        </View>

        <Banner message={error} />

        <Field
          label="Username"
          value={username}
          onChangeText={setUsername}
          placeholder="resident1"
          autoCorrect={false}
        />
        <Field
          label="Password"
          value={password}
          onChangeText={setPassword}
          placeholder="Your password"
          secureTextEntry
        />

        <Button title="Sign In" onPress={submit} loading={loading} />

        <Link href="/register" asChild>
          <Text style={styles.link}>Do not have an account? Register</Text>
        </Link>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  scroll: { flexGrow: 1, justifyContent: "center", padding: 24 },
  header: { alignItems: "center", marginBottom: 36 },
  brand: { color: colors.text, fontSize: 44, fontWeight: "800", letterSpacing: 4 },
  tag: { color: colors.muted, fontSize: 14, marginTop: 8 },
  link: { color: colors.primary, textAlign: "center", marginTop: 22, fontSize: 15 },
});
