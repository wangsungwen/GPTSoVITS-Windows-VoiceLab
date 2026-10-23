@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0" || exit /b 1
if not exist "%~dp0scripts\start.ps1" (
    echo Missing scripts\start.ps1. Extract the complete deployment kit first.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start.ps1" -Task WebUI
set "TASK_EXIT=%ERRORLEVEL%"
if not "%TASK_EXIT%"=="0" echo Task failed. Review the message above and logs.
pause
exit /b %TASK_EXIT%
