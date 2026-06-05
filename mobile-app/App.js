// App.js - Main entry with push notifications + 4-tab navigation
import React, { useEffect, useRef } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createStackNavigator } from "@react-navigation/stack";
import { StatusBar } from "expo-status-bar";
import { Ionicons } from "@expo/vector-icons";
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";

import HomeScreen from "./screens/HomeScreen";
import HistoryScreen from "./screens/HistoryScreen";
import SettingsScreen from "./screens/SettingsScreen";
import ContactsScreen from "./screens/ContactsScreen";
import LiveCallScreen from "./screens/LiveCallScreen";
import { registerPushToken } from "./api";

const Tab   = createBottomTabNavigator();
const Stack = createStackNavigator();

// ─── Design Tokens ────────────────────────────────────────────────────────────
export const COLORS = {
  bg:         "#0A0E1A",
  surface:    "#111827",
  surfaceAlt: "#1A2235",
  border:     "#1E2D45",
  accent:     "#00D4FF",
  accentGlow: "#00D4FF33",
  safe:       "#00E676",
  suspicious: "#FFB300",
  fraud:      "#FF1744",
  text:       "#E8EAF0",
  textMuted:  "#607080",
  white:      "#FFFFFF",
};

// ─── Push Notification Setup ──────────────────────────────────────────────────
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge:  true,
  }),
});

async function registerForPushNotifications() {
  if (!Device.isDevice) return null;
  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;
  if (existing !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  if (finalStatus !== "granted") return null;
  const token = (await Notifications.getExpoPushTokenAsync()).data;
  return token;
}

// ─── Tab Navigator ────────────────────────────────────────────────────────────
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons = {
            Home:     focused ? "shield"          : "shield-outline",
            History:  focused ? "time"            : "time-outline",
            Contacts: focused ? "people"          : "people-outline",
            Settings: focused ? "settings"        : "settings-outline",
          };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor:   COLORS.accent,
        tabBarInactiveTintColor: COLORS.textMuted,
        tabBarStyle: {
          backgroundColor: COLORS.surface,
          borderTopColor:  COLORS.border,
          borderTopWidth:  1,
          height: 62,
          paddingBottom: 8,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
        headerStyle:      { backgroundColor: COLORS.bg, elevation: 0, shadowOpacity: 0 },
        headerTintColor:  COLORS.text,
        headerTitleStyle: { fontWeight: "700", fontSize: 18 },
      })}
    >
      <Tab.Screen name="Home"     component={HomeScreen}     options={{ title: "🛡️ Scam Shield" }} />
      <Tab.Screen name="History"  component={HistoryScreen}  options={{ title: "Call History" }} />
      <Tab.Screen name="Contacts" component={ContactsScreen} options={{ title: "Contacts Sync" }} />
      <Tab.Screen name="Settings" component={SettingsScreen} options={{ title: "Settings" }} />
    </Tab.Navigator>
  );
}

// ─── Root Stack (includes LiveCallScreen as modal) ────────────────────────────
export default function App() {
  const navigationRef = useRef(null);
  const notificationListener = useRef(null);
  const responseListener     = useRef(null);

  useEffect(() => {
    // Register for push notifications
    registerForPushNotifications().then(token => {
      if (token) {
        console.log("[Push] Token:", token);
        registerPushToken(token).catch(() => {});
      }
    });

    // When a push notification is received while app is open
    notificationListener.current = Notifications.addNotificationReceivedListener(notif => {
      const data = notif.request.content.data;
      if (data?.type === "fraud" || data?.type === "suspicious") {
        // Auto-navigate to Live Call screen
        navigationRef.current?.navigate("LiveCall", {
          callSid:    data.call_sid,
          fromNumber: "Unknown Caller",
        });
      }
    });

    // When user TAPS a push notification
    responseListener.current = Notifications.addNotificationResponseReceivedListener(resp => {
      const data = resp.notification.request.content.data;
      if (data?.call_sid) {
        navigationRef.current?.navigate("LiveCall", {
          callSid:    data.call_sid,
          fromNumber: "Unknown Caller",
        });
      }
    });

    return () => {
      Notifications.removeNotificationSubscription(notificationListener.current);
      Notifications.removeNotificationSubscription(responseListener.current);
    };
  }, []);

  return (
    <NavigationContainer ref={navigationRef}>
      <StatusBar style="light" backgroundColor={COLORS.bg} />
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Main" component={MainTabs} />
        <Stack.Screen
          name="LiveCall"
          component={LiveCallScreen}
          options={{
            headerShown: true,
            title: "🚨 Live Call Monitor",
            headerStyle:      { backgroundColor: COLORS.bg },
            headerTintColor:  COLORS.text,
            headerTitleStyle: { fontWeight: "700", color: COLORS.fraud },
            presentation: "modal",
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
