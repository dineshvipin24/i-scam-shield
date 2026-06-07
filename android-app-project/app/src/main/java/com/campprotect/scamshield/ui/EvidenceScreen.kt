package com.campprotect.scamshield.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.campprotect.scamshield.database.FraudAlertLog

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EvidenceScreen(
    alert: FraudAlertLog,
    onBack: () -> Unit
) {
    val alertColor = if (alert.alertType == "HIGH") Color(0xFFC62828) else Color(0xFFEF6C00)

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Scam Analysis Details", fontWeight = FontWeight.Bold, color = Color.White) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back", tint = Color.White)
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
                .padding(16.dp)
                .background(Color(0xFFF5F5F5)),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Column(
                    modifier = Modifier.padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = null,
                        tint = alertColor,
                        modifier = Modifier.size(56.dp)
                    )

                    Spacer(modifier = Modifier.height(12.dp))

                    Text(
                        text = "Scam Probability: ${alert.riskScore}%",
                        fontSize = 22.sp,
                        fontWeight = FontWeight.Bold,
                        color = alertColor
                    )

                    Spacer(modifier = Modifier.height(4.dp))

                    Text(
                        text = "Classification: ${alert.category}",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.SemiBold,
                        color = Color.Gray
                    )
                }
            }

            Text("Threat Evidence Logs", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = Color.DarkGray)

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Caller Phone Number:", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text(alert.phoneNumber, fontSize = 16.sp, color = Color.DarkGray)
                    
                    Spacer(modifier = Modifier.height(12.dp))

                    Text("Trigger Keyword Match:", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text(alert.triggerKeyword.toUpperCase(), fontSize = 16.sp, color = alertColor, fontWeight = FontWeight.SemiBold)

                    Spacer(modifier = Modifier.height(12.dp))

                    Text("Severity Rating:", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text(alert.alertType, fontSize = 16.sp, color = alertColor, fontWeight = FontWeight.SemiBold)
                }
            }

            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Transcription Snippet Context:", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "\"${alert.transcriptSnippet}\"",
                        fontSize = 15.sp,
                        fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                        color = Color.DarkGray,
                        lineHeight = 20.sp
                    )
                }
            }
        }
    }
}
