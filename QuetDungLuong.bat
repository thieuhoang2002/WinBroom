@echo off
title Quet Dung Luong O Dia - Vip Pro
color 0B

echo =====================================================================
echo          CONG CU QUET DUNG LUONG O DIA (DISK ANALYZER VIP PRO)
echo =====================================================================
echo.

python "%~dp0disk_analyzer.py"

if %errorlevel% neq 0 (
    echo.
    echo [THONG BAO] Co loi xay ra hoac chua tim thay Python.
    pause
)
