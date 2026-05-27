@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM AI Daily Digest — Daily Collection Runner
REM Configure this script in Windows Task Scheduler to run daily at 08:00

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo ================================================
echo  AI Daily Digest — Daily Collection
echo  Date: %date% %time%
echo ================================================

echo.
echo [1/3] Running collector...
python "%PROJECT_DIR%collector\main.py"
if errorlevel 1 (
    echo [ERROR] Collector failed!
    pause
    exit /b 1
)

echo.
echo [2/3] Committing changes...
git add data/
git commit -m "Daily update: %date%"

echo.
echo [3/3] Pushing to GitHub...
git push origin main
if errorlevel 1 (
    echo [WARNING] Push failed — check your network or git remote
)

echo.
echo Done! Data updated for %date%
