package com.campprotect.scamshield.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun PrivacyDashboardScreen(
    onAccept: () -> Unit,
    onDecline: () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Color(0xFF121212) // Sleek Premium Dark Mode
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                Icons.Default.Info,
                contentDescription = null,
                tint = Color(0xFF64B5F6),
                modifier = Modifier.size(72.dp)
            )

            Spacer(modifier = Modifier.height(24.dp))

            Text(
                text = "Privacy & Call Security Consent",
                fontWeight = FontWeight.Bold,
                fontSize = 24.sp,
                color = Color.White,
                textAlign = TextAlign.Center
            )

            Spacer(modifier = Modifier.height(16.dp))

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1E1E))
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "Camp Protect acts as a real-time scam warning assistant. To protect you, the app analyzes microphone audio to detect scam conversation patterns (such as requests for OTPs, bank credentials, or remote access apps).",
                        fontSize = 14.sp,
                        color = Color(0xFFE0E0E0),
                        lineHeight = 20.sp
                    )

                    Divider(color = Color.DarkGray)

                    Text(
                        text = "🛡️ What We Do:",
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp,
                        color = Color(0xFF64B5F6)
                    )
                    Text(
                        text = "• We analyze speech spoken near the device's microphone in real-time.\n• We run all speech-to-text conversion and scam scoring strictly on your physical device.\n• We recommend enabling Speakerphone during unknown calls to enable optimal detection of the caller's voice.",
                        fontSize = 13.sp,
                        color = Color(0xFFB0BEC5),
                        lineHeight = 18.sp
                    )

                    Text(
                        text = "❌ What We NEVER Do:",
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp,
                        color = Color(0xFFE57373)
                    )
                    Text(
                        text = "• We do not tap into private telephone networks or record cellular lines.\n• We do not store, save, or record audio files.\n• We do not upload audio data or call transcripts to any cloud servers.",
                        fontSize = 13.sp,
                        color = Color(0xFFB0BEC5),
                        lineHeight = 18.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(32.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                OutlinedButton(
                    onClick = onDecline,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFFE57373))
                ) {
                    Text("Decline", fontWeight = FontWeight.Bold)
                }

                Button(
                    onClick = onAccept,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF64B5F6))
                ) {
                    Text("Accept", fontWeight = FontWeight.Bold, color = Color(0xFF121212))
                }
            }
        }
    }
}
