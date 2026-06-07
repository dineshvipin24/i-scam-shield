package com.campprotect.scamshield.ui

import android.content.Intent
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.campprotect.scamshield.activities.MainActivity
import com.campprotect.scamshield.activities.SettingsActivity
import com.campprotect.scamshield.database.CallHistory
import com.campprotect.scamshield.database.CallerReputation
import com.campprotect.scamshield.database.FraudAlertLog
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    activity: MainActivity,
    isMonitoring: StateFlow<Boolean>,
    activeNumber: StateFlow<String>,
    liveScore: StateFlow<Int>,
    liveCategory: StateFlow<String>,
    livePhrase: StateFlow<String>,
    callHistory: StateFlow<List<CallHistory>>,
    alertLogs: StateFlow<List<FraudAlertLog>>,
    reputationLogs: StateFlow<List<CallerReputation>>
) {
    val monitoring by isMonitoring.collectAsState()
    val activePhone by activeNumber.collectAsState()
    val score by liveScore.collectAsState()
    val category by liveCategory.collectAsState()
    val phrase by livePhrase.collectAsState()
    
    val calls by callHistory.collectAsState()
    val alerts by alertLogs.collectAsState()
    val reputations by reputationLogs.collectAsState()

    var selectedTab by remember { mutableStateOf(0) }
    var selectedAlertForEvidence by remember { mutableStateOf<FraudAlertLog?>(null) }

    // If an alert is tapped for details, render the EvidenceScreen overlay
    selectedAlertForEvidence?.let { alert ->
        EvidenceScreen(alert = alert, onBack = { selectedAlertForEvidence = null })
        return
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Camp Protect (AI Scam Shield)", fontWeight = FontWeight.Bold, color = Color.White) },
                actions = {
                    IconButton(onClick = {
                        activity.startActivity(Intent(activity, SettingsActivity::class.java))
                    }) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings", tint = Color.White)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.primary)
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(Color(0xFFF5F5F5))
        ) {
            // Live Status Card
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (monitoring) Color(0xFFFFEBEE) else Color.White
                ),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = if (monitoring) "🟢 SHIELD MONITORING ACTIVE" else "⚫ SHIELD ARMED & PROTECTED",
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp,
                        color = if (monitoring) Color(0xFFC62828) else Color.Gray
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))

                    if (monitoring) {
                        Text(
                            text = "Active Target: $activePhone",
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 18.sp
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Threat Index: $score% | Class: $category",
                            fontWeight = FontWeight.Bold,
                            color = if (score >= 61) Color(0xFFC62828) else Color(0xFFEF6C00)
                        )
                        if (phrase.isNotEmpty()) {
                            Text(
                                text = "Latest: \"$phrase\"",
                                fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                                textAlign = TextAlign.Center,
                                modifier = Modifier.padding(horizontal = 8.dp)
                            )
                        }
                    } else {
                        Text(
                            text = "Monitoring starts automatically when unknown calls connect. Speak keywords during testing.",
                            textAlign = TextAlign.Center,
                            fontSize = 13.sp,
                            color = Color.Gray
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        if (!monitoring) {
                            Button(
                                onClick = { activity.startTestMonitoring("+919876543210") },
                                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.primary)
                            ) {
                                Icon(Icons.Default.PlayArrow, contentDescription = null)
                                Spacer(modifier = Modifier.width(4.dp))
                                Text("Test Call Trigger")
                            }
                        } else {
                            Button(
                                onClick = { activity.stopTestMonitoring() },
                                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFC62828))
                            ) {
                                Text("Stop Call")
                            }
                        }
                    }
                }
            }

            // Navigation Tabs
            TabRow(selectedTabIndex = selectedTab) {
                Tab(selected = selectedTab == 0, onClick = { selectedTab = 0 }) {
                    Text("History", modifier = Modifier.padding(12.dp), fontWeight = FontWeight.Bold)
                }
                Tab(selected = selectedTab == 1, onClick = { selectedTab = 1 }) {
                    Text("Alerts", modifier = Modifier.padding(12.dp), fontWeight = FontWeight.Bold)
                }
                Tab(selected = selectedTab == 2, onClick = { selectedTab = 2 }) {
                    Text("Reputation", modifier = Modifier.padding(12.dp), fontWeight = FontWeight.Bold)
                }
            }

            // Tabs Content
            Box(modifier = Modifier.weight(1f)) {
                when (selectedTab) {
                    0 -> {
                        if (calls.isEmpty()) {
                            EmptyStateMessage("No calls analyzed yet.")
                        } else {
                            LazyColumn(modifier = Modifier.fillMaxSize().padding(8.dp)) {
                                items(calls) { call ->
                                    CallHistoryCard(call)
                                }
                            }
                        }
                    }
                    1 -> {
                        if (alerts.isEmpty()) {
                            EmptyStateMessage("No scam alert logs recorded.")
                        } else {
                            LazyColumn(modifier = Modifier.fillMaxSize().padding(8.dp)) {
                                items(alerts) { alert ->
                                    Card(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(vertical = 4.dp)
                                            .clickable { selectedAlertForEvidence = alert },
                                        colors = CardDefaults.cardColors(containerColor = Color.White)
                                    ) {
                                        FraudAlertRowContent(alert)
                                    }
                                }
                            }
                        }
                    }
                    2 -> {
                        if (reputations.isEmpty()) {
                            EmptyStateMessage("No cached reputation data.")
                        } else {
                            LazyColumn(modifier = Modifier.fillMaxSize().padding(8.dp)) {
                                items(reputations) { rep ->
                                    ReputationCard(rep, onUpdate = { activity.refreshData() }, activity = activity)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun FraudAlertRowContent(alert: FraudAlertLog) {
    val alertColor = if (alert.alertType == "HIGH") Color(0xFFC62828) else Color(0xFFEF6C00)

    Row(
        modifier = Modifier.fillMaxWidth().padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            Icons.Default.Warning,
            contentDescription = null,
            tint = alertColor,
            modifier = Modifier.size(36.dp)
        )
        Spacer(modifier = Modifier.width(16.dp))
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "${alert.alertType} Scam Alert",
                    color = alertColor,
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
                Text(
                    text = "View Evidence",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.SemiBold
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text("Category: ${alert.category}", fontWeight = FontWeight.Medium, fontSize = 13.sp)
            Text("Phrase: \"${alert.transcriptSnippet}\"", fontSize = 13.sp, color = Color.Gray)
        }
    }
}

@Composable
fun ReputationCard(
    rep: CallerReputation,
    onUpdate: () -> Unit,
    activity: MainActivity
) {
    Card(
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(rep.phoneNumber, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                Text(
                    text = "Spam Index: ${rep.localRiskScore}%",
                    color = if (rep.localRiskScore >= 50) Color(0xFFC62828) else Color(0xFF2E7D32),
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text("Spam Reports: ${rep.spamReportsCount} | Scam Reports: ${rep.scamReportsCount}", fontSize = 12.sp, color = Color.Gray)
            
            Spacer(modifier = Modifier.height(12.dp))
            Divider()
            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                OutlinedButton(
                    onClick = {
                        // Mark as Safe
                        CoroutineScope(Dispatchers.IO).launch {
                            activity.repository.insertOrUpdateReputation(
                                rep.copy(userFeedbackValue = "SAFE", localRiskScore = 0, isSafe = true)
                            )
                            onUpdate()
                        }
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Trust Safe")
                }

                Button(
                    onClick = {
                        // Mark as Spammer
                        CoroutineScope(Dispatchers.IO).launch {
                            activity.repository.insertOrUpdateReputation(
                                rep.copy(
                                    userFeedbackValue = "SCAM",
                                    spamReportsCount = rep.spamReportsCount + 1,
                                    localRiskScore = Math.min(rep.localRiskScore + 30, 100)
                                )
                            )
                            onUpdate()
                        }
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFC62828)),
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Report Scam")
                }
            }
        }
    }
}

@Composable
fun EmptyStateMessage(message: String) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = message,
            color = Color.Gray,
            textAlign = TextAlign.Center,
            fontSize = 15.sp,
            fontWeight = FontWeight.Medium
        )
    }
}

@Composable
fun CallHistoryCard(call: CallHistory) {
    val date = remember(call.timestamp) {
        val sdf = SimpleDateFormat("dd MMM yyyy, HH:mm", Locale.getDefault())
        sdf.format(Date(call.timestamp))
    }
    
    val riskColor = when (call.riskLevel) {
        "HIGH" -> Color(0xFFC62828)
        "MEDIUM" -> Color(0xFFEF6C00)
        else -> Color(0xFF2E7D32)
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = call.phoneNumber,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Text(
                    text = "${call.riskScore}% (${call.riskLevel})",
                    color = riskColor,
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Category: ${call.classification}",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium,
                    color = Color.DarkGray
                )
                Text(
                    text = date,
                    fontSize = 12.sp,
                    color = Color.Gray
                )
            }
            if (call.transcript.isNotEmpty()) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "\"${call.transcript}\"",
                    fontSize = 13.sp,
                    fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                    color = Color.Gray,
                    maxLines = 2
                )
            }
        }
    }
}

