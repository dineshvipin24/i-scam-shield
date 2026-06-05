import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/signaling.dart';

class LiveCallScreen extends StatefulWidget {
  final String callerNumber;
  const LiveCallScreen({super.key, required this.callerNumber});

  @override
  State<LiveCallScreen> createState() => _LiveCallScreenState();
}

class _LiveCallScreenState extends State<LiveCallScreen> {
  static const _platform = MethodChannel('com.example.ai_scam_shield/dialer');
  final WebRtcSignalingService _signaling = WebRtcSignalingService();
  
  double _riskScore = 0.0;
  String _riskLabel = "safe";
  double _deepfakeScore = 0.0;
  bool _isDeepfake = false;
  
  final List<String> _transcripts = [];
  final List<Map<String, dynamic>> _timeline = [];
  
  String _statusMessage = "Connecting guard...";
  bool _alerted = false;
  bool _showKeywordWarning = false;
  String _triggeredKeyword = "";
  final Set<String> _flaggedKeywords = {};
  StreamSubscription? _stateSubscription;

  @override
  void initState() {
    super.initState();
    _startWebRtcCall();
  }

  Future<void> _startWebRtcCall() async {
    print("[Call Guard] Starting WebRTC microphone stream...");
    // Listen to real-time classification feeds
    _stateSubscription = _signaling.stateStream.listen((data) {
      if (data.containsKey("error")) {
        setState(() {
          _statusMessage = data["error"];
        });
        return;
      }
      
      if (data["status"] == "disconnected") {
        Navigator.pop(context);
        return;
      }

      setState(() {
        _statusMessage = "Screening Call (Turn on Speaker Mode to monitor caller)";
        _riskScore = (data["score"] ?? 0.0).toDouble();
        _riskLabel = data["label"] ?? "safe";
        _deepfakeScore = (data["deepfake_score"] ?? 0.0).toDouble();
        _isDeepfake = data["is_deepfake"] ?? false;
        
        final newTxt = data["transcript"] ?? "";
        if (newTxt.isNotEmpty && !_transcripts.contains(newTxt)) {
          _transcripts.add(newTxt);
          _timeline.add({
            "text": newTxt,
            "score": _riskScore,
            "label": _riskLabel,
            "time": DateTime.now().toLocal().toString().substring(11, 19)
          });
          _scanTranscriptForKeywords(newTxt);
        }
      });

      // Show alert if scam is verified
      if (_riskLabel == "fraud" && !_alerted) {
        _alerted = true;
        _showFraudAlert();
      }
    });

    await _signaling.startCall(widget.callerNumber);
  }

  void _scanTranscriptForKeywords(String text) {
    final lowerText = text.toLowerCase();
    final Map<String, List<String>> keywordMap = {
      "OTP": ["otp", "one-time password", "one time password"],
      "PIN / PASSWORD": ["pin", "password", "upi pin"],
      "CARD DETAILS": ["debit card", "credit card", "cvv", "card number", "card details"],
      "AADHAAR CARD": ["aadhaar", "aadhar"],
      "PAN CARD": ["pan card", "pan number"],
      "BANK DETAILS": ["bank account", "bank details", "account number"],
      "PERSONAL INFO": ["personal details", "mother's name", "date of birth"],
    };

    for (var entry in keywordMap.entries) {
      final key = entry.key;
      for (var pattern in entry.value) {
        if (lowerText.contains(pattern) && !_flaggedKeywords.contains(pattern)) {
          _flaggedKeywords.add(pattern);
          _triggerScamKeywordAlert(key);
          break;
        }
      }
    }
  }

  void _triggerScamKeywordAlert(String keywordName) {
    // Play native beep sound via MethodChannel
    _platform.invokeMethod("playBeep");

    // Show high importance local notification
    _platform.invokeMethod("showNotification", {
      "title": "⚠️ SECURITY ALERT: SCAM DETECTED",
      "message": "Caller requested sensitive detail: $keywordName. Do NOT share!",
    });

    // Show visual flashing hazard indicator in the app
    setState(() {
      _showKeywordWarning = true;
      _triggeredKeyword = keywordName;
    });

    // Dismiss the flashing indicator after 4 seconds
    Timer(const Duration(seconds: 4), () {
      if (mounted) {
        setState(() {
          _showKeywordWarning = false;
        });
      }
    });
  }

