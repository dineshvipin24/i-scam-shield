// screens/HistoryScreen.js - Call history with risk badges and transcript viewer
import React, { useState, useEffect, useCallback } from "react";
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  RefreshControl, Modal, ScrollView, Alert,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { COLORS } from "../App";
import { fetchCalls, fetchCallDetail } from "../api";

// ─── Risk Badge ───────────────────────────────────────────────────────────────
function RiskBadge({ label }) {
  const config = {
    fraud:      { color: COLORS.fraud,      icon: "ban",              text: "FRAUD" },
    suspicious: { color: COLORS.suspicious, icon: "warning",          text: "SUSPICIOUS" },
    safe:       { color: COLORS.safe,       icon: "shield-checkmark", text: "SAFE" },
  };
  const c = config[label] || config.safe;
  return (
    <View style={[styles.badge, { backgroundColor: c.color + "22", borderColor: c.color + "66" }]}>
      <Ionicons name={c.icon} size={11} color={c.color} />
      <Text style={[styles.badgeText, { color: c.color }]}>{c.text}</Text>
    </View>
  );
}

// ─── Call Item ────────────────────────────────────────────────────────────────
function CallItem({ item, onPress }) {
  const date = item.started_at
    ? new Date(item.started_at).toLocaleString("en-IN", {
        day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
      })
    : "Unknown";

  const scorePercent = Math.round((item.final_score || 0) * 100);

  return (
    <TouchableOpacity style={styles.callCard} onPress={() => onPress(item)} activeOpacity={0.75}>
      <View style={styles.callLeft}>
        <View style={[styles.callIcon, {
          backgroundColor: item.risk_label === "fraud" ? COLORS.fraud + "22"
                         : item.risk_label === "suspicious" ? COLORS.suspicious + "22"
                         : COLORS.safe + "22"
        }]}>
          <Ionicons
            name={item.risk_label === "fraud" ? "ban" : item.risk_label === "suspicious" ? "warning" : "call"}
            size={20}
            color={item.risk_label === "fraud" ? COLORS.fraud : item.risk_label === "suspicious" ? COLORS.suspicious : COLORS.safe}
          />
        </View>
        <View style={styles.callInfo}>
          <Text style={styles.callNumber}>{item.from_number || "Unknown"}</Text>
          <Text style={styles.callDate}>{date}</Text>
          {item.action_taken && item.action_taken !== "none" && (
            <Text style={styles.callAction}>
              {item.action_taken === "warning_injected" ? "⚡ Warning Injected" : "📴 Hung Up"}
            </Text>
          )}
        </View>
      </View>
      <View style={styles.callRight}>
        <RiskBadge label={item.risk_label} />
        <Text style={[styles.callScore, {
          color: item.risk_label === "fraud" ? COLORS.fraud
               : item.risk_label === "suspicious" ? COLORS.suspicious
               : COLORS.safe
        }]}>
          {scorePercent}%
        </Text>
      </View>
    </TouchableOpacity>
  );
}

