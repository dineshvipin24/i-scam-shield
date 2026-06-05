import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:contacts_service/contacts_service.dart';
import '../services/api.dart';

class ContactsScreen extends StatefulWidget {
  const ContactsScreen({super.key});

  @override
  State<ContactsScreen> createState() => _ContactsScreenState();
}

class _ContactsScreenState extends State<ContactsScreen> {
  List<Contact> _contacts = [];
  bool _loading = true;
  bool _syncing = false;

  @override
  void initState() {
    super.initState();
    _fetchContacts();
  }

  Future<void> _fetchContacts() async {
    final status = await Permission.contacts.request();
    if (status.isGranted) {
      try {
        final contacts = await ContactsService.getContacts(withThumbnails: false);
        setState(() {
          _contacts = contacts.toList();
          _loading = false;
        });
      } catch (e) {
        print("[Contacts] Failed to load: $e");
        setState(() => _loading = false);
      }
    } else {
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Permission denied to read contacts.")),
      );
    }
  }

  Future<void> _syncWithServer() async {
    if (_contacts.isEmpty) return;
    setState(() => _syncing = true);

    List<Map<String, String>> contactsList = [];
    for (var c in _contacts) {
      final name = c.displayName ?? "";
      if (c.phones != null && c.phones!.isNotEmpty) {
        for (var p in c.phones!) {
          var val = p.value ?? "";
          // Normalize number (remove spaces, dashes)
          val = val.replaceAll(RegExp(r'[\s\-()]'), '');
          if (val.isNotEmpty) {
            contactsList.add({"name": name, "phone": val});
          }
        }
      }
    }

    final success = await ApiService.syncContacts(contactsList);
    setState(() => _syncing = false);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(success 
          ? "Successfully synced ${contactsList.length} contacts to Shield Server!" 
          : "Sync failed. Check backend connection."),
        backgroundColor: success ? Colors.green[700] : Colors.red[700],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final darkBlue = const Color(0xFF0A0E1A);
    final cardColor = const Color(0xFF111827);

    return Scaffold(
      backgroundColor: darkBlue,
      appBar: AppBar(
        backgroundColor: cardColor,
        elevation: 0,
        title: Text(
          "Saved Contacts",
          style: GoogleFonts.inter(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        actions: [
          if (!_loading && _contacts.isNotEmpty)
            _syncing
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: 16.0),
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(color: Color(0xFF00D4FF), strokeWidth: 2),
                      ),
                    ),
                  )
                : TextButton.icon(
                    onPressed: _syncWithServer,
                    icon: const Icon(Icons.cloud_upload, color: Color(0xFF00D4FF), size: 18),
                    label: Text(
                      "Sync",
                      style: GoogleFonts.inter(color: const Color(0xFF00D4FF), fontWeight: FontWeight.bold),
                    ),
                  )
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF00D4FF)))
          : _contacts.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.people_outline, size: 48, color: Colors.grey[600]),
                      const SizedBox(height: 12),
                      Text(
                        "No contacts found",
                        style: GoogleFonts.inter(color: Colors.grey[400]),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  itemCount: _contacts.length,
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemBuilder: (context, index) {
                    final c = _contacts[index];
                    final phone = c.phones != null && c.phones!.isNotEmpty 
                        ? c.phones!.first.value ?? "No number" 
                        : "No number";
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundColor: const Color(0xFF1E2D45),
                        child: Text(
                          c.displayName != null && c.displayName!.isNotEmpty 
                              ? c.displayName![0].toUpperCase() 
                              : "?",
                          style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                      ),
                      title: Text(
                        c.displayName ?? "Unknown",
                        style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14),
                      ),
                      subtitle: Text(
                        phone,
                        style: GoogleFonts.inter(color: Colors.grey[400], fontSize: 12),
                      ),
                    ).border(border: const Border(bottom: BorderSide(color: Color(0xFF111827))));
                  },
                ),
    );
  }
}

extension on ListTile {
  Widget border({required Border border}) {
    return Container(
      decoration: BoxDecoration(border: border),
      child: this,
    );
  }
}
