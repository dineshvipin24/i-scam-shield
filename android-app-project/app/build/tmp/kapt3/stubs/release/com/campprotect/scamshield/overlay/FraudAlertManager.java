package com.campprotect.scamshield.overlay;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000J\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\b\n\u0000\n\u0002\u0010\u0002\n\u0002\b\r\n\u0002\u0010\u0016\n\u0000\u0018\u00002\u00020\u0001B\r\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u0006\u0010\u0013\u001a\u00020\u0014J\b\u0010\u0015\u001a\u00020\u0014H\u0002J\b\u0010\u0016\u001a\u00020\u0014H\u0002J\b\u0010\u0017\u001a\u00020\u0014H\u0002J\u0010\u0010\u0018\u001a\u00020\u00142\u0006\u0010\u0019\u001a\u00020\u0012H\u0016J\b\u0010\u001a\u001a\u00020\u0014H\u0002J\b\u0010\u001b\u001a\u00020\u0014H\u0002J\u0006\u0010\u001c\u001a\u00020\u0014J\u0006\u0010\u001d\u001a\u00020\u0014J\u0006\u0010\u001e\u001a\u00020\u0014J\u0006\u0010\u001f\u001a\u00020\u0014J\u000e\u0010 \u001a\u00020\u00142\u0006\u0010!\u001a\u00020\"R\u000e\u0010\u0005\u001a\u00020\u0006X\u0082D\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0007\u001a\u00020\bX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\t\u001a\u0004\u0018\u00010\nX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u000b\u001a\u0004\u0018\u00010\fX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0010\u0010\r\u001a\u0004\u0018\u00010\u000eX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000f\u001a\u00020\u0010X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0011\u001a\u00020\u0012X\u0082\u000e\u00a2\u0006\u0002\n\u0000\u00a8\u0006#"}, d2 = {"Lcom/campprotect/scamshield/overlay/FraudAlertManager;", "Landroid/speech/tts/TextToSpeech$OnInitListener;", "context", "Landroid/content/Context;", "(Landroid/content/Context;)V", "TAG", "", "activeSettings", "Lcom/campprotect/scamshield/database/UserSettings;", "mediaPlayer", "Landroid/media/MediaPlayer;", "soundPool", "Landroid/media/SoundPool;", "textToSpeech", "Landroid/speech/tts/TextToSpeech;", "ttsReady", "", "warningBeepId", "", "destroy", "", "initializeSoundPool", "initializeTTS", "loadSettingsAsync", "onInit", "status", "playFallbackAlarm", "playFallbackBeep", "playFraudAlarm", "playWarningBeep", "speakWarningText", "stopAlarm", "vibrateDevice", "pattern", "", "app_release"})
public final class FraudAlertManager implements android.speech.tts.TextToSpeech.OnInitListener {
    @org.jetbrains.annotations.NotNull()
    private final android.content.Context context = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String TAG = "FraudAlertManager";
    @org.jetbrains.annotations.Nullable()
    private android.media.MediaPlayer mediaPlayer;
    @org.jetbrains.annotations.Nullable()
    private android.media.SoundPool soundPool;
    @org.jetbrains.annotations.Nullable()
    private android.speech.tts.TextToSpeech textToSpeech;
    private boolean ttsReady = false;
    private int warningBeepId = -1;
    @org.jetbrains.annotations.NotNull()
    private com.campprotect.scamshield.database.UserSettings activeSettings;
    
    public FraudAlertManager(@org.jetbrains.annotations.NotNull()
    android.content.Context context) {
        super();
    }
    
    private final void loadSettingsAsync() {
    }
    
    private final void initializeSoundPool() {
    }
    
    private final void initializeTTS() {
    }
    
    @java.lang.Override()
    public void onInit(int status) {
    }
    
    /**
     * Speaks the warning statement.
     */
    public final void speakWarningText() {
    }
    
    public final void playWarningBeep() {
    }
    
    public final void playFraudAlarm() {
    }
    
    public final void stopAlarm() {
    }
    
    public final void vibrateDevice(@org.jetbrains.annotations.NotNull()
    long[] pattern) {
    }
    
    private final void playFallbackBeep() {
    }
    
    private final void playFallbackAlarm() {
    }
    
    public final void destroy() {
    }
}