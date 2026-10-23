@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0" || exit /b 1
if not exist "%~dp0scripts\repair_openjtalk.ps1" (
    echo Missing scripts\repair_openjtalk.ps1. Update the complete repair files first.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\repair_openjtalk.ps1"
set "TASK_EXIT=%ERRORLEVEL%"
if not "%TASK_EXIT%"=="0" echo Task failed. Review the message above and logs.
pause
exit /b %TASK_EXIT%
