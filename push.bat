@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\push.ps1"
set "push_exit=%ERRORLEVEL%"
echo.
if not "%push_exit%"=="0" echo Push failed. Read the error above before retrying.
pause
exit /b %push_exit%
