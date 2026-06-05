package com.example.ai_scam_shield

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.role.RoleManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioManager
import android.media.ToneGenerator
import android.os.Build
import android.telecom.TelecomManager
import android.util.Log
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.example.ai_scam_shield/dialer"
    private var toneGenerator: ToneGenerator? = null

    companion object {
        private var methodChannel: MethodChannel? = null
        private var pendingIncomingNumber: String? = null

        fun onIncomingCallReceived(number: String) {
            pendingIncomingNumber = number
            methodChannel?.invokeMethod("onIncomingCall", number)
        }

        fun onCallAnswered(number: String) {
            // Notify Flutter that call has been answered — start WebRTC screening
            methodChannel?.invokeMethod("onCallAnswered", number)
        }
    }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        methodChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
        methodChannel?.setMethodCallHandler { call, result ->
            when (call.method) {
                "isDefaultDialer" -> result.success(isDefaultDialer())
                "setDefaultDialer" -> {
                    setDefaultDialer()
                    result.success(true)
                }
                "getIncomingCall" -> {
                    val num = pendingIncomingNumber
                    pendingIncomingNumber = null
                    result.success(num)
                }
                "playBeep" -> {
                    playBeep()
                    result.success(true)
                }
                "showNotification" -> {
                    val title = call.argument<String>("title") ?: "Alert"
                    val message = call.argument<String>("message") ?: ""
                    showLocalNotification(title, message)
                    result.success(true)
                }
                "requestMicPermission" -> {
                    requestMicrophonePermission()
                    result.success(true)
                }
                "hasMicPermission" -> {
                    val granted = ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED
                    result.success(granted)
                }
                else -> result.notImplemented()
            }
        }

        // Request microphone permission on startup if not granted
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 200)
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        val incomingNumber = intent.getStringExtra("incoming_number")
        if (!incomingNumber.isNullOrEmpty()) {
            onIncomingCallReceived(incomingNumber)
        }
    }

    private fun requestMicrophonePermission() {
        ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 200)
    }

    private fun playBeep() {
        try {
            if (toneGenerator == null) {
                toneGenerator = ToneGenerator(AudioManager.STREAM_NOTIFICATION, 100)
            }
            // Play 3 rapid warning beeps
            toneGenerator?.startTone(ToneGenerator.TONE_CDMA_ALERT_CALL_GUARD, 500)
        } catch (e: Exception) {
            Log.e("MainActivity", "Error playing tone", e)
        }
    }

    private fun showLocalNotification(title: String, message: String) {
        val channelId = "scam_shield_alerts"
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(channelId, "Scam Shield Alerts", NotificationManager.IMPORTANCE_HIGH).apply {
                description = "Critical fraud alerts from AI Scam Shield"
                enableVibration(true)
            }
            notificationManager.createNotificationChannel(channel)
        }
        val notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle(title)
            .setContentText(message)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(true)
            .setVibrate(longArrayOf(0, 500, 200, 500))
            .build()
        notificationManager.notify(System.currentTimeMillis().toInt(), notification)
    }

    private fun isDefaultDialer(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = getSystemService(Context.ROLE_SERVICE) as RoleManager
            roleManager.isRoleHeld(RoleManager.ROLE_DIALER)
        } else {
            val telecomManager = getSystemService(Context.TELECOM_SERVICE) as TelecomManager
            packageName == telecomManager.defaultDialerPackage
        }
    }

    private fun setDefaultDialer() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = getSystemService(Context.ROLE_SERVICE) as RoleManager
            if (!roleManager.isRoleHeld(RoleManager.ROLE_DIALER)) {
                val intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_DIALER)
                startActivityForResult(intent, 123)
            }
        } else {
            val intent = Intent(TelecomManager.ACTION_CHANGE_DEFAULT_DIALER)
            intent.putExtra(TelecomManager.EXTRA_CHANGE_DEFAULT_DIALER_PACKAGE_NAME, packageName)
            startActivity(intent)
        }
    }
}
