@echo off
cd /d "%~dp0"
echo Preparing to push code to GitHub repository: https://github.com/dineshvipin24/i-scam-shield.git
echo.

git add .
git commit -m "Add PyTorch AI Voice Detector integration and /api/detect-voice endpoint"
git branch -M main
git pull origin main --rebase
git push -u origin main

echo.
echo ==============================================
echo Code pushed successfully!
echo You can now go to Railway, Vercel, or Render to check your deployment.
echo ==============================================
echo.
pause
