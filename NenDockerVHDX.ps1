# Script: Nen Docker VHDX (Thu hep o ao Docker de giai phong dung luong)
# Khong xoa image/container, chi nen file VHDX de lay lai khong gian trong
# Chay voi quyen Administrator

param()

$ErrorActionPreference = "Continue"
$vhdxPath = "$env:LOCALAPPDATA\Docker\wsl\disk\docker_data.vhdx"

function Write-Color($text, $color = "White") {
    Write-Host $text -ForegroundColor $color
}

Write-Color "=================================================================" "Cyan"
Write-Color "     NEN DOCKER VHDX - THU HOI DUNG LUONG TRONG" "Cyan"
Write-Color "     (Giu nguyen toan bo image va container)" "Cyan"
Write-Color "=================================================================" "Cyan"
Write-Host ""

# Kiem tra quyen Admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Color "[LOI] Script nay can chay voi quyen Administrator!" "Red"
    Write-Color "      Hay dong cua so nay va chay lai NenDockerVHDX.bat (Run as administrator)" "Yellow"
    Read-Host "Nhan Enter de thoat"
    exit 1
}

# Kiem tra file VHDX ton tai
if (-not (Test-Path $vhdxPath)) {
    Write-Color "[LOI] Khong tim thay file VHDX tai:" "Red"
    Write-Color "      $vhdxPath" "Yellow"
    Write-Color "      Ban co chac Docker Desktop da duoc cai dat?" "Yellow"
    Read-Host "Nhan Enter de thoat"
    exit 1
}

# Kich thuoc truoc khi nen
$sizeBefore = (Get-Item $vhdxPath).Length
$sizeBeforeGB = [math]::Round($sizeBefore / 1GB, 2)
Write-Color "[INFO] File VHDX hien tai: $vhdxPath" "White"
Write-Color "[INFO] Kich thuoc hien tai: $sizeBeforeGB GB" "Yellow"
Write-Host ""

# Kiem tra Docker dang chay
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerProcess) {
    Write-Color "[CANH BAO] Docker Desktop dang chay!" "Yellow"
    Write-Color "           Hay tat Docker Desktop truoc khi tiep tuc." "Yellow"
    Write-Host ""
    $confirm = Read-Host "Ban da tat Docker Desktop chua? Tiep tuc? (y/n)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Color "Da huy. Hay tat Docker Desktop roi chay lai script." "Red"
        exit 0
    }
}

Write-Color "[BUOC 1] Dang tat WSL (wsl --shutdown)..." "Cyan"
try {
    wsl --shutdown 2>$null
    Write-Color "         OK - WSL da tat." "Green"
} catch {
    Write-Color "         SKIP - WSL co the da tat san." "Yellow"
}

Write-Host ""
Write-Color "[BUOC 2] Doi 3 giay de WSL dung hoan toan..." "Cyan"
Start-Sleep -Seconds 3

Write-Host ""
Write-Color "[BUOC 3] Dang nen file VHDX bang diskpart..." "Cyan"
Write-Color "         (Qua trinh nay co the mat 1-5 phut, vui long doi...)" "Yellow"

# Tao file lenh diskpart tam thoi
$diskpartScript = @"
select vdisk file="$vhdxPath"
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@

$tempScript = "$env:TEMP\docker_compact_diskpart.txt"
$diskpartScript | Out-File -FilePath $tempScript -Encoding ASCII

try {
    $diskpartOutput = diskpart /s $tempScript 2>&1
    $diskpartResult = $LASTEXITCODE
    
    if ($diskpartResult -eq 0) {
        Write-Color "         OK - Diskpart hoan thanh." "Green"
    } else {
        Write-Color "         Diskpart bao loi, thu Method 2 (Optimize-VHD)..." "Yellow"
        
        # Method 2: Optimize-VHD (can Hyper-V)
        try {
            Optimize-VHD -Path $vhdxPath -Mode Full -ErrorAction Stop
            Write-Color "         OK - Optimize-VHD hoan thanh." "Green"
        } catch {
            Write-Color "         Optimize-VHD khong kha dung (can kich hoat Hyper-V)." "Yellow"
            Write-Color "         Ket qua tu diskpart:" "White"
            $diskpartOutput | Write-Host
        }
    }
} catch {
    Write-Color "         [LOI] $_" "Red"
} finally {
    Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
}

# Kich thuoc sau khi nen
Write-Host ""
$sizeAfter = (Get-Item $vhdxPath).Length
$sizeAfterGB = [math]::Round($sizeAfter / 1GB, 2)
$savedGB = [math]::Round(($sizeBefore - $sizeAfter) / 1GB, 2)

Write-Color "=================================================================" "Cyan"
Write-Color " KET QUA:" "Cyan"
Write-Color "   Truoc khi nen : $sizeBeforeGB GB" "White"
Write-Color "   Sau khi nen   : $sizeAfterGB GB" "Green"
if ($savedGB -gt 0) {
    Write-Color "   Da thu hoi    : $savedGB GB" "Green"
    Write-Color "" ""
    Write-Color "   Thanh cong! Toan bo image va container van con nguyen." "Green"
} else {
    Write-Color "   Khong co thay doi - File VHDX da o kich thuoc toi thieu." "Yellow"
    Write-Color "   Dieu nay co nghia la Docker dang su dung gan het khong gian trong file." "Yellow"
}
Write-Color "=================================================================" "Cyan"
Write-Host ""
Read-Host "Nhan Enter de dong cua so"