// ─── Detail Modal ─────────────────────────────────────────────────────────────
function CallDetailModal({ call, visible, onClose }) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (visible && call) {
      setLoading(true);
      fetchCallDetail(call.call_sid)
        .then(setDetail)
        .catch(() => setDetail(null))
        .finally(() => setLoading(false));
    }
  }, [visible, call]);

  if (!call) return null;

  return (
    <Modal visible={visible} animationType="slide" presentationStyle="pageSheet" onRequestClose={onClose}>
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
            <Ionicons name="close" size={24} color={COLORS.text} />
          </TouchableOpacity>
          <Text style={styles.modalTitle}>Call Details</Text>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView style={styles.modalContent}>
          {/* Overview */}
          <View style={styles.detailCard}>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>From</Text>
              <Text style={styles.detailValue}>{call.from_number}</Text>
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Risk Score</Text>
              <Text style={[styles.detailValue, {
                color: call.risk_label === "fraud" ? COLORS.fraud
                     : call.risk_label === "suspicious" ? COLORS.suspicious
                     : COLORS.safe
              }]}>
                {Math.round((call.final_score || 0) * 100)}%
              </Text>
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Status</Text>
              <RiskBadge label={call.risk_label} />
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Action</Text>
              <Text style={styles.detailValue}>
                {call.action_taken === "warning_injected" ? "⚡ Warning Injected"
                 : call.action_taken === "hung_up" ? "📴 Auto Hung Up"
                 : "None"}
              </Text>
            </View>
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Started</Text>
              <Text style={styles.detailValue}>
                {call.started_at ? new Date(call.started_at).toLocaleString("en-IN") : "--"}
              </Text>
            </View>
          </View>

          {/* Score Timeline */}
          {detail?.score_events && detail.score_events.length > 0 && (
            <>
              <Text style={styles.modalSection}>Score Timeline</Text>
              <View style={styles.timelineContainer}>
                {detail.score_events.map((ev, i) => (
                  <View key={i} style={styles.timelineRow}>
                    <View style={[styles.timelineDot, {
                      backgroundColor: ev.label === "fraud" ? COLORS.fraud
                                     : ev.label === "suspicious" ? COLORS.suspicious
                                     : COLORS.safe
                    }]} />
                    <View style={styles.timelineInfo}>
                      <Text style={styles.timelineScore}>
                        {Math.round(ev.score * 100)}% — {ev.label.toUpperCase()}
                      </Text>
                      <Text style={styles.timelineText} numberOfLines={2}>
                        "{ev.transcript}"
                      </Text>
                    </View>
                  </View>
                ))}
              </View>
            </>
          )}
        </ScrollView>
      </View>
    </Modal>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────
export default function HistoryScreen() {
  const [calls, setCalls]         = useState([]);
  const [loading, setLoading]     = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCall, setSelected] = useState(null);
  const [filter, setFilter]       = useState("all"); // all|fraud|suspicious|safe

  const load = useCallback(async () => {
    try {
      const data = await fetchCalls(100);
      setCalls(data);
    } catch {
      // Backend offline
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { load(); }, []);

  const filtered = filter === "all" ? calls : calls.filter(c => c.risk_label === filter);

  const filters = [
    { key: "all",        label: "All",        color: COLORS.accent },
    { key: "fraud",      label: "🚨 Fraud",   color: COLORS.fraud },
    { key: "suspicious", label: "⚠️ Suspicious", color: COLORS.suspicious },
    { key: "safe",       label: "✅ Safe",    color: COLORS.safe },
  ];

  return (
    <View style={styles.container}>
      {/* Filter Tabs */}
      <View style={styles.filterRow}>
        {filters.map(f => (
          <TouchableOpacity
            key={f.key}
            style={[styles.filterBtn, filter === f.key && { backgroundColor: f.color + "22", borderColor: f.color }]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.filterText, filter === f.key && { color: f.color }]}>{f.label}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={filtered}
        keyExtractor={item => item.call_sid}
        renderItem={({ item }) => (
          <CallItem item={item} onPress={setSelected} />
        )}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing}
            onRefresh={() => { setRefreshing(true); load(); }}
            tintColor={COLORS.accent}
          />
        }
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="time-outline" size={48} color={COLORS.textMuted} />
            <Text style={styles.emptyText}>No calls yet</Text>
            <Text style={styles.emptySubtext}>Call history will appear here</Text>
          </View>
        }
      />

      <CallDetailModal
        call={selectedCall}
        visible={!!selectedCall}
        onClose={() => setSelected(null)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container:  { flex: 1, backgroundColor: COLORS.bg },
  list:       { padding: 16, paddingBottom: 32 },

  // Filter
  filterRow:  { flexDirection: "row", gap: 8, paddingHorizontal: 16, paddingVertical: 12 },
  filterBtn:  { flex: 1, paddingVertical: 6, borderRadius: 20, borderWidth: 1, borderColor: COLORS.border, alignItems: "center" },
  filterText: { color: COLORS.textMuted, fontSize: 11, fontWeight: "600" },

  // Call Card
  callCard:  { flexDirection: "row", justifyContent: "space-between", alignItems: "center", backgroundColor: COLORS.surface, borderRadius: 14, padding: 14, marginBottom: 10, borderWidth: 1, borderColor: COLORS.border },
  callLeft:  { flexDirection: "row", alignItems: "center", flex: 1 },
  callIcon:  { width: 42, height: 42, borderRadius: 21, justifyContent: "center", alignItems: "center", marginRight: 12 },
  callInfo:  { flex: 1 },
  callNumber: { color: COLORS.text, fontSize: 15, fontWeight: "600" },
  callDate:   { color: COLORS.textMuted, fontSize: 12, marginTop: 2 },
  callAction: { color: COLORS.accent, fontSize: 11, marginTop: 2 },
  callRight: { alignItems: "flex-end", gap: 6 },
  callScore: { fontSize: 16, fontWeight: "800" },

  // Badge
  badge:     { flexDirection: "row", alignItems: "center", gap: 4, paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10, borderWidth: 1 },
  badgeText: { fontSize: 10, fontWeight: "700", letterSpacing: 0.3 },

  // Empty
  empty:        { alignItems: "center", justifyContent: "center", paddingTop: 80, gap: 8 },
  emptyText:    { color: COLORS.text, fontSize: 18, fontWeight: "600" },
  emptySubtext: { color: COLORS.textMuted, fontSize: 13 },

  // Modal
  modalContainer: { flex: 1, backgroundColor: COLORS.bg },
  modalHeader:    { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 16, borderBottomWidth: 1, borderBottomColor: COLORS.border },
  modalTitle:     { color: COLORS.text, fontSize: 17, fontWeight: "700" },
  closeBtn:       { width: 40, height: 40, borderRadius: 20, backgroundColor: COLORS.surface, justifyContent: "center", alignItems: "center" },
  modalContent:   { padding: 16 },
  modalSection:   { color: COLORS.text, fontSize: 15, fontWeight: "700", marginTop: 16, marginBottom: 10 },

  // Detail Card
  detailCard: { backgroundColor: COLORS.surface, borderRadius: 14, padding: 16, borderWidth: 1, borderColor: COLORS.border, gap: 14 },
  detailRow:  { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  detailLabel: { color: COLORS.textMuted, fontSize: 13 },
  detailValue: { color: COLORS.text, fontSize: 13, fontWeight: "600" },

  // Timeline
  timelineContainer: { gap: 12 },
  timelineRow:  { flexDirection: "row", alignItems: "flex-start", gap: 10 },
  timelineDot:  { width: 10, height: 10, borderRadius: 5, marginTop: 4 },
  timelineInfo: { flex: 1 },
  timelineScore: { color: COLORS.text, fontSize: 13, fontWeight: "600" },
  timelineText:  { color: COLORS.textMuted, fontSize: 12, marginTop: 2 },
});
