@echo off
cd /d "%~dp0"
echo Preparing to push code to GitHub repository: https://github.com/dineshvipin24/i-scam-shield.git
echo.

git add .
git commit -m "Move demo.html to backend for Render deployment"
git branch -M main
git push -u origin main

echo.
echo ==============================================
echo Code pushed successfully!
echo You can now go to Render and click "Manual Deploy" -> "Clear cache and deploy".
echo ==============================================
echo.
pause
