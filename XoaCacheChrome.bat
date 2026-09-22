@echo off
title Xoa Cache Chrome - Giai Phong Dung Luong
color 0B

set CHROME_DATA=%LOCALAPPDATA%\Google\Chrome\User Data

echo =====================================================================
echo     XOA CACHE CHROME - Giai phong dung luong cache
echo     (Giu nguyen: tai khoan, mat khau, bookmark, extension)
echo =====================================================================
echo.

:: Kiem tra Chrome co dang chay khong
tasklist /fi "imagename eq chrome.exe" /nh 2>&1 | find /i "chrome.exe" >nul
if not errorlevel 1 (
    echo [CANH BAO] Chrome dang chay! Can tat Chrome truoc.
    echo            Chay TatChrome.bat de tat nhanh, roi chay lai script nay.
    echo.
    pause
    exit /b 1
)

:: Kiem tra thu muc Chrome User Data
if not exist "%CHROME_DATA%" (
    echo [LOI] Khong tim thay Chrome User Data tai:
    echo       %CHROME_DATA%
    echo       Ban co chac Chrome da duoc cai dat?
    echo.
    pause
    exit /b 1
)

echo [OK] Chrome dang tat. An toan de xoa cache.
echo.
echo [?] Xoa cache toan bo cac Chrome profile?
echo     Giu nguyen: tai khoan, mat khau, cookie, bookmark, extension.
echo     Anh huong: trang web load cham hon mot chut trong 1-2 ngay dau.
echo.
set /p CONFIRM=    Nhap Y de xac nhan, N de huy: 

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo [HUY] Khong thay doi gi.
    goto END
)

echo.
echo [INFO] Bat dau xoa cache...
echo.

set PROFILE_COUNT=0

:: Xu ly profile Default
if exist "%CHROME_DATA%\Default" (
    set /a PROFILE_COUNT+=1
    echo  Profile: Default
    call :XoaCache "%CHROME_DATA%\Default"
    echo.
)

:: Xu ly cac Profile khac (Profile 1, Profile 2, ...)
for /d %%P in ("%CHROME_DATA%\Profile *") do (
    if exist "%%P" (
        set /a PROFILE_COUNT+=1
        echo  Profile: %%~nxP
        call :XoaCache "%%P"
        echo.
    )
)

echo =====================================================================
echo  HOAN THANH! Da xu ly %PROFILE_COUNT% Chrome profile.
echo.
echo  - Tai khoan Google  : NGUYEN VEN
echo  - Mat khau da luu   : NGUYEN VEN
echo  - Bookmark / Tab    : NGUYEN VEN
echo  - Cookie / Dang nhap: NGUYEN VEN
echo  - Extension         : NGUYEN VEN
echo.
echo  Trang web co the load cham hon 1-2 ngay dau do Chrome
echo  phai tai lai cache tu internet. Sau do se nhanh nhu cu.
echo =====================================================================

:END
echo.
pause
exit /b 0

:: =====================================================================
:: Ham xoa cac thu muc cache trong 1 profile
:: =====================================================================
:XoaCache
    set DELETED=0

    if exist "%~1\Cache" (
        rd /s /q "%~1\Cache" 2>nul
        echo    [OK] Cache
        set DELETED=1
    )
    if exist "%~1\Code Cache" (
        rd /s /q "%~1\Code Cache" 2>nul
        echo    [OK] Code Cache
        set DELETED=1
    )
    if exist "%~1\GPUCache" (
        rd /s /q "%~1\GPUCache" 2>nul
        echo    [OK] GPUCache
        set DELETED=1
    )
    if exist "%~1\ShaderCache" (
        rd /s /q "%~1\ShaderCache" 2>nul
        echo    [OK] ShaderCache
        set DELETED=1
    )
    if "%DELETED%"=="0" (
        echo    [SKIP] Khong co cache nao can xoa
    )
exit /b 0
