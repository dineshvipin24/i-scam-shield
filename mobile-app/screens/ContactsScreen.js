// screens/ContactsScreen.js
// Syncs phone contacts to backend so only UNKNOWN callers are monitored.

import React, { useState, useEffect } from "react";
import {
  View, Text, StyleSheet, TouchableOpacity,
  Alert, ActivityIndicator, ScrollView,
} from "react-native";
import * as Contacts from "expo-contacts";
import { Ionicons } from "@expo/vector-icons";
import { COLORS } from "../App";
import { syncContacts, fetchContactsCount } from "../api";

export default function ContactsScreen() {
  const [synced, setSynced]     = useState(0);
  const [syncing, setSyncing]   = useState(false);
  const [permission, setPermission] = useState(null);
  const [lastSync, setLastSync] = useState(null);

  useEffect(() => {
    loadCount();
    checkPermission();
  }, []);

  const checkPermission = async () => {
    const { status } = await Contacts.getPermissionsAsync();
    setPermission(status);
  };

  const loadCount = async () => {
    try {
      const data = await fetchContactsCount();
      setSynced(data.count);
    } catch {}
  };

  const handleSync = async () => {
    // 1. Request permission
    const { status } = await Contacts.requestPermissionsAsync();
    setPermission(status);
    if (status !== "granted") {
      Alert.alert(
        "Permission Required",
        "Contacts permission is needed to identify unknown callers. Only phone numbers are sent to the server — not names or emails.",
        [{ text: "OK" }]
      );
      return;
    }

    setSyncing(true);
    try {
      // 2. Fetch all contacts
      const { data } = await Contacts.getContactsAsync({
        fields: [Contacts.Fields.PhoneNumbers, Contacts.Fields.Name],
      });

      // 3. Extract phone numbers
      const contacts = [];
      for (const c of data) {
        if (c.phoneNumbers) {
          for (const ph of c.phoneNumbers) {
            if (ph.number) {
              contacts.push({ name: c.name || null, phone: ph.number });
            }
          }
        }
      }

      // 4. Upload to backend
      const result = await syncContacts(contacts);
      setSynced(result.total_contacts);
      setLastSync(new Date().toLocaleTimeString("en-IN"));
      Alert.alert(
        "✅ Contacts Synced",
        `${result.added} new numbers added.\nTotal saved contacts: ${result.total_contacts}\n\nOnly unknown callers will now be monitored by AI.`
      );
    } catch (e) {
      Alert.alert("Sync Failed", "Could not sync contacts. Is the server running?");
    } finally {
      setSyncing(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>

      {/* Status Card */}
      <View style={[styles.statusCard, { borderColor: synced > 0 ? COLORS.safe + "44" : COLORS.border }]}>
        <Ionicons
          name={synced > 0 ? "people" : "people-outline"}
          size={36}
          color={synced > 0 ? COLORS.safe : COLORS.textMuted}
        />
        <Text style={styles.statusNum}>{synced}</Text>
        <Text style={styles.statusLabel}>Contacts Synced</Text>
        {lastSync && <Text style={styles.statusSub}>Last sync: {lastSync}</Text>}
      </View>

      {/* How it works */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>How Unknown-Only Mode Works</Text>
        <View style={styles.steps}>
          {[
            { icon: "call-outline",       text: "Any incoming call arrives" },
            { icon: "search-outline",     text: "Backend checks if number is in your contacts" },
            { icon: "people-outline",     text: "Known contact → call forwarded normally, no AI" },
            { icon: "alert-circle-outline", text: "Unknown caller → AI monitoring activated" },
            { icon: "shield-checkmark-outline", text: "If scam detected → push alert on your phone" },
          ].map((s, i) => (
            <View key={i} style={styles.step}>
              <View style={styles.stepNum}><Text style={styles.stepNumText}>{i + 1}</Text></View>
              <Ionicons name={s.icon} size={18} color={COLORS.accent} style={{ marginRight: 8 }} />
              <Text style={styles.stepText}>{s.text}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* Privacy Note */}
      <View style={styles.privacyBox}>
        <Ionicons name="lock-closed-outline" size={16} color={COLORS.accent} />
        <Text style={styles.privacyText}>
          <Text style={{ color: COLORS.accent, fontWeight: "700" }}>Privacy: </Text>
          Only phone numbers are synced. Names stay on your device only and are never stored in the cloud.
        </Text>
      </View>

      {/* Sync Button */}
      <TouchableOpacity
        style={[styles.syncBtn, syncing && { opacity: 0.6 }]}
        onPress={handleSync}
        disabled={syncing}
        activeOpacity={0.8}
      >
        {syncing
          ? <ActivityIndicator color={COLORS.bg} />
          : <Ionicons name="sync" size={20} color={COLORS.bg} />
        }
        <Text style={styles.syncBtnText}>
          {syncing ? "Syncing..." : synced > 0 ? "Re-Sync Contacts" : "Sync Contacts Now"}
        </Text>
      </TouchableOpacity>

      {synced > 0 && (
        <Text style={styles.syncHint}>
          Unknown callers = anyone NOT in your {synced} saved contacts
        </Text>
      )}

      {/* Permission status */}
      {permission === "denied" && (
        <View style={styles.permWarn}>
          <Ionicons name="warning-outline" size={16} color={COLORS.suspicious} />
          <Text style={styles.permWarnText}>
            Contacts permission denied. Go to phone Settings → AI Scam Shield → Allow Contacts.
          </Text>
        </View>
      )}

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bg },
  content:   { padding: 20, paddingBottom: 40, gap: 16 },

  statusCard:  { backgroundColor: COLORS.surface, borderRadius: 20, padding: 24, alignItems: "center", gap: 6, borderWidth: 1 },
  statusNum:   { fontSize: 48, fontWeight: "900", color: COLORS.text },
  statusLabel: { color: COLORS.textMuted, fontSize: 14 },
  statusSub:   { color: COLORS.textMuted, fontSize: 12 },

  card:      { backgroundColor: COLORS.surface, borderRadius: 16, padding: 16, borderWidth: 1, borderColor: COLORS.border },
  cardTitle: { color: COLORS.text, fontSize: 15, fontWeight: "700", marginBottom: 14 },
  steps:     { gap: 12 },
  step:      { flexDirection: "row", alignItems: "center" },
  stepNum:   { width: 24, height: 24, borderRadius: 12, backgroundColor: COLORS.accentGlow, justifyContent: "center", alignItems: "center", marginRight: 8, flexShrink: 0 },
  stepNumText:{ color: COLORS.accent, fontSize: 11, fontWeight: "700" },
  stepText:  { color: COLORS.text, fontSize: 13, flex: 1 },

  privacyBox:  { flexDirection: "row", gap: 10, backgroundColor: COLORS.accentGlow, borderRadius: 12, padding: 12, borderWidth: 1, borderColor: COLORS.accent + "33" },
  privacyText: { flex: 1, color: COLORS.text, fontSize: 12, lineHeight: 18 },

  syncBtn:     { backgroundColor: COLORS.accent, borderRadius: 16, paddingVertical: 16, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 10 },
  syncBtnText: { color: COLORS.bg, fontSize: 16, fontWeight: "800" },
  syncHint:    { color: COLORS.textMuted, fontSize: 12, textAlign: "center" },

  permWarn:     { flexDirection: "row", gap: 8, backgroundColor: COLORS.suspicious + "11", borderRadius: 10, padding: 10, borderWidth: 1, borderColor: COLORS.suspicious + "44" },
  permWarnText: { flex: 1, color: COLORS.suspicious, fontSize: 12, lineHeight: 18 },
});
