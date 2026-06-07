package com.campprotect.scamshield.database;

@kotlin.Metadata(mv = {1, 9, 0}, k = 1, xi = 48, d1 = {"\u0000D\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0010\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\t\n\u0002\b\u0002\n\u0002\u0010 \n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\r\bg\u0018\u00002\u00020\u0001J\u000e\u0010\u0002\u001a\u00020\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u000e\u0010\u0005\u001a\u00020\u0003H\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0018\u0010\u0006\u001a\u0004\u0018\u00010\u00072\u0006\u0010\b\u001a\u00020\tH\u00a7@\u00a2\u0006\u0002\u0010\nJ\u0014\u0010\u000b\u001a\b\u0012\u0004\u0012\u00020\u00070\fH\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0014\u0010\r\u001a\b\u0012\u0004\u0012\u00020\u000e0\fH\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0014\u0010\u000f\u001a\b\u0012\u0004\u0012\u00020\u00100\fH\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0018\u0010\u0011\u001a\u0004\u0018\u00010\u00102\u0006\u0010\u0012\u001a\u00020\u0013H\u00a7@\u00a2\u0006\u0002\u0010\u0014J\u0010\u0010\u0015\u001a\u0004\u0018\u00010\u0016H\u00a7@\u00a2\u0006\u0002\u0010\u0004J\u0016\u0010\u0017\u001a\u00020\t2\u0006\u0010\u0018\u001a\u00020\u0007H\u00a7@\u00a2\u0006\u0002\u0010\u0019J\u0016\u0010\u001a\u001a\u00020\t2\u0006\u0010\u001b\u001a\u00020\u000eH\u00a7@\u00a2\u0006\u0002\u0010\u001cJ\u0016\u0010\u001d\u001a\u00020\t2\u0006\u0010\u001e\u001a\u00020\u0010H\u00a7@\u00a2\u0006\u0002\u0010\u001fJ\u0016\u0010 \u001a\u00020\u00032\u0006\u0010!\u001a\u00020\u0016H\u00a7@\u00a2\u0006\u0002\u0010\"\u00a8\u0006#"}, d2 = {"Lcom/campprotect/scamshield/database/CallHistoryDao;", "", "clearAllAlertLogs", "", "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "clearAllCalls", "getAlertLogById", "Lcom/campprotect/scamshield/database/FraudAlertLog;", "logId", "", "(JLkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getAllAlertLogs", "", "getAllCalls", "Lcom/campprotect/scamshield/database/CallHistory;", "getAllReputations", "Lcom/campprotect/scamshield/database/CallerReputation;", "getReputationByNumber", "phone", "", "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "getSettings", "Lcom/campprotect/scamshield/database/UserSettings;", "insertAlertLog", "log", "(Lcom/campprotect/scamshield/database/FraudAlertLog;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "insertCall", "call", "(Lcom/campprotect/scamshield/database/CallHistory;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "insertOrUpdateReputation", "reputation", "(Lcom/campprotect/scamshield/database/CallerReputation;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "saveSettings", "settings", "(Lcom/campprotect/scamshield/database/UserSettings;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;", "app_release"})
@androidx.room.Dao()
public abstract interface CallHistoryDao {
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object insertCall(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.CallHistory call, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM CallHistory ORDER BY timestamp DESC")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getAllCalls(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.campprotect.scamshield.database.CallHistory>> $completion);
    
    @androidx.room.Query(value = "DELETE FROM CallHistory")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object clearAllCalls(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object insertAlertLog(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.FraudAlertLog log, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM FraudAlertLog ORDER BY timestamp DESC")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getAllAlertLogs(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.campprotect.scamshield.database.FraudAlertLog>> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM FraudAlertLog WHERE id = :logId")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getAlertLogById(long logId, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.campprotect.scamshield.database.FraudAlertLog> $completion);
    
    @androidx.room.Query(value = "DELETE FROM FraudAlertLog")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object clearAllAlertLogs(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object insertOrUpdateReputation(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.CallerReputation reputation, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.lang.Long> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM CallerReputation WHERE phoneNumber = :phone")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getReputationByNumber(@org.jetbrains.annotations.NotNull()
    java.lang.String phone, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.campprotect.scamshield.database.CallerReputation> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM CallerReputation ORDER BY spamReportsCount DESC")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getAllReputations(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super java.util.List<com.campprotect.scamshield.database.CallerReputation>> $completion);
    
    @androidx.room.Insert(onConflict = 1)
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object saveSettings(@org.jetbrains.annotations.NotNull()
    com.campprotect.scamshield.database.UserSettings settings, @org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super kotlin.Unit> $completion);
    
    @androidx.room.Query(value = "SELECT * FROM UserSettings WHERE id = 1")
    @org.jetbrains.annotations.Nullable()
    public abstract java.lang.Object getSettings(@org.jetbrains.annotations.NotNull()
    kotlin.coroutines.Continuation<? super com.campprotect.scamshield.database.UserSettings> $completion);
}