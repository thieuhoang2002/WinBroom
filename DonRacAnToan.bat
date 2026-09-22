@echo off
title Don Rac - Xoa File An Toan 100%%
color 0A
chcp 65001 >nul

echo =====================================================================
echo     DON RAC TU DONG - XOA AN TOAN (Temp + npm cache + .cache + Docker Installer)
echo =====================================================================
echo.

:: 1. Thu muc Temp
echo [1/4] Dang xoa thu muc Temp: %TEMP%
if exist "%TEMP%" (
    rd /s /q "%TEMP%" 2>nul
    md "%TEMP%" 2>nul
    echo     OK - Da xoa xong %TEMP%
) else (
    echo     SKIP - Khong tim thay %TEMP%
)
echo.

:: 2. File Docker Desktop Installer trong Downloads
echo [2/4] Dang xoa: Docker Desktop Installer.exe
if exist "%USERPROFILE%\Downloads\Docker Desktop Installer.exe" (
    del /f /q "%USERPROFILE%\Downloads\Docker Desktop Installer.exe"
    echo     OK - Da xoa Docker Desktop Installer.exe
) else (
    echo     SKIP - File khong ton tai
)
echo.

:: 3. npm cache
echo [3/4] Dang xoa npm cache: %LOCALAPPDATA%\npm-cache
if exist "%LOCALAPPDATA%\npm-cache" (
    where npm >nul 2>&1
    if %errorlevel% == 0 (
        call npm cache clean --force 2>nul
    )
    rd /s /q "%LOCALAPPDATA%\npm-cache" 2>nul
    echo     OK - Da xoa npm-cache
) else (
    echo     SKIP - Khong tim thay npm-cache
)
echo.

:: 4. .cache (Hugging Face, pip, cargo...)
echo [4/4] Dang xoa thu muc .cache: %USERPROFILE%\.cache
if exist "%USERPROFILE%\.cache" (
    rd /s /q "%USERPROFILE%\.cache" 2>nul
    echo     OK - Da xoa .cache
) else (
    echo     SKIP - Khong tim thay .cache
)
echo.

echo =====================================================================
echo  HOAN THANH! Hay kiem tra lai dung luong trong File Explorer.
echo  (Chay QuetDungLuong.bat de quet lai neu can biet chinh xac)
echo =====================================================================
echo.
pause
