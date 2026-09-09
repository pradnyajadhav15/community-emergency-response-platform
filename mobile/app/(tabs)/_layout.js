import { useEffect } from "react";
import { Redirect, Tabs } from "expo-router";
import { ActivityIndicator, Text, View } from "react-native";

import { useAuth } from "../../src/auth";
import { registerPushToken } from "../../src/device";
import { colors } from "../../src/theme";

function Icon({ label, focused }) {
  return (
    <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.45 }}>{label}</Text>
  );
}

export default function TabsLayout() {
  const { user, loading } = useAuth();

  useEffect(() => {
    if (user) registerPushToken();
  }, [user]);

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}>
        <ActivityIndicator color={colors.primary} />
      </View>
    );
  }

  if (!user) return <Redirect href="/login" />;

  const isResident = user.role === "RESIDENT";
  const isResponder = ["VOLUNTEER", "SECURITY", "GUARDIAN", "ADMIN"].includes(user.role);

  return (
    <Tabs
      screenOptions={{
        headerStyle: { backgroundColor: colors.bg },
        headerTintColor: colors.text,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.muted,
        sceneStyle: { backgroundColor: colors.bg },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: isResident ? "SOS" : "Incidents",
          tabBarIcon: ({ focused }) => <Icon label={isResident ? "🆘" : "📋"} focused={focused} />,
          headerShown: false,
        }}
      />
      <Tabs.Screen
        name="alerts"
        options={{
          title: "My Alerts",
          tabBarIcon: ({ focused }) => <Icon label="🔔" focused={focused} />,
          href: isResident ? "/alerts" : null,
        }}
      />
      <Tabs.Screen
        name="contacts"
        options={{
          title: "Contacts",
          tabBarIcon: ({ focused }) => <Icon label="👥" focused={focused} />,
          href: isResident ? "/contacts" : null,
        }}
      />
      <Tabs.Screen
        name="notifications"
        options={{
          title: "Inbox",
          tabBarIcon: ({ focused }) => <Icon label="📨" focused={focused} />,
          href: isResponder ? "/notifications" : null,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ focused }) => <Icon label="⚙️" focused={focused} />,
        }}
      />
    </Tabs>
  );
}
