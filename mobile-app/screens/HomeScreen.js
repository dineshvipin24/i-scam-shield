// screens/HomeScreen.js - Live risk gauge + call status dashboard
import React, { useState, useEffect, useRef } from "react";
import {
  View, Text, StyleSheet, ScrollView, Animated,
  TouchableOpacity, Dimensions, RefreshControl, Alert,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { COLORS } from "../App";
import { fetchStats, checkHealth } from "../api";

const { width } = Dimensions.get("window");

// ─── Risk Gauge Component ─────────────────────────────────────────────────────
function RiskGauge({ score = 0, label = "safe" }) {
  const animValue = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.spring(animValue, {
      toValue: score,
      friction: 6,
      tension: 40,
      useNativeDriver: false,
    }).start();
  }, [score]);

  const gaugeColor = label === "fraud"
    ? COLORS.fraud
    : label === "suspicious"
    ? COLORS.suspicious
    : COLORS.safe;

  const arcWidth = animValue.interpolate({
    inputRange: [0, 1],
    outputRange: ["0%", "100%"],
    extrapolate: "clamp",
  });

  const percent = Math.round(score * 100);

  return (
    <View style={styles.gaugeContainer}>
      {/* Outer glow ring */}
      <View style={[styles.gaugeRing, { borderColor: gaugeColor + "44" }]}>
        <View style={[styles.gaugeInner, { borderColor: gaugeColor }]}>
          <Text style={[styles.gaugePercent, { color: gaugeColor }]}>
            {percent}%
          </Text>
          <Text style={styles.gaugeSubtext}>Risk Score</Text>
        </View>
      </View>

      {/* Label badge */}
      <View style={[styles.labelBadge, { backgroundColor: gaugeColor + "22", borderColor: gaugeColor + "66" }]}>
        <Text style={[styles.labelText, { color: gaugeColor }]}>
          {label === "fraud" ? "🚨 FRAUD DETECTED" :
           label === "suspicious" ? "⚠️ SUSPICIOUS" : "✅ SAFE"}
        </Text>
      </View>

      {/* Linear progress bar */}
      <View style={styles.progressTrack}>
        <Animated.View
          style={[
            styles.progressFill,
            { width: arcWidth, backgroundColor: gaugeColor },
          ]}
        />
      </View>
      <View style={styles.progressLabels}>
        <Text style={styles.progressLabel}>0</Text>
        <Text style={styles.progressLabel}>Safe</Text>
        <Text style={styles.progressLabel}>Suspicious</Text>
        <Text style={styles.progressLabel}>Fraud</Text>
        <Text style={styles.progressLabel}>1.0</Text>
      </View>
    </View>
  );
}


