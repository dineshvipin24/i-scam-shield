package com.campprotect.scamshield.services;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000&\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\b\u0007\u0018\u00002\u00020\u0001B\u0005\u00a2\u0006\u0002\u0010\u0002J\u0010\u0010\u0007\u001a\u00020\b2\u0006\u0010\t\u001a\u00020\u0004H\u0002J\u0010\u0010\n\u001a\u00020\b2\u0006\u0010\u000b\u001a\u00020\fH\u0016R\u000e\u0010\u0003\u001a\u00020\u0004X\u0082D\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0005\u001a\u00020\u0006X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\r"}, d2 = {"Lcom/campprotect/scamshield/services/CallScreeningServiceImpl;", "Landroid/telecom/CallScreeningService;", "()V", "TAG", "", "reputationEngine", "Lcom/campprotect/scamshield/scamdetection/CallerReputationEngine;", "listenForCallState", "", "phoneNumber", "onScreenCall", "callDetails", "Landroid/telecom/Call$Details;", "app_release"})
@androidx.annotation.RequiresApi(value = android.os.Build.VERSION_CODES.Q)
public final class CallScreeningServiceImpl extends android.telecom.CallScreeningService {
    @org.jetbrains.annotations.NotNull()
    private final java.lang.String TAG = "CallScreeningService";
    @org.jetbrains.annotations.NotNull()
    private final com.campprotect.scamshield.scamdetection.CallerReputationEngine reputationEngine = null;
    
    public CallScreeningServiceImpl() {
        super();
    }
    
    @java.lang.Override()
    public void onScreenCall(@org.jetbrains.annotations.NotNull()
    android.telecom.Call.Details callDetails) {
    }
    
    private final void listenForCallState(java.lang.String phoneNumber) {
    }
}