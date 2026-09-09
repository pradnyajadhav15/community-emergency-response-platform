import { ScrollView, StyleSheet, Text, View } from "react-native";

import { useAuth } from "../src/auth";
import { colors, roleLabels } from "../src/theme";
import { Button, Card } from "../src/ui";

export default function Home() {
  const { user, signOut } = useAuth();

  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      <Text style={styles.greeting}>Hello, {user?.first_name || user?.username}</Text>
      <Text style={styles.role}>{roleLabels[user?.role] || user?.role}</Text>

      <Card>
        <Text style={styles.cardTitle}>Signed in successfully</Text>
        <Text style={styles.cardBody}>
          Your account is connected to the CERP backend. Role-specific screens are coming next.
        </Text>
      </Card>

      <Card>
        <Text style={styles.cardTitle}>Account</Text>
        <Text style={styles.detail}>Username: {user?.username}</Text>
        <Text style={styles.detail}>Email: {user?.email || "not set"}</Text>
        <Text style={styles.detail}>Phone: {user?.phone || "not set"}</Text>
      </Card>

      <Button title="Sign Out" variant="ghost" onPress={signOut} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { padding: 20, paddingTop: 60, backgroundColor: colors.bg, flexGrow: 1 },
  greeting: { color: colors.text, fontSize: 26, fontWeight: "800" },
  role: { color: colors.muted, fontSize: 15, marginBottom: 24 },
  cardTitle: { color: colors.text, fontSize: 16, fontWeight: "700", marginBottom: 8 },
  cardBody: { color: colors.muted, fontSize: 14, lineHeight: 20 },
  detail: { color: colors.muted, fontSize: 14, marginBottom: 4 },
});
