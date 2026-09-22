@echo off
title Tat Chrome Toan Bo (Kill All Chrome Processes)
color 0E

echo =====================================================================
echo     TAT CHROME TOAN BO - Giai phong bo nho ngam
echo =====================================================================
echo.

:: Dem so tien trinh chrome dang chay
for /f %%i in ('tasklist /fi "imagename eq chrome.exe" /nh ^| find /c "chrome.exe" 2^>^&1') do set COUNT=%%i

if "%COUNT%"=="0" (
    echo [OK] Khong co tien trinh Chrome nao dang chay.
    goto END
)

echo [INFO] Phat hien %COUNT% tien trinh Chrome dang chay ngam.
echo.

:: Kill toan bo chrome.exe
taskkill /F /IM chrome.exe >nul 2>&1

if %errorlevel% == 0 (
    echo [OK] Da tat toan bo %COUNT% tien trinh Chrome thanh cong.
    echo      Co the chay PhanTichChrome.bat an toan bay gio.
) else (
    echo [LOI] Khong the tat Chrome. Thu chay lai voi quyen Admin.
)

:END
echo.
pause
