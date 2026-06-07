package com.campprotect.scamshield.activities;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000l\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\b\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0002\b\t\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0005\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0006\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\u0006\u0010+\u001a\u00020,J\u0012\u0010-\u001a\u00020,2\b\u0010.\u001a\u0004\u0018\u00010/H\u0014J\b\u00100\u001a\u00020,H\u0014J\u0006\u00101\u001a\u00020,J\u000e\u00102\u001a\u00020,2\u0006\u00103\u001a\u00020\u0007J\u0006\u00104\u001a\u00020,R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082D\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0082D\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0006\u001a\u00020\u0007X\u0082D\u00a2\u0006\u0002\n\u0000R\u0017\u0010\b\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\n\u0010\u000bR\u001d\u0010\f\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u000e0\r0\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u000f\u0010\u000bR\u001d\u0010\u0010\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020\u00110\r0\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0012\u0010\u000bR\u0017\u0010\u0013\u001a\b\u0012\u0004\u0012\u00020\u00140\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0015\u0010\u000bR\u0017\u0010\u0016\u001a\b\u0012\u0004\u0012\u00020\u00140\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0016\u0010\u000bR\u0017\u0010\u0017\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u0018\u0010\u000bR\u0017\u0010\u0019\u001a\b\u0012\u0004\u0012\u00020\u00070\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001a\u0010\u000bR\u0017\u0010\u001b\u001a\b\u0012\u0004\u0012\u00020\u00040\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\u001c\u0010\u000bR\u000e\u0010\u001d\u001a\u00020\u001eX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001a\u0010\u001f\u001a\u00020 X\u0086.\u00a2\u0006\u000e\n\u0000\u001a\u0004\b!\u0010\"\"\u0004\b#\u0010$R\u001d\u0010%\u001a\u000e\u0012\n\u0012\b\u0012\u0004\u0012\u00020&0\r0\t\u00a2\u0006\b\n\u0000\u001a\u0004\b\'\u0010\u000bR\u0017\u0010(\u001a\b\u0012\u0004\u0012\u00020)0\t\u00a2\u0006\b\n\u0000\u001a\u0004\b*\u0010\u000b\u00a8\u00065"}, d2 = {"Lcom/campprotect/scamshield/activities/MainActivity;", "Landroidx/activity/ComponentActivity;", "()V", "REQUEST_OVERLAY_PERMISSION", "", "REQUEST_SCREENING_ROLE", "TAG", "", "activeNumberState", "Lkotlinx/coroutines/flow/MutableStateFlow;", "getActiveNumberState", "()Lkotlinx/coroutines/flow/MutableStateFlow;", "alertLogsState", "", "Lcom/campprotect/scamshield/database/FraudAlertLog;", "getAlertLogsState", "callLogsState", "Lcom/campprotect/scamshield/database/CallHistory;", "getCallLogsState", "consentAcceptedState", "", "getConsentAcceptedState", "isMonitoringState", "liveCategoryState", "getLiveCategoryState", "livePhraseState", "getLivePhraseState", "liveScoreState", "getLiveScoreState", "monitorReceiver", "Landroid/content/BroadcastReceiver;", "repository", "Lcom/campprotect/scamshield/repository/CallHistoryRepository;", "getRepository", "()Lcom/campprotect/scamshield/repository/CallHistoryRepository;", "setRepository", "(Lcom/campprotect/scamshield/repository/CallHistoryRepository;)V", "reputationState", "Lcom/campprotect/scamshield/database/CallerReputation;", "getReputationState", "settingsState", "Lcom/campprotect/scamshield/database/UserSettings;", "getSettingsState", "checkAndRequestPermissions", "", "onCreate", "savedInstanceState", "Landroid/os/Bundle;", "onDestroy", "refreshData", "startTestMonitoring", "phoneNumber", "stopTestMonitoring", "app_release"})
public final class MainActivity extends androidx.activity.ComponentActivity {
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String TAG = "MainActivity";
    private final int REQUEST_OVERLAY_PERMISSION = 3001;
    private final int REQUEST_SCREENING_ROLE = 3002;
    public com.campprotect.scamshield.repository.CallHistoryRepository repository;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.lang.Boolean> isMonitoringState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.lang.String> activeNumberState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.lang.Integer> liveScoreState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.lang.String> liveCategoryState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.lang.String> livePhraseState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.util.List<com.campprotect.scamshield.database.CallHistory>> callLogsState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.util.List<com.campprotect.scamshield.database.FraudAlertLog>> alertLogsState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.util.List<com.campprotect.scamshield.database.CallerReputation>> reputationState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.campprotect.scamshield.database.UserSettings> settingsState = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<java.lang.Boolean> consentAcceptedState = null;
    @org.jetbrains.annotations.NotNull()
    private final android.content.BroadcastReceiver monitorReceiver = null;
    
    public MainActivity() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final com.campprotect.scamshield.repository.CallHistoryRepository getRepository() {
        return null;
    }
    
    public final void setRepository(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.repository.CallHistoryRepository p0) {
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.lang.Boolean> isMonitoringState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.lang.String> getActiveNumberState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.lang.Integer> getLiveScoreState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.lang.String> getLiveCategoryState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.lang.String> getLivePhraseState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.util.List<com.campprotect.scamshield.database.CallHistory>> getCallLogsState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.util.List<com.campprotect.scamshield.database.FraudAlertLog>> getAlertLogsState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.util.List<com.campprotect.scamshield.database.CallerReputation>> getReputationState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<com.campprotect.scamshield.database.UserSettings> getSettingsState() {
        return null;
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<java.lang.Boolean> getConsentAcceptedState() {
        return null;
    }
    
    @java.lang.Override()
    protected void onCreate(@org.jetbrains.annotations.Nullable()
    android.os.Bundle savedInstanceState) {
    }
    
    public final void refreshData() {
    }
    
    public final void checkAndRequestPermissions() {
    }
    
    /**
     * Diagnostic testing utility to start monitoring programmatically (e.g. for student presentation tests).
     */
    public final void startTestMonitoring(@org.jetbrains.annotations.NotNull()
    java.lang.String phoneNumber) {
    }
    
    public final void stopTestMonitoring() {
    }
    
    @java.lang.Override()
    protected void onDestroy() {
    }
}