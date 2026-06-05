import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/home_screen.dart';

const _channel = MethodChannel('com.example.ai_scam_shield/dialer');

Future<void> _requestDialerRole() async {
  try {
    final bool isDefault = await _channel.invokeMethod('isDefaultDialer') ?? false;
    if (!isDefault) {
      await _channel.invokeMethod('setDefaultDialer');
    }
  } catch (e) {
    print("[Dialer Role] Bypassed/Failed: $e");
  }
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await _requestDialerRole();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Scam Shield',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF00D4FF),
        scaffoldBackgroundColor: const Color(0xFF0A0E1A),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00D4FF),
          secondary: Color(0xFF00E676),
          background: Color(0xFF0A0E1A),
          surface: Color(0xFF111827),
        ),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
