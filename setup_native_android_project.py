import os
import shutil

def setup():
    src_dir = "android-app"
    dest_dir = "android-app-project"
    
    if not os.path.exists(src_dir):
        print(f"[ERROR] Source directory {src_dir} not found!")
        return
        
    print("Initializing Native Android Project configuration...")
    
    # 1. Create directory structure
    dirs = [
        dest_dir,
        os.path.join(dest_dir, "gradle", "wrapper"),
        os.path.join(dest_dir, "app"),
        os.path.join(dest_dir, "app", "src", "main"),
        os.path.join(dest_dir, "app", "src", "main", "java", "com", "campprotect", "scamshield"),
        os.path.join(dest_dir, "app", "src", "main", "res", "values"),
        os.path.join(dest_dir, "app", "src", "main", "res", "mipmap"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        
    # 2. Copy source directories
    subdirs = ["activities", "database", "overlay", "repository", "scamdetection", "services", "speech", "ui"]
    for sd in subdirs:
        src_path = os.path.join(src_dir, sd)
        dest_path = os.path.join(dest_dir, "app", "src", "main", "java", "com", "campprotect", "scamshield", sd)
        if os.path.exists(src_path):
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            print(f"Copied {sd} to project.")
            
    # 3. Copy AndroidManifest.xml
    manifest_src = os.path.join(src_dir, "manifest", "AndroidManifest.xml")
    manifest_dest = os.path.join(dest_dir, "app", "src", "main", "AndroidManifest.xml")
    if os.path.exists(manifest_src):
        shutil.copy2(manifest_src, manifest_dest)
        print("Copied AndroidManifest.xml.")
        
    # 4. Copy gradle wrapper from mobile-flutter
    flutter_gradle_dir = os.path.join("mobile-flutter", "android")
    if os.path.exists(flutter_gradle_dir):
        files_to_copy = [
            ("gradlew", dest_dir),
            ("gradlew.bat", dest_dir),
            (os.path.join("gradle", "wrapper", "gradle-wrapper.properties"), os.path.join(dest_dir, "gradle", "wrapper")),
            (os.path.join("gradle", "wrapper", "gradle-wrapper.jar"), os.path.join(dest_dir, "gradle", "wrapper")),
        ]
        for src_rel, dest_rel in files_to_copy:
            full_src = os.path.join(flutter_gradle_dir, src_rel)
            full_dest = os.path.join(dest_rel, os.path.basename(src_rel))
            if os.path.exists(full_src):
                shutil.copy2(full_src, full_dest)
        print("Copied Gradle wrapper from Flutter android project.")
        
    # 5. Create project gradle files
    build_gradle_content = """// Top-level build file where you can add configuration options common to all sub-projects/modules.
buildscript {
    ext {
        compose_version = '1.6.1'
        kotlin_version = '1.9.22'
        ksp_version = '1.9.22-1.0.17'
    }
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.13.2'
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
        classpath "com.google.devtools.ksp:com.google.devtools.ksp.gradle.plugin:$ksp_version"
    }
}

tasks.register('clean', Delete) {
    delete rootProject.buildDir
}
"""
    with open(os.path.join(dest_dir, "build.gradle"), "w", encoding="utf-8") as f:
        f.write(build_gradle_content)
        
    settings_gradle_content = """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "CampProtectScamShield"
include ':app'
"""
    with open(os.path.join(dest_dir, "settings.gradle"), "w", encoding="utf-8") as f:
        f.write(settings_gradle_content)
        
    gradle_properties_content = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
"""
    with open(os.path.join(dest_dir, "gradle.properties"), "w", encoding="utf-8") as f:
        f.write(gradle_properties_content)
        
    app_build_gradle_content = """plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
    id 'com.google.devtools.ksp'
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(24)
    }
}

android {
    namespace 'com.campprotect.scamshield'
    compileSdk 34

    defaultConfig {
        applicationId "com.campprotect.scamshield"
        minSdk 26
        targetSdk 34
        versionCode 1
        versionName "1.0"

        testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary true
        }
    }

    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
            signingConfig signingConfigs.debug
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = '17'
    }
    buildFeatures {
        compose true
    }
    composeOptions {
        kotlinCompilerExtensionVersion '1.5.8'
    }
    packagingOptions {
        resources {
            excludes += '/META-INF/{AL2.0,LGPL2.1}'
        }
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.lifecycle:lifecycle-runtime-ktx:2.7.0'
    implementation 'androidx.activity:activity-compose:1.8.2'

    implementation platform('androidx.compose:compose-bom:2024.01.00')
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.compose.ui:ui'
    implementation 'androidx.compose.ui:ui-graphics'
    implementation 'androidx.compose.ui:ui-tooling-preview'
    implementation 'androidx.compose.material3:material3'
    implementation 'androidx.compose.material:material-icons-extended'

    def room_version = "2.6.1"
    implementation "androidx.room:room-runtime:$room_version"
    implementation "androidx.room:room-ktx:$room_version"
    ksp "androidx.room:room-compiler:$room_version"

    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'

    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
"""
    with open(os.path.join(dest_dir, "app", "build.gradle"), "w", encoding="utf-8") as f:
        f.write(app_build_gradle_content)
        
    # 6. Create values
    strings_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Camp Protect</string>
</resources>
"""
    with open(os.path.join(dest_dir, "app", "src", "main", "res", "values", "strings.xml"), "w", encoding="utf-8") as f:
        f.write(strings_content)
        
    colors_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="purple_200">#FFBB86FC</color>
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
"""
    with open(os.path.join(dest_dir, "app", "src", "main", "res", "values", "colors.xml"), "w", encoding="utf-8") as f:
        f.write(colors_content)
        
    themes_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.CampProtect" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <!-- Customize your theme here. -->
    </style>
</resources>
"""
    with open(os.path.join(dest_dir, "app", "src", "main", "res", "values", "themes.xml"), "w", encoding="utf-8") as f:
        f.write(themes_content)

    # 7. Create launcher icons (Vector drawables)
    icon_content = """<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#FFC62828"
        android:pathData="M0,0h108v108h-108z" />
    <path
        android:fillColor="#FFFFFF"
        android:pathData="M54,20L24,35v30c0,18.5 12.8,35.8 30,40 17.2,-4.2 30,-21.5 30,-40V35L54,20zM54,40c2.2,0 4,1.8 4,4v12c0,2.2 -1.8,4 -4,4s-4,-1.8 -4,-4V44C50,41.8 51.8,40 54,40zM54,72c-2.2,0 -4,-1.8 -4,-4s1.8,-4 4,-4 4,1.8 4,4 -1.8,4 -4,4z" />
</vector>
"""
    with open(os.path.join(dest_dir, "app", "src", "main", "res", "mipmap", "ic_launcher.xml"), "w", encoding="utf-8") as f:
        f.write(icon_content)
    with open(os.path.join(dest_dir, "app", "src", "main", "res", "mipmap", "ic_launcher_round.xml"), "w", encoding="utf-8") as f:
        f.write(icon_content)

    # Create local.properties copying SDK path from mobile-flutter
    local_props_src = os.path.join("mobile-flutter", "android", "local.properties")
    local_props_dest = os.path.join(dest_dir, "local.properties")
    if os.path.exists(local_props_src):
        with open(local_props_src, "r") as src_f:
            lines = src_f.readlines()
        with open(local_props_dest, "w") as dest_f:
            for line in lines:
                if line.startswith("sdk.dir"):
                    dest_f.write(line)
                    break
                    
    print("[SUCCESS] Native Android project successfully set up in 'android-app-project'!")

if __name__ == "__main__":
    setup()
