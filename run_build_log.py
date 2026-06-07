import subprocess
import os
import sys

def find_jdk_and_jbr():
    # Find JBR (Java 21 from IntelliJ) to run Gradle
    jbr_candidates = [
        r"C:\Program Files\JetBrains\IntelliJ IDEA 2025.2.2\jbr",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\IntelliJ IDEA 2025.2.2\jbr")
    ]
    jbr_path = None
    for p in jbr_candidates:
        if os.path.exists(os.path.join(p, "bin", "java.exe")):
            jbr_path = p
            break
            
    # Find JDK (Java 24 or 25 with jlink) to run the compiler
    jdk_candidates = [
        r"C:\Program Files\Java\jdk-24",
        r"C:\Program Files\Java\jdk-25",
        r"C:\Program Files\Eclipse Adoptium\jdk-25.0.0.36-hotspot"
    ]
    jdk_path = None
    for p in jdk_candidates:
        if os.path.exists(os.path.join(p, "bin", "java.exe")) and os.path.exists(os.path.join(p, "bin", "jlink.exe")):
            jdk_path = p
            break
            
    return jbr_path, jdk_path

def main():
    jbr_path, jdk_path = find_jdk_and_jbr()
    if not jbr_path:
        print("[ERROR] Could not find IntelliJ's JBR on this system.")
        return
    if not jdk_path:
        print("[ERROR] Could not find a full JDK containing jlink on this system.")
        return
        
    print(f"Setting Gradle Daemon Java (JAVA_HOME) to: {jbr_path}")
    print(f"Setting Gradle Compiler Java (org.gradle.java.home) to: {jdk_path}")
    
    os.environ["JAVA_HOME"] = jbr_path
    os.environ["PATH"] = os.path.join(os.environ["JAVA_HOME"], "bin") + os.path.pathsep + os.environ.get("PATH", "")
    
    # Run setup
    print("Running setup...")
    import setup_native_android_project
    setup_native_android_project.setup()
    
    print("Running Gradle build...")
    project_dir = os.path.abspath("android-app-project")
    gradlew = os.path.join(project_dir, "gradlew.bat")
    
    # Ensure gradlew exists
    if not os.path.exists(gradlew):
        print(f"[ERROR] Gradle wrapper not found at {gradlew}")
        return
        
    with open("gradle_build.log", "w", encoding="utf-8") as f:
        # Run Gradle assembleRelease
        process = subprocess.Popen(
            [gradlew, "assembleRelease"],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8"
        )
        
        while True:
            line = process.stdout.readline()
            if not line:
                break
            sys.stdout.write(line)
            f.write(line)
            
        process.wait()
        
    print(f"\nBuild finished with code: {process.returncode}")
    print("Full log written to gradle_build.log")

if __name__ == "__main__":
    main()
