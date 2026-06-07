@echo off

echo ==============================================
echo Locating Java Environments (JBR & JDK) on your system...
echo ==============================================

rem 1. Locate JBR (Java 21 from IntelliJ) for Gradle execution
set "FOUND_JBR="
for %%p in (
    "C:\Program Files\JetBrains\IntelliJ IDEA 2025.2.2\jbr"
    "%LOCALAPPDATA%\Programs\IntelliJ IDEA 2025.2.2\jbr"
) do (
    if exist "%%~p\bin\java.exe" (
        set "FOUND_JBR=%%~p"
        goto found_jbr
    )
)

:found_jbr
if "%FOUND_JBR%"=="" (
    echo [ERROR] Could not find IntelliJ's JBR Java to run Gradle daemon.
    pause
    exit /b 1
)

rem 2. Locate Full JDK (Java 24 or 25 with jlink) for compilation
set "FOUND_JDK="
for %%p in (
    "C:\Program Files\Java\jdk-24"
    "C:\Program Files\Java\jdk-25"
    "C:\Program Files\Eclipse Adoptium\jdk-25.0.0.36-hotspot"
) do (
    if exist "%%~p\bin\java.exe" if exist "%%~p\bin\jlink.exe" (
        set "FOUND_JDK=%%~p"
        goto found_jdk
    )
)

:found_jdk
if "%FOUND_JDK%"=="" (
    echo [ERROR] Could not find a full JDK with jlink.exe for compilation.
    pause
    exit /b 1
)

echo Setting Gradle Daemon Java (JAVA_HOME) to: "%FOUND_JBR%"
echo Setting Gradle Compiler Java (Java Toolchain) to: "%FOUND_JDK%"

set "JAVA_HOME=%FOUND_JBR%"
set "PATH=%JAVA_HOME%\bin;%PATH%"

echo.
echo ==============================================
echo STEP 1: Running Python Setup Script to Organize Source Code...
echo ==============================================
python setup_native_android_project.py
echo.
if not exist android-app-project (
    echo [ERROR] setup_native_android_project.py did not run successfully.
    pause
    exit /b 1
)

echo ==============================================
echo STEP 2: Running Gradle to Compile the APK...
echo ==============================================
cd android-app-project
call gradlew.bat assembleRelease
echo.
echo ==============================================
echo BUILD RESULT:
echo If successful, your APK is located at:
echo android-app-project\app\build\outputs\apk\release\app-release.apk
echo ==============================================
pause
