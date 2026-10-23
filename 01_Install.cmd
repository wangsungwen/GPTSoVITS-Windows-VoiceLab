@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0" || exit /b 1
if not exist "%~dp0scripts\install.ps1" (
    echo Missing scripts\install.ps1. Extract the complete deployment kit first.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1" 
set "TASK_EXIT=%ERRORLEVEL%"
if not "%TASK_EXIT%"=="0" echo Task failed. Review the message above and logs.
pause
exit /b %TASK_EXIT%
