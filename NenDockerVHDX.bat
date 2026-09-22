@echo off
title Nen Docker VHDX - Thu Hoi Dung Luong
color 0B

:: Kiem tra quyen Admin, neu chua co thi tu dong xin quyen
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Dang yeu cau quyen Administrator...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
    exit /b
)

set PYTHONIOENCODING=utf-8

echo =====================================================================
echo     NEN DOCKER VHDX - GIU LAI IMAGE, GIAI PHONG DUNG LUONG TRONG
echo =====================================================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0src\NenDockerVHDX.ps1"

echo.
pause
