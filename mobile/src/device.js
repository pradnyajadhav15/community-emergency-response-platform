import Constants from "expo-constants";
import * as Location from "expo-location";
import { Platform } from "react-native";

import api from "./api";

// expo-notifications removed remote push from Expo Go in SDK 53.
// Import it lazily so the app still runs in Expo Go; push works in a dev build.
const isExpoGo = Constants.appOwnership === "expo";

export async function registerPushToken() {
  if (isExpoGo) {
    console.log("Push notifications require a development build. Skipping in Expo Go.");
    return null;
  }

  try {
    const Notifications = require("expo-notifications");
    const Device = require("expo-device");

    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowBanner: true,
        shouldShowList: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
      }),
    });

    if (!Device.isDevice) return null;

    if (Platform.OS === "android") {
      await Notifications.setNotificationChannelAsync("emergency", {
        name: "Emergency Alerts",
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 400, 200, 400],
        lightColor: "#DC2626",
        sound: "default",
      });
    }

    const existing = await Notifications.getPermissionsAsync();
    let granted = existing.status;
    if (granted !== "granted") {
      const asked = await Notifications.requestPermissionsAsync();
      granted = asked.status;
    }
    if (granted !== "granted") return null;

    const { data } = await Notifications.getExpoPushTokenAsync();
    await api.post("/auth/push-token/", { expo_push_token: data });
    return data;
  } catch (e) {
    console.log("Push token registration skipped:", e.message);
    return null;
  }
}

export async function getCurrentLocation() {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== "granted") {
    return { granted: false, latitude: null, longitude: null };
  }
  try {
    const position = await Location.getCurrentPositionAsync({
      accuracy: Location.Accuracy.Balanced,
    });
    return {
      granted: true,
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
    };
  } catch {
    return { granted: true, latitude: null, longitude: null };
  }
}