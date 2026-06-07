package com.campprotect.scamshield.speech;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000D\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0002\n\u0002\b\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0010\b\n\u0002\b\u0005\u0018\u00002\u00020\u0001BE\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00126\u0010\u0004\u001a2\u0012\u0013\u0012\u00110\u0006\u00a2\u0006\f\b\u0007\u0012\b\b\b\u0012\u0004\b\b(\t\u0012\u0013\u0012\u00110\n\u00a2\u0006\f\b\u0007\u0012\b\b\b\u0012\u0004\b\b(\u000b\u0012\u0004\u0012\u00020\f0\u0005\u00a2\u0006\u0002\u0010\rJ\u0006\u0010\u0014\u001a\u00020\fJ\u0010\u0010\u0015\u001a\u00020\u00062\u0006\u0010\u0016\u001a\u00020\u0017H\u0002J\b\u0010\u0018\u001a\u00020\fH\u0002J\b\u0010\u0019\u001a\u00020\fH\u0002J\u0006\u0010\u001a\u001a\u00020\fJ\u0006\u0010\u001b\u001a\u00020\fR\u000e\u0010\u000e\u001a\u00020\u0006X\u0082D\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000f\u001a\u00020\nX\u0082\u000e\u00a2\u0006\u0002\n\u0000R>\u0010\u0004\u001a2\u0012\u0013\u0012\u00110\u0006\u00a2\u0006\f\b\u0007\u0012\b\b\b\u0012\u0004\b\b(\t\u0012\u0013\u0012\u00110\n\u00a2\u0006\f\b\u0007\u0012\b\b\b\u0012\u0004\b\b(\u000b\u0012\u0004\u0012\u00020\f0\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0010\u001a\u0004\u0018\u00010\u0011X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0012\u001a\u0004\u0018\u00010\u0013X\u0082\u000e\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u001c"}, d2 = {"Lcom/campprotect/scamshield/speech/SpeechRecognizerManager;", "", "context", "Landroid/content/Context;", "onResultCallback", "Lkotlin/Function2;", "", "Lkotlin/ParameterName;", "name", "text", "", "isFinal", "", "(Landroid/content/Context;Lkotlin/jvm/functions/Function2;)V", "TAG", "isListening", "recognizerIntent", "Landroid/content/Intent;", "speechRecognizer", "Landroid/speech/SpeechRecognizer;", "destroy", "getErrorText", "errorCode", "", "initializeRecognizer", "restartListening", "startListening", "stopListening", "app_release"})
public final class SpeechRecognizerManager {
    @org.jetbrains.annotations.NotNull()
    private final android.content.Context context = null;
    @org.jetbrains.annotations.NotNull()
    private final kotlin.jvm.functions.Function2<java.lang.String, java.lang.Boolean, kotlin.Unit> onResultCallback = null;
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String TAG = "SpeechRecognizerManager";
    @org.jetbrains.annotations.Nullable()
    private android.speech.SpeechRecognizer speechRecognizer;
    @org.jetbrains.annotations.Nullable()
    private android.content.Intent recognizerIntent;
    private boolean isListening = false;
    
    public SpeechRecognizerManager(@org.jetbrains.annotations.NotNull()
    android.content.Context context, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function2<? super java.lang.String, ? super java.lang.Boolean, kotlin.Unit> onResultCallback) {
        super();
    }
    
    private final void initializeRecognizer() {
    }
    
    public final void startListening() {
    }
    
    public final void stopListening() {
    }
    
    private final void restartListening() {
    }
    
    public final void destroy() {
    }
    
    private final java.lang.String getErrorText(int errorCode) {
        return null;
    }
}