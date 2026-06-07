package com.campprotect.scamshield.services;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000j\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000b\n\u0002\b\u0004\n\u0002\u0010\b\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010#\n\u0000\n\u0002\u0010\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0004\n\u0002\u0010 \n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u000b\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\u0018\u0010\u0018\u001a\u00020\u00192\u0006\u0010\u001a\u001a\u00020\u00042\u0006\u0010\u001b\u001a\u00020\u0004H\u0002J\b\u0010\u001c\u001a\u00020\u001dH\u0002J\b\u0010\u001e\u001a\u00020\u0019H\u0002J.\u0010\u001f\u001a\u00020\u00192\u0006\u0010 \u001a\u00020\u000e2\f\u0010!\u001a\b\u0012\u0004\u0012\u00020\u00040\"2\u0006\u0010#\u001a\u00020\u00042\u0006\u0010$\u001a\u00020\u0004H\u0002J\u0014\u0010%\u001a\u0004\u0018\u00010&2\b\u0010\'\u001a\u0004\u0018\u00010(H\u0016J\b\u0010)\u001a\u00020\u0019H\u0016J\b\u0010*\u001a\u00020\u0019H\u0016J\"\u0010+\u001a\u00020\u000e2\b\u0010\'\u001a\u0004\u0018\u00010(2\u0006\u0010,\u001a\u00020\u000e2\u0006\u0010-\u001a\u00020\u000eH\u0016J\b\u0010.\u001a\u00020\u0019H\u0002J\u0010\u0010/\u001a\u00020\u00192\u0006\u00100\u001a\u00020\tH\u0002J&\u00101\u001a\u00020\u00192\u0006\u0010 \u001a\u00020\u000e2\f\u0010!\u001a\b\u0012\u0004\u0012\u00020\u00040\"2\u0006\u00102\u001a\u00020\u0004H\u0002R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082D\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0004X\u0082D\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0006\u001a\u0004\u0018\u00010\u0007X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\b\u001a\u00020\tX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\n\u001a\u00020\tX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000b\u001a\u00020\u0004X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\f\u001a\u00020\u0004X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\r\u001a\u00020\u000eX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0012\u0010\u000f\u001a\u00060\u0010j\u0002`\u0011X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0012\u001a\u00020\u0013X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0014\u001a\u0004\u0018\u00010\u0015X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u0016\u001a\b\u0012\u0004\u0012\u00020\u00040\u0017X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u00063"}, d2 = {"Lcom/campprotect/scamshield/services/CallMonitoringForegroundService;", "Landroid/app/Service;", "()V", "CHANNEL_ID", "", "TAG", "alertManager", "Lcom/campprotect/scamshield/overlay/FraudAlertManager;", "alertTriggeredHigh", "", "alertTriggeredMedium", "currentCallNumber", "detectedCategory", "maxScoreReached", "", "rollingTranscript", "Ljava/lang/StringBuilder;", "Lkotlin/text/StringBuilder;", "scamEngine", "Lcom/campprotect/scamshield/scamdetection/ScamDetectionEngine;", "speechManager", "Lcom/campprotect/scamshield/speech/SpeechRecognizerManager;", "triggeredKeywords", "", "analyzeSpeech", "", "fullText", "latestPhrase", "createNotification", "Landroid/app/Notification;", "createNotificationChannel", "logAlertToDatabase", "score", "keywords", "", "phrase", "level", "onBind", "Landroid/os/IBinder;", "intent", "Landroid/content/Intent;", "onCreate", "onDestroy", "onStartCommand", "flags", "startId", "saveCallHistory", "sendMonitoringBroadcast", "active", "showOverlayWarning", "category", "app_release"})
public final class CallMonitoringForegroundService extends android.app.Service {
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String TAG = "MonitoringService";
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String CHANNEL_ID = "CallMonitorChannel";
    @org.jetbrains.annotations.Nullable()
    private com.campprotect.scamshield.speech.SpeechRecognizerManager speechManager;
    @org.jetbrains.annotations.Nullable()
    private com.campprotect.scamshield.overlay.FraudAlertManager alertManager;
    @org.jetbrains.annotations.NotNull()
    private final com.campprotect.scamshield.scamdetection.ScamDetectionEngine scamEngine = null;
    @org.jetbrains.annotations.NotNull()
    private java.lang.String currentCallNumber = "";
    @org.jetbrains.annotations.NotNull()
    private java.lang.StringBuilder rollingTranscript;
    private int maxScoreReached = 0;
    @org.jetbrains.annotations.NotNull()
    private java.lang.String detectedCategory = "Safe Call";
    @org.jetbrains.annotations.NotNull()
    private final java.util.Set<java.lang.String> triggeredKeywords = null;
    private boolean alertTriggeredMedium = false;
    private boolean alertTriggeredHigh = false;
    
    public CallMonitoringForegroundService() {
        super();
    }
    
    @java.lang.Override()
    @org.jetbrains.annotations.Nullable()
    public android.os.IBinder onBind(@org.jetbrains.annotations.Nullable()
    android.content.Intent intent) {
        return null;
    }
    
    @java.lang.Override()
    public void onCreate() {
    }
    
    @java.lang.Override()
    public int onStartCommand(@org.jetbrains.annotations.Nullable()
    android.content.Intent intent, int flags, int startId) {
        return 0;
    }
    
    private final void analyzeSpeech(java.lang.String fullText, java.lang.String latestPhrase) {
    }
    
    private final void showOverlayWarning(int score, java.util.List<java.lang.String> keywords, java.lang.String category) {
    }
    
    private final void logAlertToDatabase(int score, java.util.List<java.lang.String> keywords, java.lang.String phrase, java.lang.String level) {
    }
    
    private final void sendMonitoringBroadcast(boolean active) {
    }
    
    @java.lang.Override()
    public void onDestroy() {
    }
    
    private final void saveCallHistory() {
    }
    
    private final void createNotificationChannel() {
    }
    
    private final android.app.Notification createNotification() {
        return null;
    }
}