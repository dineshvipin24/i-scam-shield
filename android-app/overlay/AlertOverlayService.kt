package com.campprotect.scamshield.overlay

import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.graphics.PixelFormat
import android.os.Build
import android.os.IBinder
import android.view.Gravity
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class AlertOverlayService : Service() {

    private var windowManager: WindowManager? = null
    private var overlayView: View? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val phoneNumber = intent?.getStringExtra("EXTRA_PHONE_NUMBER") ?: "Unknown"
        val riskScore = intent?.getIntExtra("EXTRA_RISK_SCORE", 0) ?: 0
        val keywords = intent?.getStringArrayListExtra("EXTRA_KEYWORDS") ?: arrayListOf()
        val category = intent?.getStringExtra("EXTRA_CATEGORY") ?: "Suspicious Behavior"

        showOverlay(phoneNumber, riskScore, keywords, category)

        return START_NOT_STICKY
    }

    private fun showOverlay(phoneNumber: String, score: Int, keywords: List<String>, category: String) {
        if (overlayView != null) {
            updateOverlayText(score, keywords, category)
            return
        }

        val layoutType = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        } else {
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE
        }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            layoutType,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or
                    WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                    WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON or
                    WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
            x = 0
            y = 120
        }

        overlayView = createOverlayView(phoneNumber, score, keywords, category)
        windowManager?.addView(overlayView, params)
    }

    private fun createOverlayView(phoneNumber: String, score: Int, keywords: List<String>, category: String): View {
        val context = this
        val rootLayout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#C62828")) // Material Red (Dark)
            setPadding(44, 44, 44, 44)
            elevation = 24f
        }

        // Title
        val titleView = TextView(context).apply {
            text = "🚨 CRITICAL SCAM DETECTED"
            textSize = 20f
            setTextColor(Color.WHITE)
            setTypeface(null, android.graphics.Typeface.BOLD)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 10)
        }
        rootLayout.addView(titleView)

        // Metadata: Category & Risk Score
        val subtitleView = TextView(context).apply {
            text = "Type: $category | Scam Probability: $score%"
            textSize = 15f
            setTextColor(Color.WHITE)
            setTypeface(null, android.graphics.Typeface.BOLD)
            gravity = Gravity.CENTER
            setPadding(0, 0, 0, 16)
        }
        rootLayout.addView(subtitleView)

        // Warnings body
        val bodyView = TextView(context).apply {
            text = """
                This caller matches scam behavior profiles.
                
                Do NOT disclose:
                • OTPs or login codes
                • Aadhaar/PAN Identity numbers
                • CVV or credit card information
                • UPI PIN credentials
                • Bank password/Verification steps
            """.trimIndent()
            textSize = 14f
            setTextColor(Color.WHITE)
            setPadding(16, 0, 16, 20)
        }
        rootLayout.addView(bodyView)

        // Keywords detected evidence
        val evidenceView = TextView(context).apply {
            text = "Threat Keywords: " + keywords.joinToString(", ").ifEmpty { "Scam pattern conversation" }
            textSize = 13f
            setTextColor(Color.YELLOW)
            setTypeface(null, android.graphics.Typeface.BOLD)
            setPadding(16, 0, 16, 24)
        }
        rootLayout.addView(evidenceView)

        // Dismiss
        val dismissBtn = Button(context).apply {
            text = "DISMISS WARNING"
            setBackgroundColor(Color.WHITE)
            setTextColor(Color.parseColor("#C62828"))
            setTypeface(null, android.graphics.Typeface.BOLD)
            setOnClickListener {
                stopSelf()
            }
        }
        rootLayout.addView(dismissBtn)

        return rootLayout
    }

    private fun updateOverlayText(score: Int, keywords: List<String>, category: String) {
        overlayView?.let { view ->
            val root = view as LinearLayout
            (root.getChildAt(1) as? TextView)?.text = "Type: $category | Scam Probability: $score%"
            if (root.childCount >= 4) {
                (root.getChildAt(3) as? TextView)?.text = "Threat Keywords: " + keywords.joinToString(", ")
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        overlayView?.let {
            windowManager?.removeView(it)
            overlayView = null
        }
    }
}
