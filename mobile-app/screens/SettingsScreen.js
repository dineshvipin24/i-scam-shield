// screens/SettingsScreen.js - Sensitivity controls + setup guide
import React, { useState, useEffect } from "react";
import {
  View, Text, StyleSheet, ScrollView, Switch,
  TouchableOpacity, TextInput, Alert, Linking, ActivityIndicator,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { COLORS } from "../App";
import { fetchSettings, updateSettings, checkHealth } from "../api";

// ─── Section Header ───────────────────────────────────────────────────────────
function Section({ title, icon }) {
  return (
    <View style={styles.sectionHeader}>
      <Ionicons name={icon} size={16} color={COLORS.accent} />
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );
}

// ─── Setting Row ──────────────────────────────────────────────────────────────
function SettingRow({ label, subtitle, children }) {
  return (
    <View style={styles.settingRow}>
      <View style={styles.settingLeft}>
        <Text style={styles.settingLabel}>{label}</Text>
        {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
      </View>
      {children}
    </View>
  );
}

// ─── Threshold Slider (manual steps) ─────────────────────────────────────────
function ThresholdControl({ value, onChange }) {
  const steps = [0.50, 0.60, 0.71, 0.80, 0.90];
  const labels = {
    0.50: "Very Sensitive",
    0.60: "Sensitive",
    0.71: "Balanced ✅",
    0.80: "Conservative",
    0.90: "Strict",
  };

  return (
    <View style={styles.thresholdContainer}>
      <View style={styles.thresholdRow}>
        {steps.map(step => (
          <TouchableOpacity
            key={step}
            style={[
              styles.thresholdBtn,
              Math.abs(value - step) < 0.01 && styles.thresholdBtnActive,
            ]}
            onPress={() => onChange(step)}
          >
            <Text style={[
              styles.thresholdBtnText,
              Math.abs(value - step) < 0.01 && styles.thresholdBtnTextActive,
            ]}>
              {Math.round(step * 100)}%
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <Text style={styles.thresholdLabel}>
        {labels[steps.find(s => Math.abs(value - s) < 0.01)] || `${Math.round(value * 100)}% threshold`}
      </Text>
    </View>
  );
}

// ─── Setup Guide Step ─────────────────────────────────────────────────────────
function GuideStep({ num, title, code, description }) {
  return (
    <View style={styles.guideStep}>
      <View style={styles.guideNum}>
        <Text style={styles.guideNumText}>{num}</Text>
      </View>
      <View style={styles.guideContent}>
        <Text style={styles.guideTitle}>{title}</Text>
        {code && (
          <View style={styles.codeBox}>
            <Text style={styles.codeText}>{code}</Text>
          </View>
        )}
        <Text style={styles.guideDesc}>{description}</Text>
      </View>
    </View>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────
export default function SettingsScreen() {
  const [settings, setSettings]   = useState(null);
  const [loading, setLoading]     = useState(true);
  const [saving, setSaving]       = useState(false);
  const [health, setHealth]       = useState(null);
  const [serverUrl, setServerUrl] = useState("");
  const [forwardTo, setForwardTo] = useState("");

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [s, h] = await Promise.all([fetchSettings(), checkHealth()]);
      setSettings(s);
      setHealth(h);
      setForwardTo(s.forward_to || "");
    } catch {
      // backend offline
    } finally {
      setLoading(false);
    }
  };

  const save = async (patch) => {
    setSaving(true);
    const updated = { ...settings, ...patch };
    setSettings(updated);
    try {
      await updateSettings(patch);
    } catch {
      Alert.alert("Error", "Could not save settings. Is the server running?");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={COLORS.accent} size="large" />
        <Text style={styles.loadingText}>Loading settings...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>

      {/* ── Server Status Card ── */}
      <View style={[styles.statusCard, { borderColor: health?.online ? COLORS.safe + "44" : COLORS.fraud + "44" }]}>
        <Ionicons
          name={health?.online ? "cloud-done" : "cloud-offline"}
          size={24}
          color={health?.online ? COLORS.safe : COLORS.fraud}
        />
        <View style={{ flex: 1 }}>
          <Text style={styles.statusTitle}>
            {health?.online ? "Server Connected" : "Server Offline"}
          </Text>
          <Text style={styles.statusSub}>
            {health?.online
              ? `Model: ${health.model_loaded ? "Loaded ✅" : "Demo Mode ⚠️"}`
              : "Start backend: uvicorn main:app --reload"
            }
          </Text>
        </View>
        <TouchableOpacity onPress={loadAll} style={styles.refreshBtn}>
          <Ionicons name="refresh" size={18} color={COLORS.accent} />
        </TouchableOpacity>
      </View>

      {/* ── AI Sensitivity ── */}
      <Section title="AI Sensitivity" icon="options" />
      <View style={styles.card}>
        <SettingRow
          label="Fraud Threshold"
          subtitle="Score above this → call is blocked"
        />
        <ThresholdControl
          value={settings?.risk_threshold ?? 0.71}
          onChange={v => save({ risk_threshold: v })}
        />

        <View style={styles.divider} />

        <SettingRow
          label="Auto Hangup"
          subtitle="Automatically disconnect fraudulent calls"
        >
          <Switch
            value={settings?.auto_hangup ?? true}
            onValueChange={v => save({ auto_hangup: v })}
            trackColor={{ false: COLORS.border, true: COLORS.fraud + "88" }}
            thumbColor={settings?.auto_hangup ? COLORS.fraud : COLORS.textMuted}
          />
        </SettingRow>

        <View style={styles.divider} />

        <SettingRow
          label="Suspicious Alerts"
          subtitle="Play audio warning for suspicious calls"
        >
          <Switch
            value={settings?.alert_suspicious ?? true}
            onValueChange={v => save({ alert_suspicious: v })}
            trackColor={{ false: COLORS.border, true: COLORS.suspicious + "88" }}
            thumbColor={settings?.alert_suspicious ? COLORS.suspicious : COLORS.textMuted}
          />
        </SettingRow>
      </View>

      {/* ── Risk Scale Reference ── */}
      <View style={styles.riskRef}>
        {[
          { range: "0 – 40%",  label: "Safe",        color: COLORS.safe },
          { range: "41 – 70%", label: "Suspicious",  color: COLORS.suspicious },
          { range: "71 – 100%",label: "Fraud Risk",  color: COLORS.fraud },
        ].map(r => (
          <View key={r.range} style={styles.riskRow}>
            <View style={[styles.riskDot, { backgroundColor: r.color }]} />
            <Text style={[styles.riskRange, { color: r.color }]}>{r.range}</Text>
            <Text style={styles.riskLabel}>{r.label}</Text>
          </View>
        ))}
      </View>

      {/* ── Call Forwarding ── */}
      <Section title="Call Forwarding" icon="git-network" />
      <View style={styles.card}>
        <SettingRow
          label="Your Real Number"
          subtitle="Calls will be forwarded here after screening"
        />
        <TextInput
          style={styles.input}
          value={forwardTo}
          onChangeText={setForwardTo}
          placeholder="+91XXXXXXXXXX"
          placeholderTextColor={COLORS.textMuted}
          keyboardType="phone-pad"
          onBlur={() => save({ forward_to: forwardTo })}
        />
      </View>

      {/* ── Setup Guide ── */}
      <Section title="Setup Guide" icon="book" />
      <View style={styles.guideCard}>
        <GuideStep
          num="1"
          title="Get Twilio Number"
          description="Sign up at twilio.com → buy a phone number → note your Account SID and Auth Token."
        />
        <GuideStep
          num="2"
          title="Start Backend Server"
          code="cd backend\npip install -r requirements.txt\ncopy .env.example .env\n# Edit .env with your keys\nuvicorn main:app --reload"
          description="The Python server listens on port 8000."
        />
        <GuideStep
          num="3"
          title="Expose with ngrok (Testing)"
          code="ngrok http 8000"
          description="Copy the https:// URL and paste it in SERVER_URL in your .env file."
        />
        <GuideStep
          num="4"
          title="Configure Twilio Webhook"
          description="In Twilio Console → Phone Numbers → your number → Voice & Fax → A Call Comes In → set Webhook URL to: https://YOUR_NGROK/twiml"
        />
        <GuideStep
          num="5"
          title="Enable Call Forwarding"
          code="*61*+1XXXXXXXXXX#"
          description="Dial this on your phone (replace with Twilio number) to forward unanswered calls. Or use the Twilio Voice SDK to route all calls."
        />
        <GuideStep
          num="6"
          title="Train the AI Model"
          code="cd backend/model\npython train_model.py"
          description="Trains the LSTM model on the scam dataset. Takes ~5 minutes. Saves scam_model.pth."
        />

        {/* Quick Links */}
        <View style={styles.linksRow}>
          {[
            { label: "Twilio Console", url: "https://console.twilio.com" },
            { label: "Deepgram API", url: "https://console.deepgram.com" },
            { label: "ngrok Download", url: "https://ngrok.com/download" },
          ].map(link => (
            <TouchableOpacity
              key={link.url}
              style={styles.linkBtn}
              onPress={() => Linking.openURL(link.url)}
            >
              <Ionicons name="open-outline" size={12} color={COLORS.accent} />
              <Text style={styles.linkText}>{link.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {saving && (
        <View style={styles.savingBar}>
          <ActivityIndicator size="small" color={COLORS.accent} />
          <Text style={styles.savingText}>Saving...</Text>
        </View>
      )}

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:  { flex: 1, backgroundColor: COLORS.bg },
  content:    { padding: 16, paddingBottom: 40 },
  loading:    { flex: 1, justifyContent: "center", alignItems: "center", gap: 12, backgroundColor: COLORS.bg },
  loadingText:{ color: COLORS.textMuted, fontSize: 14 },

  // Status Card
  statusCard:  { flexDirection: "row", alignItems: "center", gap: 12, backgroundColor: COLORS.surface, borderRadius: 14, padding: 14, marginBottom: 16, borderWidth: 1 },
  statusTitle: { color: COLORS.text, fontSize: 14, fontWeight: "600" },
  statusSub:   { color: COLORS.textMuted, fontSize: 12, marginTop: 2 },
  refreshBtn:  { padding: 8 },

  // Section
  sectionHeader: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 16, marginBottom: 10 },
  sectionTitle:  { color: COLORS.text, fontSize: 15, fontWeight: "700" },

  // Card
  card:    { backgroundColor: COLORS.surface, borderRadius: 16, padding: 16, borderWidth: 1, borderColor: COLORS.border, gap: 4, marginBottom: 8 },
  divider: { height: 1, backgroundColor: COLORS.border, marginVertical: 8 },

  // Setting Row
  settingRow:     { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  settingLeft:    { flex: 1, paddingRight: 12 },
  settingLabel:   { color: COLORS.text, fontSize: 14, fontWeight: "600" },
  settingSubtitle:{ color: COLORS.textMuted, fontSize: 12, marginTop: 2 },

  // Threshold
  thresholdContainer: { marginTop: 12 },
  thresholdRow:   { flexDirection: "row", gap: 6, marginBottom: 8 },
  thresholdBtn:   { flex: 1, paddingVertical: 8, borderRadius: 10, borderWidth: 1, borderColor: COLORS.border, alignItems: "center" },
  thresholdBtnActive: { backgroundColor: COLORS.accentGlow, borderColor: COLORS.accent },
  thresholdBtnText:   { color: COLORS.textMuted, fontSize: 12, fontWeight: "600" },
  thresholdBtnTextActive: { color: COLORS.accent },
  thresholdLabel: { color: COLORS.textMuted, fontSize: 12, textAlign: "center" },

  // Risk Reference
  riskRef:  { flexDirection: "row", justifyContent: "space-around", backgroundColor: COLORS.surface, borderRadius: 12, padding: 12, marginBottom: 8, borderWidth: 1, borderColor: COLORS.border },
  riskRow:  { alignItems: "center", gap: 4 },
  riskDot:  { width: 10, height: 10, borderRadius: 5 },
  riskRange:{ fontSize: 11, fontWeight: "700" },
  riskLabel:{ color: COLORS.textMuted, fontSize: 10 },

  // Input
  input: { backgroundColor: COLORS.bg, borderRadius: 10, paddingHorizontal: 14, paddingVertical: 10, color: COLORS.text, fontSize: 14, borderWidth: 1, borderColor: COLORS.border, marginTop: 8 },

  // Guide
  guideCard:    { backgroundColor: COLORS.surface, borderRadius: 16, padding: 16, borderWidth: 1, borderColor: COLORS.border, gap: 16, marginBottom: 8 },
  guideStep:    { flexDirection: "row", gap: 12 },
  guideNum:     { width: 28, height: 28, borderRadius: 14, backgroundColor: COLORS.accentGlow, justifyContent: "center", alignItems: "center", flexShrink: 0 },
  guideNumText: { color: COLORS.accent, fontSize: 13, fontWeight: "700" },
  guideContent: { flex: 1 },
  guideTitle:   { color: COLORS.text, fontSize: 14, fontWeight: "600", marginBottom: 4 },
  guideDesc:    { color: COLORS.textMuted, fontSize: 12, lineHeight: 18 },
  codeBox:      { backgroundColor: COLORS.bg, borderRadius: 8, padding: 10, marginBottom: 6, borderWidth: 1, borderColor: COLORS.border },
  codeText:     { color: COLORS.accent, fontSize: 11, fontFamily: "monospace" },

  // Links
  linksRow: { flexDirection: "row", gap: 8, flexWrap: "wrap", marginTop: 4 },
  linkBtn:  { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 10, paddingVertical: 6, backgroundColor: COLORS.accentGlow, borderRadius: 8, borderWidth: 1, borderColor: COLORS.accent + "44" },
  linkText: { color: COLORS.accent, fontSize: 11, fontWeight: "600" },

  // Saving
  savingBar:  { flexDirection: "row", alignItems: "center", gap: 8, justifyContent: "center", marginTop: 16 },
  savingText: { color: COLORS.textMuted, fontSize: 13 },
});
