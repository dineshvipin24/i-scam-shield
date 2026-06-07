package com.campprotect.scamshield.database;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Long;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class CallHistoryDao_Impl implements CallHistoryDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<CallHistory> __insertionAdapterOfCallHistory;

  private final EntityInsertionAdapter<FraudAlertLog> __insertionAdapterOfFraudAlertLog;

  private final EntityInsertionAdapter<CallerReputation> __insertionAdapterOfCallerReputation;

  private final EntityInsertionAdapter<UserSettings> __insertionAdapterOfUserSettings;

  private final SharedSQLiteStatement __preparedStmtOfClearAllCalls;

  private final SharedSQLiteStatement __preparedStmtOfClearAllAlertLogs;

  public CallHistoryDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfCallHistory = new EntityInsertionAdapter<CallHistory>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `CallHistory` (`id`,`phoneNumber`,`timestamp`,`transcript`,`riskScore`,`riskLevel`,`classification`) VALUES (nullif(?, 0),?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final CallHistory entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getPhoneNumber());
        statement.bindLong(3, entity.getTimestamp());
        statement.bindString(4, entity.getTranscript());
        statement.bindLong(5, entity.getRiskScore());
        statement.bindString(6, entity.getRiskLevel());
        statement.bindString(7, entity.getClassification());
      }
    };
    this.__insertionAdapterOfFraudAlertLog = new EntityInsertionAdapter<FraudAlertLog>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `FraudAlertLog` (`id`,`phoneNumber`,`timestamp`,`riskScore`,`triggerKeyword`,`alertType`,`transcriptSnippet`,`category`) VALUES (nullif(?, 0),?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final FraudAlertLog entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getPhoneNumber());
        statement.bindLong(3, entity.getTimestamp());
        statement.bindLong(4, entity.getRiskScore());
        statement.bindString(5, entity.getTriggerKeyword());
        statement.bindString(6, entity.getAlertType());
        statement.bindString(7, entity.getTranscriptSnippet());
        statement.bindString(8, entity.getCategory());
      }
    };
    this.__insertionAdapterOfCallerReputation = new EntityInsertionAdapter<CallerReputation>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `CallerReputation` (`id`,`phoneNumber`,`spamReportsCount`,`scamReportsCount`,`localRiskScore`,`lastSeenTimestamp`,`userFeedbackValue`,`isSafe`) VALUES (nullif(?, 0),?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final CallerReputation entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getPhoneNumber());
        statement.bindLong(3, entity.getSpamReportsCount());
        statement.bindLong(4, entity.getScamReportsCount());
        statement.bindLong(5, entity.getLocalRiskScore());
        statement.bindLong(6, entity.getLastSeenTimestamp());
        statement.bindString(7, entity.getUserFeedbackValue());
        final int _tmp = entity.isSafe() ? 1 : 0;
        statement.bindLong(8, _tmp);
      }
    };
    this.__insertionAdapterOfUserSettings = new EntityInsertionAdapter<UserSettings>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `UserSettings` (`id`,`saveCallHistory`,`enableBeep`,`enableVibration`,`enableTTS`,`alertVolume`) VALUES (?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final UserSettings entity) {
        statement.bindLong(1, entity.getId());
        final int _tmp = entity.getSaveCallHistory() ? 1 : 0;
        statement.bindLong(2, _tmp);
        final int _tmp_1 = entity.getEnableBeep() ? 1 : 0;
        statement.bindLong(3, _tmp_1);
        final int _tmp_2 = entity.getEnableVibration() ? 1 : 0;
        statement.bindLong(4, _tmp_2);
        final int _tmp_3 = entity.getEnableTTS() ? 1 : 0;
        statement.bindLong(5, _tmp_3);
        statement.bindDouble(6, entity.getAlertVolume());
      }
    };
    this.__preparedStmtOfClearAllCalls = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM CallHistory";
        return _query;
      }
    };
    this.__preparedStmtOfClearAllAlertLogs = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM FraudAlertLog";
        return _query;
      }
    };
  }

  @Override
  public Object insertCall(final CallHistory call, final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfCallHistory.insertAndReturnId(call);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertAlertLog(final FraudAlertLog log,
      final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfFraudAlertLog.insertAndReturnId(log);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertOrUpdateReputation(final CallerReputation reputation,
      final Continuation<? super Long> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Long>() {
      @Override
      @NonNull
      public Long call() throws Exception {
        __db.beginTransaction();
        try {
          final Long _result = __insertionAdapterOfCallerReputation.insertAndReturnId(reputation);
          __db.setTransactionSuccessful();
          return _result;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object saveSettings(final UserSettings settings,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfUserSettings.insert(settings);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object clearAllCalls(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfClearAllCalls.acquire();
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfClearAllCalls.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Object clearAllAlertLogs(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfClearAllAlertLogs.acquire();
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfClearAllAlertLogs.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Object getAllCalls(final Continuation<? super List<CallHistory>> $completion) {
    final String _sql = "SELECT * FROM CallHistory ORDER BY timestamp DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<CallHistory>>() {
      @Override
      @NonNull
      public List<CallHistory> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfTranscript = CursorUtil.getColumnIndexOrThrow(_cursor, "transcript");
          final int _cursorIndexOfRiskScore = CursorUtil.getColumnIndexOrThrow(_cursor, "riskScore");
          final int _cursorIndexOfRiskLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "riskLevel");
          final int _cursorIndexOfClassification = CursorUtil.getColumnIndexOrThrow(_cursor, "classification");
          final List<CallHistory> _result = new ArrayList<CallHistory>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final CallHistory _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final String _tmpTranscript;
            _tmpTranscript = _cursor.getString(_cursorIndexOfTranscript);
            final int _tmpRiskScore;
            _tmpRiskScore = _cursor.getInt(_cursorIndexOfRiskScore);
            final String _tmpRiskLevel;
            _tmpRiskLevel = _cursor.getString(_cursorIndexOfRiskLevel);
            final String _tmpClassification;
            _tmpClassification = _cursor.getString(_cursorIndexOfClassification);
            _item = new CallHistory(_tmpId,_tmpPhoneNumber,_tmpTimestamp,_tmpTranscript,_tmpRiskScore,_tmpRiskLevel,_tmpClassification);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getAllAlertLogs(final Continuation<? super List<FraudAlertLog>> $completion) {
    final String _sql = "SELECT * FROM FraudAlertLog ORDER BY timestamp DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<FraudAlertLog>>() {
      @Override
      @NonNull
      public List<FraudAlertLog> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfRiskScore = CursorUtil.getColumnIndexOrThrow(_cursor, "riskScore");
          final int _cursorIndexOfTriggerKeyword = CursorUtil.getColumnIndexOrThrow(_cursor, "triggerKeyword");
          final int _cursorIndexOfAlertType = CursorUtil.getColumnIndexOrThrow(_cursor, "alertType");
          final int _cursorIndexOfTranscriptSnippet = CursorUtil.getColumnIndexOrThrow(_cursor, "transcriptSnippet");
          final int _cursorIndexOfCategory = CursorUtil.getColumnIndexOrThrow(_cursor, "category");
          final List<FraudAlertLog> _result = new ArrayList<FraudAlertLog>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final FraudAlertLog _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final int _tmpRiskScore;
            _tmpRiskScore = _cursor.getInt(_cursorIndexOfRiskScore);
            final String _tmpTriggerKeyword;
            _tmpTriggerKeyword = _cursor.getString(_cursorIndexOfTriggerKeyword);
            final String _tmpAlertType;
            _tmpAlertType = _cursor.getString(_cursorIndexOfAlertType);
            final String _tmpTranscriptSnippet;
            _tmpTranscriptSnippet = _cursor.getString(_cursorIndexOfTranscriptSnippet);
            final String _tmpCategory;
            _tmpCategory = _cursor.getString(_cursorIndexOfCategory);
            _item = new FraudAlertLog(_tmpId,_tmpPhoneNumber,_tmpTimestamp,_tmpRiskScore,_tmpTriggerKeyword,_tmpAlertType,_tmpTranscriptSnippet,_tmpCategory);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getAlertLogById(final long logId,
      final Continuation<? super FraudAlertLog> $completion) {
    final String _sql = "SELECT * FROM FraudAlertLog WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, logId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<FraudAlertLog>() {
      @Override
      @Nullable
      public FraudAlertLog call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "timestamp");
          final int _cursorIndexOfRiskScore = CursorUtil.getColumnIndexOrThrow(_cursor, "riskScore");
          final int _cursorIndexOfTriggerKeyword = CursorUtil.getColumnIndexOrThrow(_cursor, "triggerKeyword");
          final int _cursorIndexOfAlertType = CursorUtil.getColumnIndexOrThrow(_cursor, "alertType");
          final int _cursorIndexOfTranscriptSnippet = CursorUtil.getColumnIndexOrThrow(_cursor, "transcriptSnippet");
          final int _cursorIndexOfCategory = CursorUtil.getColumnIndexOrThrow(_cursor, "category");
          final FraudAlertLog _result;
          if (_cursor.moveToFirst()) {
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final long _tmpTimestamp;
            _tmpTimestamp = _cursor.getLong(_cursorIndexOfTimestamp);
            final int _tmpRiskScore;
            _tmpRiskScore = _cursor.getInt(_cursorIndexOfRiskScore);
            final String _tmpTriggerKeyword;
            _tmpTriggerKeyword = _cursor.getString(_cursorIndexOfTriggerKeyword);
            final String _tmpAlertType;
            _tmpAlertType = _cursor.getString(_cursorIndexOfAlertType);
            final String _tmpTranscriptSnippet;
            _tmpTranscriptSnippet = _cursor.getString(_cursorIndexOfTranscriptSnippet);
            final String _tmpCategory;
            _tmpCategory = _cursor.getString(_cursorIndexOfCategory);
            _result = new FraudAlertLog(_tmpId,_tmpPhoneNumber,_tmpTimestamp,_tmpRiskScore,_tmpTriggerKeyword,_tmpAlertType,_tmpTranscriptSnippet,_tmpCategory);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getReputationByNumber(final String phone,
      final Continuation<? super CallerReputation> $completion) {
    final String _sql = "SELECT * FROM CallerReputation WHERE phoneNumber = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, phone);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<CallerReputation>() {
      @Override
      @Nullable
      public CallerReputation call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfSpamReportsCount = CursorUtil.getColumnIndexOrThrow(_cursor, "spamReportsCount");
          final int _cursorIndexOfScamReportsCount = CursorUtil.getColumnIndexOrThrow(_cursor, "scamReportsCount");
          final int _cursorIndexOfLocalRiskScore = CursorUtil.getColumnIndexOrThrow(_cursor, "localRiskScore");
          final int _cursorIndexOfLastSeenTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "lastSeenTimestamp");
          final int _cursorIndexOfUserFeedbackValue = CursorUtil.getColumnIndexOrThrow(_cursor, "userFeedbackValue");
          final int _cursorIndexOfIsSafe = CursorUtil.getColumnIndexOrThrow(_cursor, "isSafe");
          final CallerReputation _result;
          if (_cursor.moveToFirst()) {
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final int _tmpSpamReportsCount;
            _tmpSpamReportsCount = _cursor.getInt(_cursorIndexOfSpamReportsCount);
            final int _tmpScamReportsCount;
            _tmpScamReportsCount = _cursor.getInt(_cursorIndexOfScamReportsCount);
            final int _tmpLocalRiskScore;
            _tmpLocalRiskScore = _cursor.getInt(_cursorIndexOfLocalRiskScore);
            final long _tmpLastSeenTimestamp;
            _tmpLastSeenTimestamp = _cursor.getLong(_cursorIndexOfLastSeenTimestamp);
            final String _tmpUserFeedbackValue;
            _tmpUserFeedbackValue = _cursor.getString(_cursorIndexOfUserFeedbackValue);
            final boolean _tmpIsSafe;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsSafe);
            _tmpIsSafe = _tmp != 0;
            _result = new CallerReputation(_tmpId,_tmpPhoneNumber,_tmpSpamReportsCount,_tmpScamReportsCount,_tmpLocalRiskScore,_tmpLastSeenTimestamp,_tmpUserFeedbackValue,_tmpIsSafe);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getAllReputations(final Continuation<? super List<CallerReputation>> $completion) {
    final String _sql = "SELECT * FROM CallerReputation ORDER BY spamReportsCount DESC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<List<CallerReputation>>() {
      @Override
      @NonNull
      public List<CallerReputation> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPhoneNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "phoneNumber");
          final int _cursorIndexOfSpamReportsCount = CursorUtil.getColumnIndexOrThrow(_cursor, "spamReportsCount");
          final int _cursorIndexOfScamReportsCount = CursorUtil.getColumnIndexOrThrow(_cursor, "scamReportsCount");
          final int _cursorIndexOfLocalRiskScore = CursorUtil.getColumnIndexOrThrow(_cursor, "localRiskScore");
          final int _cursorIndexOfLastSeenTimestamp = CursorUtil.getColumnIndexOrThrow(_cursor, "lastSeenTimestamp");
          final int _cursorIndexOfUserFeedbackValue = CursorUtil.getColumnIndexOrThrow(_cursor, "userFeedbackValue");
          final int _cursorIndexOfIsSafe = CursorUtil.getColumnIndexOrThrow(_cursor, "isSafe");
          final List<CallerReputation> _result = new ArrayList<CallerReputation>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final CallerReputation _item;
            final long _tmpId;
            _tmpId = _cursor.getLong(_cursorIndexOfId);
            final String _tmpPhoneNumber;
            _tmpPhoneNumber = _cursor.getString(_cursorIndexOfPhoneNumber);
            final int _tmpSpamReportsCount;
            _tmpSpamReportsCount = _cursor.getInt(_cursorIndexOfSpamReportsCount);
            final int _tmpScamReportsCount;
            _tmpScamReportsCount = _cursor.getInt(_cursorIndexOfScamReportsCount);
            final int _tmpLocalRiskScore;
            _tmpLocalRiskScore = _cursor.getInt(_cursorIndexOfLocalRiskScore);
            final long _tmpLastSeenTimestamp;
            _tmpLastSeenTimestamp = _cursor.getLong(_cursorIndexOfLastSeenTimestamp);
            final String _tmpUserFeedbackValue;
            _tmpUserFeedbackValue = _cursor.getString(_cursorIndexOfUserFeedbackValue);
            final boolean _tmpIsSafe;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsSafe);
            _tmpIsSafe = _tmp != 0;
            _item = new CallerReputation(_tmpId,_tmpPhoneNumber,_tmpSpamReportsCount,_tmpScamReportsCount,_tmpLocalRiskScore,_tmpLastSeenTimestamp,_tmpUserFeedbackValue,_tmpIsSafe);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Object getSettings(final Continuation<? super UserSettings> $completion) {
    final String _sql = "SELECT * FROM UserSettings WHERE id = 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<UserSettings>() {
      @Override
      @Nullable
      public UserSettings call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfSaveCallHistory = CursorUtil.getColumnIndexOrThrow(_cursor, "saveCallHistory");
          final int _cursorIndexOfEnableBeep = CursorUtil.getColumnIndexOrThrow(_cursor, "enableBeep");
          final int _cursorIndexOfEnableVibration = CursorUtil.getColumnIndexOrThrow(_cursor, "enableVibration");
          final int _cursorIndexOfEnableTTS = CursorUtil.getColumnIndexOrThrow(_cursor, "enableTTS");
          final int _cursorIndexOfAlertVolume = CursorUtil.getColumnIndexOrThrow(_cursor, "alertVolume");
          final UserSettings _result;
          if (_cursor.moveToFirst()) {
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final boolean _tmpSaveCallHistory;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfSaveCallHistory);
            _tmpSaveCallHistory = _tmp != 0;
            final boolean _tmpEnableBeep;
            final int _tmp_1;
            _tmp_1 = _cursor.getInt(_cursorIndexOfEnableBeep);
            _tmpEnableBeep = _tmp_1 != 0;
            final boolean _tmpEnableVibration;
            final int _tmp_2;
            _tmp_2 = _cursor.getInt(_cursorIndexOfEnableVibration);
            _tmpEnableVibration = _tmp_2 != 0;
            final boolean _tmpEnableTTS;
            final int _tmp_3;
            _tmp_3 = _cursor.getInt(_cursorIndexOfEnableTTS);
            _tmpEnableTTS = _tmp_3 != 0;
            final float _tmpAlertVolume;
            _tmpAlertVolume = _cursor.getFloat(_cursorIndexOfAlertVolume);
            _result = new UserSettings(_tmpId,_tmpSaveCallHistory,_tmpEnableBeep,_tmpEnableVibration,_tmpEnableTTS,_tmpAlertVolume);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
