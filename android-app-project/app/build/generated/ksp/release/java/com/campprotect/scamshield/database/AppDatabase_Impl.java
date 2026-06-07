package com.campprotect.scamshield.database;

import androidx.annotation.NonNull;
import androidx.room.DatabaseConfiguration;
import androidx.room.InvalidationTracker;
import androidx.room.RoomDatabase;
import androidx.room.RoomOpenHelper;
import androidx.room.migration.AutoMigrationSpec;
import androidx.room.migration.Migration;
import androidx.room.util.DBUtil;
import androidx.room.util.TableInfo;
import androidx.sqlite.db.SupportSQLiteDatabase;
import androidx.sqlite.db.SupportSQLiteOpenHelper;
import java.lang.Class;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.Generated;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class AppDatabase_Impl extends AppDatabase {
  private volatile CallHistoryDao _callHistoryDao;

  @Override
  @NonNull
  protected SupportSQLiteOpenHelper createOpenHelper(@NonNull final DatabaseConfiguration config) {
    final SupportSQLiteOpenHelper.Callback _openCallback = new RoomOpenHelper(config, new RoomOpenHelper.Delegate(1) {
      @Override
      public void createAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("CREATE TABLE IF NOT EXISTS `CallHistory` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `phoneNumber` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `transcript` TEXT NOT NULL, `riskScore` INTEGER NOT NULL, `riskLevel` TEXT NOT NULL, `classification` TEXT NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `FraudAlertLog` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `phoneNumber` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `riskScore` INTEGER NOT NULL, `triggerKeyword` TEXT NOT NULL, `alertType` TEXT NOT NULL, `transcriptSnippet` TEXT NOT NULL, `category` TEXT NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `CallerReputation` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `phoneNumber` TEXT NOT NULL, `spamReportsCount` INTEGER NOT NULL, `scamReportsCount` INTEGER NOT NULL, `localRiskScore` INTEGER NOT NULL, `lastSeenTimestamp` INTEGER NOT NULL, `userFeedbackValue` TEXT NOT NULL, `isSafe` INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `UserSettings` (`id` INTEGER NOT NULL, `saveCallHistory` INTEGER NOT NULL, `enableBeep` INTEGER NOT NULL, `enableVibration` INTEGER NOT NULL, `enableTTS` INTEGER NOT NULL, `alertVolume` REAL NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)");
        db.execSQL("INSERT OR REPLACE INTO room_master_table (id,identity_hash) VALUES(42, 'bbd04f7a88c215dfeca1eadc9415e9da')");
      }

      @Override
      public void dropAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("DROP TABLE IF EXISTS `CallHistory`");
        db.execSQL("DROP TABLE IF EXISTS `FraudAlertLog`");
        db.execSQL("DROP TABLE IF EXISTS `CallerReputation`");
        db.execSQL("DROP TABLE IF EXISTS `UserSettings`");
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onDestructiveMigration(db);
          }
        }
      }

      @Override
      public void onCreate(@NonNull final SupportSQLiteDatabase db) {
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onCreate(db);
          }
        }
      }

      @Override
      public void onOpen(@NonNull final SupportSQLiteDatabase db) {
        mDatabase = db;
        internalInitInvalidationTracker(db);
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onOpen(db);
          }
        }
      }

      @Override
      public void onPreMigrate(@NonNull final SupportSQLiteDatabase db) {
        DBUtil.dropFtsSyncTriggers(db);
      }

      @Override
      public void onPostMigrate(@NonNull final SupportSQLiteDatabase db) {
      }

      @Override
      @NonNull
      public RoomOpenHelper.ValidationResult onValidateSchema(
          @NonNull final SupportSQLiteDatabase db) {
        final HashMap<String, TableInfo.Column> _columnsCallHistory = new HashMap<String, TableInfo.Column>(7);
        _columnsCallHistory.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallHistory.put("phoneNumber", new TableInfo.Column("phoneNumber", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallHistory.put("timestamp", new TableInfo.Column("timestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallHistory.put("transcript", new TableInfo.Column("transcript", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallHistory.put("riskScore", new TableInfo.Column("riskScore", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallHistory.put("riskLevel", new TableInfo.Column("riskLevel", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallHistory.put("classification", new TableInfo.Column("classification", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysCallHistory = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesCallHistory = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoCallHistory = new TableInfo("CallHistory", _columnsCallHistory, _foreignKeysCallHistory, _indicesCallHistory);
        final TableInfo _existingCallHistory = TableInfo.read(db, "CallHistory");
        if (!_infoCallHistory.equals(_existingCallHistory)) {
          return new RoomOpenHelper.ValidationResult(false, "CallHistory(com.campprotect.scamshield.database.CallHistory).\n"
                  + " Expected:\n" + _infoCallHistory + "\n"
                  + " Found:\n" + _existingCallHistory);
        }
        final HashMap<String, TableInfo.Column> _columnsFraudAlertLog = new HashMap<String, TableInfo.Column>(8);
        _columnsFraudAlertLog.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsFraudAlertLog.put("phoneNumber", new TableInfo.Column("phoneNumber", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsFraudAlertLog.put("timestamp", new TableInfo.Column("timestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsFraudAlertLog.put("riskScore", new TableInfo.Column("riskScore", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsFraudAlertLog.put("triggerKeyword", new TableInfo.Column("triggerKeyword", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsFraudAlertLog.put("alertType", new TableInfo.Column("alertType", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsFraudAlertLog.put("transcriptSnippet", new TableInfo.Column("transcriptSnippet", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsFraudAlertLog.put("category", new TableInfo.Column("category", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysFraudAlertLog = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesFraudAlertLog = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoFraudAlertLog = new TableInfo("FraudAlertLog", _columnsFraudAlertLog, _foreignKeysFraudAlertLog, _indicesFraudAlertLog);
        final TableInfo _existingFraudAlertLog = TableInfo.read(db, "FraudAlertLog");
        if (!_infoFraudAlertLog.equals(_existingFraudAlertLog)) {
          return new RoomOpenHelper.ValidationResult(false, "FraudAlertLog(com.campprotect.scamshield.database.FraudAlertLog).\n"
                  + " Expected:\n" + _infoFraudAlertLog + "\n"
                  + " Found:\n" + _existingFraudAlertLog);
        }
        final HashMap<String, TableInfo.Column> _columnsCallerReputation = new HashMap<String, TableInfo.Column>(8);
        _columnsCallerReputation.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallerReputation.put("phoneNumber", new TableInfo.Column("phoneNumber", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallerReputation.put("spamReportsCount", new TableInfo.Column("spamReportsCount", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallerReputation.put("scamReportsCount", new TableInfo.Column("scamReportsCount", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallerReputation.put("localRiskScore", new TableInfo.Column("localRiskScore", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallerReputation.put("lastSeenTimestamp", new TableInfo.Column("lastSeenTimestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallerReputation.put("userFeedbackValue", new TableInfo.Column("userFeedbackValue", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsCallerReputation.put("isSafe", new TableInfo.Column("isSafe", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysCallerReputation = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesCallerReputation = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoCallerReputation = new TableInfo("CallerReputation", _columnsCallerReputation, _foreignKeysCallerReputation, _indicesCallerReputation);
        final TableInfo _existingCallerReputation = TableInfo.read(db, "CallerReputation");
        if (!_infoCallerReputation.equals(_existingCallerReputation)) {
          return new RoomOpenHelper.ValidationResult(false, "CallerReputation(com.campprotect.scamshield.database.CallerReputation).\n"
                  + " Expected:\n" + _infoCallerReputation + "\n"
                  + " Found:\n" + _existingCallerReputation);
        }
        final HashMap<String, TableInfo.Column> _columnsUserSettings = new HashMap<String, TableInfo.Column>(6);
        _columnsUserSettings.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserSettings.put("saveCallHistory", new TableInfo.Column("saveCallHistory", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserSettings.put("enableBeep", new TableInfo.Column("enableBeep", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserSettings.put("enableVibration", new TableInfo.Column("enableVibration", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserSettings.put("enableTTS", new TableInfo.Column("enableTTS", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserSettings.put("alertVolume", new TableInfo.Column("alertVolume", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysUserSettings = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesUserSettings = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoUserSettings = new TableInfo("UserSettings", _columnsUserSettings, _foreignKeysUserSettings, _indicesUserSettings);
        final TableInfo _existingUserSettings = TableInfo.read(db, "UserSettings");
        if (!_infoUserSettings.equals(_existingUserSettings)) {
          return new RoomOpenHelper.ValidationResult(false, "UserSettings(com.campprotect.scamshield.database.UserSettings).\n"
                  + " Expected:\n" + _infoUserSettings + "\n"
                  + " Found:\n" + _existingUserSettings);
        }
        return new RoomOpenHelper.ValidationResult(true, null);
      }
    }, "bbd04f7a88c215dfeca1eadc9415e9da", "d3dfc08b94d2b8130b9f7bcb9ec584b3");
    final SupportSQLiteOpenHelper.Configuration _sqliteConfig = SupportSQLiteOpenHelper.Configuration.builder(config.context).name(config.name).callback(_openCallback).build();
    final SupportSQLiteOpenHelper _helper = config.sqliteOpenHelperFactory.create(_sqliteConfig);
    return _helper;
  }

  @Override
  @NonNull
  protected InvalidationTracker createInvalidationTracker() {
    final HashMap<String, String> _shadowTablesMap = new HashMap<String, String>(0);
    final HashMap<String, Set<String>> _viewTables = new HashMap<String, Set<String>>(0);
    return new InvalidationTracker(this, _shadowTablesMap, _viewTables, "CallHistory","FraudAlertLog","CallerReputation","UserSettings");
  }

  @Override
  public void clearAllTables() {
    super.assertNotMainThread();
    final SupportSQLiteDatabase _db = super.getOpenHelper().getWritableDatabase();
    try {
      super.beginTransaction();
      _db.execSQL("DELETE FROM `CallHistory`");
      _db.execSQL("DELETE FROM `FraudAlertLog`");
      _db.execSQL("DELETE FROM `CallerReputation`");
      _db.execSQL("DELETE FROM `UserSettings`");
      super.setTransactionSuccessful();
    } finally {
      super.endTransaction();
      _db.query("PRAGMA wal_checkpoint(FULL)").close();
      if (!_db.inTransaction()) {
        _db.execSQL("VACUUM");
      }
    }
  }

  @Override
  @NonNull
  protected Map<Class<?>, List<Class<?>>> getRequiredTypeConverters() {
    final HashMap<Class<?>, List<Class<?>>> _typeConvertersMap = new HashMap<Class<?>, List<Class<?>>>();
    _typeConvertersMap.put(CallHistoryDao.class, CallHistoryDao_Impl.getRequiredConverters());
    return _typeConvertersMap;
  }

  @Override
  @NonNull
  public Set<Class<? extends AutoMigrationSpec>> getRequiredAutoMigrationSpecs() {
    final HashSet<Class<? extends AutoMigrationSpec>> _autoMigrationSpecsSet = new HashSet<Class<? extends AutoMigrationSpec>>();
    return _autoMigrationSpecsSet;
  }

  @Override
  @NonNull
  public List<Migration> getAutoMigrations(
      @NonNull final Map<Class<? extends AutoMigrationSpec>, AutoMigrationSpec> autoMigrationSpecs) {
    final List<Migration> _autoMigrations = new ArrayList<Migration>();
    return _autoMigrations;
  }

  @Override
  public CallHistoryDao callHistoryDao() {
    if (_callHistoryDao != null) {
      return _callHistoryDao;
    } else {
      synchronized(this) {
        if(_callHistoryDao == null) {
          _callHistoryDao = new CallHistoryDao_Impl(this);
        }
        return _callHistoryDao;
      }
    }
  }
}