// ─── Stat Card Component ──────────────────────────────────────────────────────
function StatCard({ icon, value, label, color }) {
  return (
    <View style={[styles.statCard, { borderColor: color + "44" }]}>
      <Ionicons name={icon} size={22} color={color} />
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}


// ─── Main Screen ──────────────────────────────────────────────────────────────
export default function HomeScreen({ navigation }) {
  const [stats, setStats]       = useState(null);
  const [health, setHealth]     = useState(null);
  const [loading, setLoading]   = useState(true);
  const [demoScore, setDemoScore] = useState(0.0);
  const [demoLabel, setDemoLabel] = useState("safe");
  const [demoing, setDemoing]   = useState(false);

  const pulseAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Pulse animation for active call indicator
  useEffect(() => {
    const pulse = Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, { toValue: 1.15, duration: 800, useNativeDriver: true }),
        Animated.timing(pulseAnim, { toValue: 1.0,  duration: 800, useNativeDriver: true }),
      ])
    );
    pulse.start();
    return () => pulse.stop();
  }, []);

  const loadData = async () => {
    try {
      const [statsData, healthData] = await Promise.all([
        fetchStats(),
        checkHealth(),
      ]);
      setStats(statsData);
      setHealth(healthData);
    } catch (e) {
      // Backend might not be running
    } finally {
      setLoading(false);
    }
  };

  // Demo: simulate a scam call detection for the pitch
  const runDemo = () => {
    if (demoing) return;
    setDemoing(true);
    setDemoScore(0);
    setDemoLabel("safe");

    const steps = [
      { score: 0.05, label: "safe",       delay: 500  },
      { score: 0.15, label: "safe",       delay: 1500 },
      { score: 0.32, label: "safe",       delay: 2500 },
      { score: 0.48, label: "suspicious", delay: 3500 },
      { score: 0.61, label: "suspicious", delay: 4500 },
      { score: 0.74, label: "fraud",      delay: 5500 },
      { score: 0.89, label: "fraud",      delay: 6500 },
      { score: 0.95, label: "fraud",      delay: 7500 },
    ];

    steps.forEach(({ score, label, delay }) => {
      setTimeout(() => {
        setDemoScore(score);
        setDemoLabel(label);
        if (score >= 0.74) {
          // Show alert when fraud detected
          if (score === 0.74) {
            Alert.alert(
              "🚨 FRAUD DETECTED",
              "AI Scam Shield has detected fraud!\nRisk Score: 74%\n\nInjecting warning into call...\nDisconnecting scammer.",
              [{ text: "OK", style: "destructive" }]
            );
          }
        }
      }, delay);
    });

    setTimeout(() => setDemoing(false), 9000);
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={loading} onRefresh={loadData}
          tintColor={COLORS.accent} />
      }
    >
      {/* ── Status Bar ── */}
      <View style={styles.statusBar}>
        <View style={styles.statusLeft}>
          <Animated.View style={[
            styles.statusDot,
            {
              backgroundColor: health?.online ? COLORS.safe : COLORS.fraud,
              transform: [{ scale: health?.online ? pulseAnim : 1 }],
            }
          ]} />
          <Text style={styles.statusText}>
            {health?.online ? "Server Online" : "Server Offline"}
          </Text>
        </View>
        <Text style={styles.statusRight}>
          Model: {health?.model_loaded ? "✅ Loaded" : "⏳ Demo Mode"}
        </Text>
      </View>

      {/* ── Hero Gauge ── */}
      <View style={styles.heroCard}>
        <Text style={styles.heroTitle}>Live Call Monitor</Text>
        <Text style={styles.heroSub}>
          Real-time AI scam detection
        </Text>
        <RiskGauge score={demoScore} label={demoLabel} />

        {/* Demo Button */}
        <TouchableOpacity
          style={[styles.demoBtn, demoing && styles.demoBtnActive]}
          onPress={runDemo}
          disabled={demoing}
          activeOpacity={0.8}
        >
          <Ionicons
            name={demoing ? "radio" : "play-circle"}
            size={18}
            color={COLORS.bg}
          />
          <Text style={styles.demoBtnText}>
            {demoing ? "Simulating Call..." : "▶ Demo Scam Call"}
          </Text>
        </TouchableOpacity>
      </View>

      {/* ── Stats Grid ── */}
      <Text style={styles.sectionTitle}>Call Statistics</Text>
      <View style={styles.statsGrid}>
        <StatCard
          icon="call"
          value={stats?.total_calls ?? "--"}
          label="Total Calls"
          color={COLORS.accent}
        />
        <StatCard
          icon="shield-checkmark"
          value={stats?.safe_calls ?? "--"}
          label="Safe"
          color={COLORS.safe}
        />
        <StatCard
          icon="warning"
          value={stats?.suspicious_calls ?? "--"}
          label="Suspicious"
          color={COLORS.suspicious}
        />
        <StatCard
          icon="ban"
          value={stats?.blocked_calls ?? "--"}
          label="Blocked"
          color={COLORS.fraud}
        />
      </View>

      {/* ── How It Works ── */}
      <Text style={styles.sectionTitle}>How It Works</Text>
      <View style={styles.howCard}>
        {[
          { icon: "call-outline",      step: "1", text: "Call routed through Twilio cloud bridge" },
          { icon: "mic-outline",       step: "2", text: "Audio streamed via WebSocket in real-time" },
          { icon: "text-outline",      step: "3", text: "Speech converted to text (Deepgram STT)" },
          { icon: "hardware-chip-outline", step: "4", text: "LSTM AI model scores for scam patterns" },
          { icon: "flash-outline",     step: "5", text: "Warning injected or call terminated instantly" },
        ].map(({ icon, step, text }) => (
          <View key={step} style={styles.howRow}>
            <View style={styles.howStep}>
              <Text style={styles.howStepNum}>{step}</Text>
            </View>
            <Ionicons name={icon} size={20} color={COLORS.accent} style={{ marginRight: 10 }} />
            <Text style={styles.howText}>{text}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container:  { flex: 1, backgroundColor: COLORS.bg },
  content:    { padding: 16, paddingBottom: 32 },

  // Status
  statusBar:   { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12, paddingHorizontal: 4 },
  statusLeft:  { flexDirection: "row", alignItems: "center", gap: 8 },
  statusDot:   { width: 10, height: 10, borderRadius: 5 },
  statusText:  { color: COLORS.text, fontSize: 13 },
  statusRight: { color: COLORS.textMuted, fontSize: 12 },

  // Hero Card
  heroCard:   { backgroundColor: COLORS.surface, borderRadius: 20, padding: 20, marginBottom: 20, borderWidth: 1, borderColor: COLORS.border },
  heroTitle:  { color: COLORS.text, fontSize: 20, fontWeight: "700", marginBottom: 4 },
  heroSub:    { color: COLORS.textMuted, fontSize: 13, marginBottom: 16 },

  // Gauge
  gaugeContainer: { alignItems: "center", marginBottom: 16 },
  gaugeRing:      { width: 160, height: 160, borderRadius: 80, borderWidth: 8, justifyContent: "center", alignItems: "center", marginBottom: 12 },
  gaugeInner:     { width: 130, height: 130, borderRadius: 65, borderWidth: 3, justifyContent: "center", alignItems: "center", backgroundColor: COLORS.bg },
  gaugePercent:   { fontSize: 36, fontWeight: "800" },
  gaugeSubtext:   { color: COLORS.textMuted, fontSize: 12, marginTop: 2 },
  labelBadge:     { borderRadius: 20, paddingHorizontal: 16, paddingVertical: 6, borderWidth: 1, marginBottom: 16 },
  labelText:      { fontSize: 14, fontWeight: "700", letterSpacing: 0.5 },
  progressTrack:  { width: "100%", height: 8, backgroundColor: COLORS.border, borderRadius: 4, overflow: "hidden" },
  progressFill:   { height: "100%", borderRadius: 4 },
  progressLabels: { flexDirection: "row", justifyContent: "space-between", width: "100%", marginTop: 4 },
  progressLabel:  { color: COLORS.textMuted, fontSize: 9 },

  // Demo Button
  demoBtn:       { flexDirection: "row", alignItems: "center", gap: 8, backgroundColor: COLORS.accent, borderRadius: 12, paddingVertical: 12, paddingHorizontal: 20, marginTop: 8, justifyContent: "center" },
  demoBtnActive: { backgroundColor: COLORS.suspicious },
  demoBtnText:   { color: COLORS.bg, fontSize: 15, fontWeight: "700" },

  // Stats
  sectionTitle: { color: COLORS.text, fontSize: 16, fontWeight: "700", marginBottom: 12, marginTop: 4 },
  statsGrid:    { flexDirection: "row", flexWrap: "wrap", gap: 10, marginBottom: 20 },
  statCard:     { flex: 1, minWidth: "45%", backgroundColor: COLORS.surface, borderRadius: 14, padding: 16, alignItems: "center", gap: 6, borderWidth: 1 },
  statValue:    { fontSize: 28, fontWeight: "800" },
  statLabel:    { color: COLORS.textMuted, fontSize: 12 },

  // How It Works
  howCard: { backgroundColor: COLORS.surface, borderRadius: 16, padding: 16, borderWidth: 1, borderColor: COLORS.border, gap: 14 },
  howRow:  { flexDirection: "row", alignItems: "center" },
  howStep: { width: 26, height: 26, borderRadius: 13, backgroundColor: COLORS.accentGlow, justifyContent: "center", alignItems: "center", marginRight: 10 },
  howStepNum: { color: COLORS.accent, fontSize: 12, fontWeight: "700" },
  howText:    { color: COLORS.text, fontSize: 13, flex: 1, lineHeight: 18 },
});
