package com.campprotect.scamshield.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.campprotect.scamshield.activities.SettingsActivity
import com.campprotect.scamshield.database.UserSettings
import kotlinx.coroutines.flow.StateFlow

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    activity: SettingsActivity,
    settings: StateFlow<UserSettings>,
    onSave: (UserSettings) -> Unit,
    onTestBeep: () -> Unit,
    onTestAlarm: () -> Unit
) {
    val currentSettings by settings.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings Configurations", fontWeight = FontWeight.Bold, color = Color.White) },
                navigationIcon = {
                    IconButton(onClick = { activity.finish() }) {
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
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text("System Preferences", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.Gray)

            // History Log Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Save Call Transcripts", fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                        Text("Save analysis history in the local device database.", fontSize = 12.sp, color = Color.Gray)
                    }
                    Switch(
                        checked = currentSettings.saveCallHistory,
                        onCheckedChange = { checked ->
                            onSave(currentSettings.copy(saveCallHistory = checked))
                        }
                    )
                }
            }

            // Warning Beep Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Play Warning Beeps", fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                        Text("Play beep sounds during suspicious conversations.", fontSize = 12.sp, color = Color.Gray)
                    }
                    Switch(
                        checked = currentSettings.enableBeep,
                        onCheckedChange = { checked ->
                            onSave(currentSettings.copy(enableBeep = checked))
                        }
                    )
                }
            }

            // Vibration Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Vibration Warnings", fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                        Text("Vibrate device on medium/high threat triggers.", fontSize = 12.sp, color = Color.Gray)
                    }
                    Switch(
                        checked = currentSettings.enableVibration,
                        onCheckedChange = { checked ->
                            onSave(currentSettings.copy(enableVibration = checked))
                        }
                    )
                }
            }

            // Text to Speech Voice Announcement Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("Voice Alert (Text-to-Speech)", fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                        Text("Announce verbal warning statement on high-threat levels.", fontSize = 12.sp, color = Color.Gray)
                    }
                    Switch(
                        checked = currentSettings.enableTTS,
                        onCheckedChange = { checked ->
                            onSave(currentSettings.copy(enableTTS = checked))
                        }
                    )
                }
            }

            // Volume Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Warning Volume Level", fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                    Spacer(modifier = Modifier.height(4.dp))
                    Slider(
                        value = currentSettings.alertVolume,
                        onValueChange = { volume ->
                            onSave(currentSettings.copy(alertVolume = volume))
                        },
                        valueRange = 0.0f..1.0f
                    )
                    Text(
                        text = "Level: ${(currentSettings.alertVolume * 100).toInt()}%",
                        modifier = Modifier.align(Alignment.End),
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                }
            }

            Text("Diagnostic Diagnostics", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = Color.Gray)

            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color.White)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Button(onClick = onTestBeep, modifier = Modifier.weight(1f)) {
                        Text("Test Beep")
                    }
                    Button(
                        onClick = onTestAlarm,
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFC62828)),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Test Alarm")
                    }
                }
            }
        }
    }
}