  void _showFraudAlert() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext ctx) {
        return AlertDialog(
          backgroundColor: const Color(0xFF1E0A10),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
            side: const BorderSide(color: Colors.redAccent, width: 2),
          ),
          title: Center(
            child: Text(
              "🚨 FRAUD DETECTED!",
              style: GoogleFonts.inter(color: Colors.redAccent, fontWeight: FontWeight.w900),
            ),
          ),
          content: Text(
            "Our AI detected scam signatures and high risk patterns in this conversation.\n\n"
            "DO NOT share OTP, UPI PIN, or bank passwords. Disconnect immediately!",
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(color: Colors.white, fontSize: 13, height: 1.4),
          ),
          actionsAlignment: MainAxisAlignment.center,
          actions: [
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.redAccent,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              onPressed: () {
                Navigator.pop(ctx);
                _hangUp();
              },
              child: Text(
                "Hang Up Now",
                style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.bold),
              ),
            )
          ],
        );
      },
    );
  }

  Future<void> _hangUp() async {
    await _signaling.stopCall();
    if (mounted) {
      Navigator.pop(context);
    }
  }

  @override
  void dispose() {
    _stateSubscription?.cancel();
    _signaling.stopCall();
    super.dispose();
  }

  Color _getRiskColor() {
    if (_riskLabel == "fraud") return Colors.redAccent[400]!;
    if (_riskLabel == "suspicious") return Colors.amber[600]!;
    return Colors.greenAccent[400]!;
  }

  @override
  Widget build(BuildContext context) {
    final darkBlue = const Color(0xFF0A0E1A);
    final cardColor = const Color(0xFF111827);
    final riskColor = _getRiskColor();

    return Scaffold(
      backgroundColor: darkBlue,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12),
          child: Column(
            children: [
              // Header caller indicator
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back, color: Colors.white),
                    onPressed: _hangUp,
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.redAccent.withOpacity(0.1),
                      border: Border.all(color: Colors.redAccent.withOpacity(0.3)),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      "● SCREENING CALL",
                      style: GoogleFonts.inter(color: Colors.redAccent, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 14),

              Text(
                widget.callerNumber,
                style: GoogleFonts.inter(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w900),
              ),
              const SizedBox(height: 4),
              Text(
                _statusMessage,
                style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 13),
              ),
              const SizedBox(height: 24),

              // Keyword Warning Banner
              if (_showKeywordWarning)
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.only(bottom: 18),
                  padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.amber[900]!.withOpacity(0.3),
                    border: Border.all(color: Colors.amber[500]!, width: 2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.gpp_maybe, color: Colors.amber, size: 28),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "CRITICAL INFO REQUESTED!",
                              style: GoogleFonts.inter(color: Colors.amber[300], fontWeight: FontWeight.bold, fontSize: 13),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              "Caller requested your $_triggeredKeyword.",
                              style: GoogleFonts.inter(color: Colors.white, fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),

              // Deepfake Warning Banner
              if (_isDeepfake)
                Container(
                  width: double.infinity,
                  margin: const EdgeInsets.only(bottom: 18),
                  padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.redAccent[700]!.withOpacity(0.2),
                    border: Border.all(color: Colors.redAccent[700]!, width: 2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.warning_amber_rounded, color: Colors.redAccent, size: 24),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              "DEEPFAKE DETECTED",
                              style: GoogleFonts.inter(color: Colors.redAccent, fontWeight: FontWeight.w900, fontSize: 12, letterSpacing: 0.5),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              "AI-synthesized voice detected. Stay alert!",
                              style: GoogleFonts.inter(color: Colors.white, fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        "${(_deepfakeScore * 100).round()}%",
                        style: GoogleFonts.inter(color: Colors.redAccent, fontWeight: FontWeight.w900, fontSize: 16),
                      )
                    ],
                  ),
                ),

              // Radial Score Gauge
              Center(
                child: Container(
                  width: 170,
                  height: 170,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: riskColor.withOpacity(0.15), width: 14),
                  ),
                  child: Center(
                    child: Container(
                      width: 140,
                      height: 140,
                      decoration: BoxDecoration(
                        color: cardColor,
                        shape: BoxShape.circle,
                        border: Border.all(color: riskColor, width: 4),
                      ),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            "${(_riskScore * 100).round()}%",
                            style: GoogleFonts.inter(color: riskColor, fontSize: 38, fontWeight: FontWeight.w900),
                          ),
                          Text(
                            "SCAM RISK",
                            style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Live Transcript card
              Expanded(
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: cardColor,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF1E2D45)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "LIVE TRANSCRIPT (ENGLISH ONLY)",
                        style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.5),
                      ),
                      const SizedBox(height: 10),
                      Expanded(
                        child: _timeline.isEmpty
                            ? Center(
                                child: Text(
                                  "Say something to begin...",
                                  style: GoogleFonts.inter(color: Colors.grey[600], fontSize: 13),
                                ),
                              )
                            : ListView.builder(
                                itemCount: _timeline.length,
                                itemBuilder: (context, index) {
                                  final item = _timeline[index];
                                  final double itemScore = item["score"];
                                  return Padding(
                                    padding: const EdgeInsets.only(bottom: 8.0),
                                    child: Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          "[${item["time"]}] ",
                                          style: GoogleFonts.inter(color: Colors.grey[600], fontSize: 10, fontWeight: FontWeight.bold),
                                        ),
                                        Expanded(
                                          child: Text(
                                            "\"${item["text"]}\"",
                                            style: GoogleFonts.inter(color: Colors.white, fontSize: 13, height: 1.4),
                                          ),
                                        ),
                                        const SizedBox(width: 6),
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: Colors.redAccent.withOpacity(0.1),
                                            borderRadius: BorderRadius.circular(6),
                                          ),
                                          child: Text(
                                            "${(itemScore * 100).round()}%",
                                            style: GoogleFonts.inter(color: Colors.redAccent, fontSize: 9, fontWeight: FontWeight.bold),
                                          ),
                                        )
                                      ],
                                    ),
                                  );
                                },
                              ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // End Call Control Button
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.redAccent[700],
                  minimumSize: const Size(double.infinity, 56),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 4,
                ),
                onPressed: _hangUp,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.call_end, color: Colors.white, size: 24),
                    const SizedBox(width: 10),
                    Text(
                      "DECLINE CALL",
                      style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.w900, letterSpacing: 0.5),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
