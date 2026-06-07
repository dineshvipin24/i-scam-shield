package com.campprotect.scamshield.activities;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u00004\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0004\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\b\u0010\f\u001a\u00020\rH\u0002J\u0012\u0010\u000e\u001a\u00020\r2\b\u0010\u000f\u001a\u0004\u0018\u00010\u0010H\u0014J\b\u0010\u0011\u001a\u00020\rH\u0014J\u0010\u0010\u0012\u001a\u00020\r2\u0006\u0010\u0013\u001a\u00020\tH\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082.\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0006X\u0082.\u00a2\u0006\u0002\n\u0000R\u0017\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\t0\b\u00a2\u0006\b\n\u0000\u001a\u0004\b\n\u0010\u000b\u00a8\u0006\u0014"}, d2 = {"Lcom/campprotect/scamshield/activities/SettingsActivity;", "Landroidx/activity/ComponentActivity;", "()V", "alertManager", "Lcom/campprotect/scamshield/overlay/FraudAlertManager;", "repository", "Lcom/campprotect/scamshield/repository/CallHistoryRepository;", "settingsState", "Lkotlinx/coroutines/flow/MutableStateFlow;", "Lcom/campprotect/scamshield/database/UserSettings;", "getSettingsState", "()Lkotlinx/coroutines/flow/MutableStateFlow;", "loadSettings", "", "onCreate", "savedInstanceState", "Landroid/os/Bundle;", "onDestroy", "saveSettings", "updated", "app_release"})
public final class SettingsActivity extends androidx.activity.ComponentActivity {
    private com.campprotect.scamshield.overlay.FraudAlertManager alertManager;
    private com.campprotect.scamshield.repository.CallHistoryRepository repository;
    @org.jetbrains.annotations.NotNull()
    private final kotlinx.coroutines.flow.MutableStateFlow<com.campprotect.scamshield.database.UserSettings> settingsState = null;
    
    public SettingsActivity() {
        super();
    }
    
    @org.jetbrains.annotations.NotNull()
    public final kotlinx.coroutines.flow.MutableStateFlow<com.campprotect.scamshield.database.UserSettings> getSettingsState() {
        return null;
    }
    
    @java.lang.Override()
    protected void onCreate(@org.jetbrains.annotations.Nullable()
    android.os.Bundle savedInstanceState) {
    }
    
    private final void loadSettings() {
    }
    
    private final void saveSettings(com.campprotect.scamshield.database.UserSettings updated) {
    }
    
    @java.lang.Override()
    protected void onDestroy() {
    }
}