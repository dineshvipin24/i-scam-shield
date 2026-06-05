import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:contacts_service/contacts_service.dart';
import '../services/api.dart';
import 'contacts_screen.dart';
import 'live_call_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const _platform = MethodChannel('com.example.ai_scam_shield/dialer');
  final TextEditingController _urlController = TextEditingController();
  final TextEditingController _numberController = TextEditingController(text: "+91 98765 43210");
  
  double _threshold = 70.0;
  bool _autoHangup = true;
  bool _alertSuspicious = true;
  bool _unknownOnly = true;
  bool _loading = true;
  bool _permissionsGranted = false;
  bool _isNavigating = false; // Guard to prevent duplicate navigation

  @override
  void initState() {
    super.initState();
    _loadConfig();
    _checkPermissions();
    _setupIncomingCallInterception();
  }

  Future<void> _loadConfig() async {
    final url = await ApiService.getBaseUrl();
    _urlController.text = url;
    
    final settings = await ApiService.getSettings();
    if (settings.isNotEmpty) {
      setState(() {
        _threshold = ((settings['risk_threshold'] ?? 0.71) * 100).toDouble();
        _autoHangup = settings['auto_hangup'] ?? true;
        _alertSuspicious = settings['alert_suspicious'] ?? true;
        _unknownOnly = settings['unknown_only'] ?? true;
        _loading = false;
      });
    } else {
      setState(() {
        _loading = false;
      });
    }
  }

  Future<void> _checkPermissions() async {
    final phone = await Permission.phone.isGranted;
    final contacts = await Permission.contacts.isGranted;
    final notification = await Permission.notification.isGranted;
    final mic = await Permission.microphone.isGranted;
    
    setState(() {
      _permissionsGranted = phone && contacts && notification && mic;
    });
  }

  Future<void> _requestAllPermissions() async {
    await [
      Permission.phone,
      Permission.contacts,
      Permission.notification,
      Permission.microphone,
    ].request();

    await _checkPermissions();
  }

  void _setupIncomingCallInterception() {
    _platform.setMethodCallHandler((call) async {
      if (call.method == "onIncomingCall" || call.method == "onCallAnswered") {
        final String? incomingNumber = call.arguments as String?;
        if (incomingNumber != null && incomingNumber.isNotEmpty) {
          _handleIncomingCall(incomingNumber);
        }
      }
    });

    // Check for any pending calls when app returns to foreground
    _platform.invokeMethod<String>("getIncomingCall").then((incomingNumber) {
      if (incomingNumber != null && incomingNumber.isNotEmpty) {
        _handleIncomingCall(incomingNumber);
      }
    });
  }

  Future<void> _handleIncomingCall(String rawNumber) async {
    // Guard: prevent duplicate navigation crashes
    if (_isNavigating || !mounted) return;

    if (_unknownOnly) {
      final status = await Permission.contacts.status;
      if (status.isGranted) {
        final contacts = await ContactsService.getContacts(withThumbnails: false);
        bool isSaved = false;
        final normTarget = rawNumber.replaceAll(RegExp(r'[\s\-()+]'), '');
        
        for (var c in contacts) {
          if (c.phones != null) {
            for (var p in c.phones!) {
              var val = p.value ?? "";
              val = val.replaceAll(RegExp(r'[\s\-()+]'), '');
              if (val.isNotEmpty && (normTarget.endsWith(val) || val.endsWith(normTarget))) {
                isSaved = true;
                break;
              }
            }
          }
          if (isSaved) break;
        }

        if (isSaved) {
          print("[Call Guard] Bypassed for known contact: $rawNumber");
          return;
        }
      }
    }

    if (!mounted || _isNavigating) return;
    _isNavigating = true;

    // Use addPostFrameCallback to ensure navigation runs after current build frame
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (!mounted) {
        _isNavigating = false;
        return;
      }
      await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => LiveCallScreen(callerNumber: rawNumber),
        ),
      );
      // Reset guard when user returns from LiveCallScreen
      if (mounted) {
        setState(() => _isNavigating = false);
      } else {
        _isNavigating = false;
      }
    });
  }

  Future<void> _saveConfig() async {
    setState(() => _loading = true);
    await ApiService.saveBaseUrl(_urlController.text.trim());
    
    final success = await ApiService.updateSettings({
      "risk_threshold": _threshold / 100,
      "auto_hangup": _autoHangup,
      "alert_suspicious": _alertSuspicious,
      "unknown_only": _unknownOnly,
    });
    
    setState(() => _loading = false);
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(success ? "Settings Saved Successfully!" : "Server connection error, saved locally."),
        backgroundColor: success ? Colors.greenAccent[700] : Colors.amber[800],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final darkBlue = const Color(0xFF0A0E1A);
    final cardColor = const Color(0xFF111827);
    final accentBlue = const Color(0xFF00D4FF);

    return Scaffold(
      backgroundColor: darkBlue,
      appBar: AppBar(
        backgroundColor: cardColor,
        elevation: 0,
        title: Text(
          "🛡️ AI SCAM SHIELD",
          style: GoogleFonts.inter(fontWeight: FontWeight.w900, letterSpacing: 1, fontSize: 18),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.contacts, color: Colors.white),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ContactsScreen()),
              );
            },
          )
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF00D4FF)))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(18.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                   GestureDetector(
                    onTap: _permissionsGranted ? null : _requestAllPermissions,
                    child: Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: _permissionsGranted
                              ? [const Color(0xFF1E293B), const Color(0xFF0F172A)]
                              : [const Color(0xFF3F2B1E), const Color(0xFF1F120A)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(18),
                        border: Border.all(
                          color: _permissionsGranted ? const Color(0xFF334155) : Colors.amber[800]!,
                          width: 1.5,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                _permissionsGranted ? "🛡️ SHIELD ACTIVE" : "⚠️ SHIELD INACTIVE",
                                style: GoogleFonts.inter(
                                  color: _permissionsGranted ? Colors.greenAccent[400] : Colors.amber[500],
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                              if (!_permissionsGranted)
                                Text(
                                  "Tap to Enable",
                                  style: GoogleFonts.inter(
                                    color: Colors.amber[300],
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    decoration: TextDecoration.underline,
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            _permissionsGranted
                                ? "Active Background Call Guard is protecting your incoming unknown calls."
                                : "Call Interception permissions are missing. Tap here to grant phone, contact, and notification access.",
                            style: GoogleFonts.inter(color: Colors.grey[300], fontSize: 13, height: 1.4),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Config Card
                  Text(
                    "SHIELD SETTINGS",
                    style: GoogleFonts.inter(color: Colors.grey[400], fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 1),
                  ),
                  const SizedBox(height: 8),
                  Card(
                    color: cardColor,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                      side: const BorderSide(color: Color(0xFF1E2D45)),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          TextField(
                            controller: _urlController,
                            style: GoogleFonts.inter(color: Colors.white, fontSize: 14),
                            decoration: InputDecoration(
                              labelText: "Backend URL",
                              labelStyle: GoogleFonts.inter(color: Colors.grey[400]),
                              enabledBorder: const UnderlineInputBorder(borderSide: BorderSide(color: Color(0xFF334155))),
                              focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: accentBlue)),
                            ),
                          ),
                          const SizedBox(height: 18),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text("Risk Threshold", style: GoogleFonts.inter(color: Colors.white)),
                                  Text("${_threshold.round()}%", style: GoogleFonts.inter(color: accentBlue, fontWeight: FontWeight.bold)),
                                ],
                              ),
                              Slider(
                                value: _threshold,
                                min: 20,
                                max: 90,
                                activeColor: accentBlue,
                                inactiveColor: Colors.grey[800],
                                onChanged: (val) {
                                  setState(() => _threshold = val);
                                },
                              ),
                            ],
                          ),
                          SwitchListTile(
                            title: Text("Auto-Hangup Fraud", style: GoogleFonts.inter(color: Colors.white, fontSize: 14)),
                            subtitle: Text("Block automatically on high risk", style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 11)),
                            value: _autoHangup,
                            activeColor: accentBlue,
                            contentPadding: EdgeInsets.zero,
                            onChanged: (val) => setState(() => _autoHangup = val),
                          ),
                          SwitchListTile(
                            title: Text("Alert Suspicious", style: GoogleFonts.inter(color: Colors.white, fontSize: 14)),
                            subtitle: Text("Push warning for low scam levels", style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 11)),
                            value: _alertSuspicious,
                            activeColor: accentBlue,
                            contentPadding: EdgeInsets.zero,
                            onChanged: (val) => setState(() => _alertSuspicious = val),
                          ),
                          SwitchListTile(
                            title: Text("Protect Unknown Calls Only", style: GoogleFonts.inter(color: Colors.white, fontSize: 14)),
                            subtitle: Text("Bypass checks for saved contacts", style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 11)),
                            value: _unknownOnly,
                            activeColor: accentBlue,
                            contentPadding: EdgeInsets.zero,
                            onChanged: (val) => setState(() => _unknownOnly = val),
                          ),
                          const SizedBox(height: 12),
                          ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: accentBlue,
                              minimumSize: const Size(double.infinity, 44),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                            ),
                            onPressed: _saveConfig,
                            child: Text(
                              "Save Settings",
                              style: GoogleFonts.inter(color: Colors.black, fontWeight: FontWeight.bold),
                            ),
                          )
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Simulation Card
                  Text(
                    "TEST SIMULATOR",
                    style: GoogleFonts.inter(color: Colors.grey[400], fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 1),
                  ),
                  const SizedBox(height: 8),
                  Card(
                    color: cardColor,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                      side: const BorderSide(color: Color(0xFF1E2D45)),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Simulate Incoming WebRTC Call",
                            style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            "Starts a local audio connection using WebRTC client loop to test features.",
                            style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 11),
                          ),
                          const SizedBox(height: 14),
                          TextField(
                            controller: _numberController,
                            style: GoogleFonts.inter(color: Colors.white, fontSize: 14),
                            decoration: InputDecoration(
                              labelText: "Incoming Number",
                              labelStyle: GoogleFonts.inter(color: Colors.grey[400]),
                              enabledBorder: const UnderlineInputBorder(borderSide: BorderSide(color: Color(0xFF334155))),
                              focusedBorder: UnderlineInputBorder(borderSide: BorderSide(color: accentBlue)),
                            ),
                          ),
                          const SizedBox(height: 18),
                          ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF00E676),
                              minimumSize: const Size(double.infinity, 48),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            onPressed: () async {
                              final rawNumber = _numberController.text.trim();
                              if (_unknownOnly) {
                                final status = await Permission.contacts.status;
                                if (status.isGranted) {
                                  final contacts = await ContactsService.getContacts(withThumbnails: false);
                                  bool isSaved = false;
                                  String matchedName = "";
                                  
                                  // Normalize target number
                                  final normTarget = rawNumber.replaceAll(RegExp(r'[\s\-()+]'), '');
                                  
                                  for (var c in contacts) {
                                    if (c.phones != null) {
                                      for (var p in c.phones!) {
                                        var val = p.value ?? "";
                                        val = val.replaceAll(RegExp(r'[\s\-()+]'), '');
                                        if (val.isNotEmpty && (normTarget.endsWith(val) || val.endsWith(normTarget))) {
                                          isSaved = true;
                                          matchedName = c.displayName ?? "Unknown";
                                          break;
                                        }
                                      }
                                    }
                                    if (isSaved) break;
                                  }
                                  
                                  if (isSaved) {
                                    showDialog(
                                      context: context,
                                      builder: (context) => AlertDialog(
                                        backgroundColor: const Color(0xFF111827),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                                        title: Text("Bypass Shield", style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.bold)),
                                        content: Text("The caller '$matchedName' ($rawNumber) is in your saved contacts.\n\nShield is bypassed for contacts.", style: GoogleFonts.inter(color: Colors.grey[300])),
                                        actions: [
                                          TextButton(
                                            onPressed: () => Navigator.pop(context),
                                            child: Text("OK", style: GoogleFonts.inter(color: const Color(0xFF00D4FF))),
                                          )
                                        ],
                                      ),
                                    );
                                    return;
                                  }
                                }
                              }

                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => LiveCallScreen(
                                    callerNumber: rawNumber,
                                  ),
                                ),
                              );
                            },
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(Icons.call, color: Colors.black),
                                const SizedBox(width: 8),
                                Text(
                                  "Start Call (WebRTC)",
                                  style: GoogleFonts.inter(color: Colors.black, fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                          )
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
