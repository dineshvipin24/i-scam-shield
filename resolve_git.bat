@echo off
cd /d "%~dp0"
echo Aborting rebase and force pushing local state...
git rebase --abort
git add .
git commit -m "Force match local setup for Render deployment"
git push origin main --force
echo.
echo ==============================================
echo Force push complete!
echo ==============================================
pause
