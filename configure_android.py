import os

def configure():
    manifest_path = os.path.join("mobile-flutter", "android", "app", "src", "main", "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        print("[ERROR] AndroidManifest.xml not found!")
        print("Please make sure you have run 'flutter create --platforms=android .' inside the 'mobile-flutter' folder first.")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add permissions
    permissions = [
        '<uses-permission android:name="android.permission.ANSWER_PHONE_CALLS" />',
        '<uses-permission android:name="android.permission.READ_PHONE_STATE" />',
        '<uses-permission android:name="android.permission.READ_CONTACTS" />'
    ]
    
    modified = False
    for perm in permissions:
        if perm not in content:
            # Insert permissions right before the <application> tag
            content = content.replace("<application", f"    {perm}\n    <application")
            modified = True

    # 2. Add Dialer Intent Filters inside MainActivity activity tag
    intent_filters = """            <intent-filter>
                <action android:name="android.intent.action.DIAL" />
                <category android:name="android.intent.category.DEFAULT" />
                <data android:scheme="tel" />
            </intent-filter>
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="tel" />
            </intent-filter>"""

    if "android.intent.action.DIAL" not in content:
        # We find MainActivity activity block end tag and insert intent filters before it
        # Or look for </activity> inside MainActivity
        # Let's do a reliable replace of MainActivity declaration
        # Standard flutter manifest has:
        # <activity
        #     android:name=".MainActivity"
        #     ... >
        #     <meta-data ... />
        #     <intent-filter> ... </intent-filter>
        # </activity>
        
        main_activity_index = content.find('android:name=".MainActivity"')
        if main_activity_index != -1:
            end_activity_index = content.find('</activity>', main_activity_index)
            if end_activity_index != -1:
                content = content[:end_activity_index] + f"\n{intent_filters}\n        " + content[end_activity_index:]
                modified = True

    if modified:
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[SUCCESS] AndroidManifest.xml configured successfully with system call blocker permissions and dialer roles!")
    else:
        print("[INFO] AndroidManifest.xml was already configured.")

if __name__ == "__main__":
    configure()
