package com.campprotect.scamshield.repository;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000L\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\t\n\u0002\b\u0002\n\u0002\u0010 \n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\r\u0018\u00002\u00020\u0001B\r\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0002\u0010\u0004J\u000e\u0010\u0005\u001a\u00020\u0006H\u0086@\u00a2\u0006\u0002\u0010\u0007J\u000e\u0010\b\u001a\u00020\u0006H\u0086@\u00a2\u0006\u0002\u0010\u0007J\u0018\u0010\t\u001a\u0004\u0018\u00010\n2\u0006\u0010\u000b\u001a\u00020\fH\u0086@\u00a2\u0006\u0002\u0010\rJ\u0014\u0010\u000e\u001a\b\u0012\u0004\u0012\u00020\n0\u000fH\u0086@\u00a2\u0006\u0002\u0010\u0007J\u0014\u0010\u0010\u001a\b\u0012\u0004\u0012\u00020\u00110\u000fH\u0086@\u00a2\u0006\u0002\u0010\u0007J\u0014\u0010\u0012\u001a\b\u0012\u0004\u0012\u00020\u00130\u000fH\u0086@\u00a2\u0006\u0002\u0010\u0007J\u0018\u0010\u0014\u001a\u0004\u0018\u00010\u00132\u0006\u0010\u0015\u001a\u00020\u0016H\u0086@\u00a2\u0006\u0002\u0010\u0017J\u0010\u0010\u0018\u001a\u0004\u0018\u00010\u0019H\u0086@\u00a2\u0006\u0002\u0010\u0007J\u0016\u0010\u001a\u001a\u00020\f2\u0006\u0010\u001b\u001a\u00020\nH\u0086@\u00a2\u0006\u0002\u0010\u001cJ\u0016\u0010\u001d\u001a\u00020\f2\u0006\u0010\u001e\u001a\u00020\u0011H\u0086@\u00a2\u0006\u0002\u0010\u001fJ\u0016\u0010 \u001a\u00020\f2\u0006\u0010!\u001a\u00020\u0013H\u0086@\u00a2\u0006\u0002\u0010\"J\u0016\u0010#\u001a\u00020\u00062\u0006\u0010$\u001a\u00020\u0019H\u0086@\u00a2\u0006\u0002\u0010%R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006&"}, d2 = {"Lcom/campprotect/scamshield/repository/CallHistoryRepository;", "", "dao", "Lcom/campprotect/scamshield/database/CallHistoryDao;", "(Lcom/campprotect/scamshield/database/CallHistoryDao;)V", "clearAllAlertLogs", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "clearAllCalls", "getAlertLogById", "Lcom/campprotect/scamshield/database/FraudAlertLog;", "logId", "", "(JLkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getAllAlertLogs", "", "getAllCalls", "Lcom/campprotect/scamshield/database/CallHistory;", "getAllReputations", "Lcom/campprotect/scamshield/database/CallerReputation;", "getReputationByNumber", "phone", "", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getSettings", "Lcom/campprotect/scamshield/database/UserSettings;", "insertAlertLog", "log", "(Lcom/campprotect/scamshield/database/FraudAlertLog;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "insertCall", "call", "(Lcom/campprotect/scamshield/database/CallHistory;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "insertOrUpdateReputation", "reputation", "(Lcom/campprotect/scamshield/database/CallerReputation;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "saveSettings", "settings", "(Lcom/campprotect/scamshield/database/UserSettings;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_release"})
public final class CallHistoryRepository {
    @org.jetbrains.annotations.NotNull()
    private final com.campprotect.scamshield.database.CallHistoryDao dao = null;
    
    public CallHistoryRepository(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.CallHistoryDao dao) {
        super();
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object insertCall(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.CallHistory call, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getAllCalls(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.campprotect.scamshield.database.CallHistory>> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object clearAllCalls(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object insertAlertLog(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.FraudAlertLog log, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getAllAlertLogs(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.campprotect.scamshield.database.FraudAlertLog>> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getAlertLogById(long logId, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.campprotect.scamshield.database.FraudAlertLog> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object clearAllAlertLogs(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object insertOrUpdateReputation(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.CallerReputation reputation, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getReputationByNumber(@org.jetbrains.annotations.NotNull()
    java.lang.String phone, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.campprotect.scamshield.database.CallerReputation> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getAllReputations(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.campprotect.scamshield.database.CallerReputation>> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object saveSettings(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.UserSettings settings, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion) {
        return null;
    }
    
    @org.jetbrains.annotations.Nullable()
    public final java.lang.Object getSettings(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.campprotect.scamshield.database.UserSettings> $completion) {
        return null;
    }
}