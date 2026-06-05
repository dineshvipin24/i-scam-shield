import 'dart:async';
import 'dart:convert';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'api.dart';

class WebRtcSignalingService {
  RTCPeerConnection? _peerConnection;
  MediaStream? _localStream;
  WebSocketChannel? _channel;
  
  // Real-time call logs/score controller
  final _onStateChange = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get stateStream => _onStateChange.stream;

  bool _isCallActive = false;
  bool get isCallActive => _isCallActive;

  // Initialize WebRTC and WebSocket Signaling
  Future<void> startCall(String callerNumber) async {
    if (_isCallActive) return;

    final baseUrl = await ApiService.getBaseUrl();
    // Swap http/https with ws/wss
    final wsUrl = baseUrl.replaceFirst("http", "ws") + "/stream/webrtc";
    
    print("[WebRTC] Connecting to signaling server: $wsUrl");
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
    } catch (e) {
      print("[WebRTC Error] Signaling socket failed: $e");
      _onStateChange.add({"error": "Failed to connect to signaling server"});
      return;
    }

    // Set up standard Google STUN servers
    final Map<String, dynamic> rtcConfig = {
      'iceServers': [
        {'url': 'stun:stun.l.google.com:19302'},
        {'url': 'stun:stun1.l.google.com:19302'},
      ]
    };

    final Map<String, dynamic> mediaConstraints = {
      'mandatory': {},
      'optional': [],
    };

    // Create RTCPeerConnection
    _peerConnection = await createPeerConnection(rtcConfig, mediaConstraints);

    // Listen to signaling socket messages
    _channel!.stream.listen((message) {
      _handleSignalingMessage(message);
    }, onError: (e) {
      print("[WebRTC Socket Error] $e");
      stopCall();
    }, onDone: () {
      print("[WebRTC Socket Done]");
      stopCall();
    });

    // Capture Local Microphone Stream
    final Map<String, dynamic> mediaConstraintsInput = {
      'audio': true,
      'video': false,
    };
    
    try {
      _localStream = await navigator.mediaDevices.getUserMedia(mediaConstraintsInput);
      // Add track to PeerConnection
      _localStream!.getTracks().forEach((track) {
        _peerConnection!.addTrack(track, _localStream!);
      });
      print("[WebRTC] Microphone track added to connection");
    } catch (e) {
      print("[WebRTC Error] Microphone access failed: $e");
      _onStateChange.add({"error": "Microphone permission or hardware error"});
      stopCall();
      return;
    }

    // SDP Offer constraints
    final Map<String, dynamic> sdpConstraints = {
      'mandatory': {
        'OfferToReceiveAudio': true,
        'OfferToReceiveVideo': false,
      },
      'optional': [],
    };

    // Create and Set Local Description
    RTCSessionDescription offer = await _peerConnection!.createOffer(sdpConstraints);
    await _peerConnection!.setLocalDescription(offer);
    
    // Send dynamic handshake initiation message
    _channel!.sink.add(jsonEncode({
      "event": "start",
      "start": {
        "callSid": "webrtc_${DateTime.now().millisecondsSinceEpoch}",
        "callerNumber": callerNumber,
      }
    }));

    // Send SDP Offer via WebSocket
    _channel!.sink.add(jsonEncode({
      "event": "sdp_offer",
      "sdp": offer.sdp,
      "type": offer.type,
    }));

    _isCallActive = true;
    print("[WebRTC] SDP Offer sent. Waiting for SDP Answer...");
  }

  // Handle incoming signaling messages from backend
  void _handleSignalingMessage(String messageStr) async {
    try {
      final msg = jsonDecode(messageStr);
      final event = msg["event"];

      if (event == "sdp_answer" && _peerConnection != null) {
        final sdp = msg["sdp"];
        final type = msg["type"];
        print("[WebRTC] Received SDP Answer from backend. Setting remote description.");
        RTCSessionDescription answer = RTCSessionDescription(sdp, type);
        await _peerConnection!.setRemoteDescription(answer);
      } 
      else if (event == "call_update") {
        // Real-time classification update (score, label, transcript, deepfake)
        _onStateChange.add(msg["data"]);
      }
    } catch (e) {
      print("[WebRTC] Error handling message: $e");
    }
  }

  // Terminate Connection and release media locks
  Future<void> stopCall() async {
    if (!_isCallActive) return;
    print("[WebRTC] Disconnecting active call...");

    try {
      if (_channel != null) {
        _channel!.sink.add(jsonEncode({"event": "stop"}));
        _channel!.sink.close();
      }
    } catch (e) {}

    try {
      _localStream?.getTracks().forEach((track) {
        track.stop();
      });
      _localStream?.dispose();
    } catch (e) {}

    try {
      await _peerConnection?.close();
      await _peerConnection?.dispose();
    } catch (e) {}

    _peerConnection = null;
    _localStream = null;
    _channel = null;
    _isCallActive = false;
    
    _onStateChange.add({"status": "disconnected"});
  }
}
