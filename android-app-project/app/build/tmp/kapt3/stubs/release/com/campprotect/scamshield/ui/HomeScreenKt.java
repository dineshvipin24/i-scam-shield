package com.campprotect.scamshield.ui;

@kotlin.Metadata(mv = {1, 9, 0}, k = 2, xi = 48, d1 = {"\u0000P\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0003\n\u0002\u0010 \n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\u001a\u0010\u0010\u0000\u001a\u00020\u00012\u0006\u0010\u0002\u001a\u00020\u0003H\u0007\u001a\u0010\u0010\u0004\u001a\u00020\u00012\u0006\u0010\u0005\u001a\u00020\u0006H\u0007\u001a\u0010\u0010\u0007\u001a\u00020\u00012\u0006\u0010\b\u001a\u00020\tH\u0007\u001a\u0092\u0001\u0010\n\u001a\u00020\u00012\u0006\u0010\u000b\u001a\u00020\f2\f\u0010\r\u001a\b\u0012\u0004\u0012\u00020\u000f0\u000e2\f\u0010\u0010\u001a\b\u0012\u0004\u0012\u00020\u00060\u000e2\f\u0010\u0011\u001a\b\u0012\u0004\u0012\u00020\u00120\u000e2\f\u0010\u0013\u001a\b\u0012\u0004\u0012\u00020\u00060\u000e2\f\u0010\u0014\u001a\b\u0012\u0004\u0012\u00020\u00060\u000e2\u0012\u0010\u0015\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00030\u00160\u000e2\u0012\u0010\u0017\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\t0\u00160\u000e2\u0012\u0010\u0018\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00190\u00160\u000eH\u0007\u001a&\u0010\u001a\u001a\u00020\u00012\u0006\u0010\u001b\u001a\u00020\u00192\f\u0010\u001c\u001a\b\u0012\u0004\u0012\u00020\u00010\u001d2\u0006\u0010\u000b\u001a\u00020\fH\u0007\u00a8\u0006\u001e"}, d2 = {"CallHistoryCard", "", "call", "Lcom/campprotect/scamshield/database/CallHistory;", "EmptyStateMessage", "message", "", "FraudAlertRowContent", "alert", "Lcom/campprotect/scamshield/database/FraudAlertLog;", "HomeScreen", "activity", "Lcom/campprotect/scamshield/activities/MainActivity;", "isMonitoring", "Lkotlinx/coroutines/flow/StateFlow;", "", "activeNumber", "liveScore", "", "liveCategory", "livePhrase", "callHistory", "", "alertLogs", "reputationLogs", "Lcom/campprotect/scamshield/database/CallerReputation;", "ReputationCard", "rep", "onUpdate", "Lkotlin/Function0;", "app_release"})
public final class HomeScreenKt {
    
    @kotlin.OptIn(markerClass = {androidx.compose.material3.ExperimentalMaterial3Api.class})
    @androidx.compose.runtime.Composable()
    public static final void HomeScreen(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.activities.MainActivity activity, @org.jetbrains.annotations.NotNull()
    kotlinx.coroutines.flow.StateFlow<java.lang.Boolean> isMonitoring, @org.jetbrains.annotations.NotNull()
    kotlinx.coroutines.flow.StateFlow<java.lang.String> activeNumber, @org.jetbrains.annotations.NotNull()
    kotlinx.coroutines.flow.StateFlow<java.lang.Integer> liveScore, @org.jetbrains.annotations.NotNull()
    kotlinx.coroutines.flow.StateFlow<java.lang.String> liveCategory, @org.jetbrains.annotations.NotNull()
    kotlinx.coroutines.flow.StateFlow<java.lang.String> livePhrase, @org.jetbrains.annotations.NotNull()
    kotlinx.coroutines.flow.StateFlow<? extends java.util.List<com.campprotect.scamshield.database.CallHistory>> callHistory, @org.jetbrains.annotations.NotNull()
    kotlinx.coroutines.flow.StateFlow<? extends java.util.List<com.campprotect.scamshield.database.FraudAlertLog>> alertLogs, @org.jetbrains.annotations.NotNull()
    kotlinx.coroutines.flow.StateFlow<? extends java.util.List<com.campprotect.scamshield.database.CallerReputation>> reputationLogs) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void FraudAlertRowContent(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.FraudAlertLog alert) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void ReputationCard(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.CallerReputation rep, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onUpdate, @org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.activities.MainActivity activity) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void EmptyStateMessage(@org.jetbrains.annotations.NotNull()
    java.lang.String message) {
    }
    
    @androidx.compose.runtime.Composable()
    public static final void CallHistoryCard(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.CallHistory call) {
    }
}