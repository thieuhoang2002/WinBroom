# 🔧 Hướng Dẫn Chi Tiết Từng Công Cụ

> Đọc tài liệu này trước khi chạy để biết chính xác công cụ làm gì và cần chuẩn bị gì.
>
> 📁 File nguồn Python/PowerShell nằm trong thư mục `src/` — không cần mở trực tiếp.

---

## 📑 Mục lục

1. [QuetDungLuong — Phân tích dung lượng ổ đĩa](#1--quetdungluong--phân-tích-dung-lượng-ổ-đĩa)
2. [DonRacAnToan — Dọn file rác an toàn](#2--donracantoan--dọn-file-rác-an-toàn)
3. [TatChrome — Tắt Chrome toàn bộ](#3--tatchrome--tắt-chrome-toàn-bộ)
4. [PhanTichChrome — Phân tích Chrome Profiles](#4--phantichchrome--phân-tích-chrome-profiles)
5. [NenDockerVHDX — Nén ổ đĩa ảo Docker](#5--nendockervhdx--nén-ổ-đĩa-ảo-docker)

---

## 1. 🔍 QuetDungLuong — Phân tích dung lượng ổ đĩa

**Files:** `QuetDungLuong.bat` + `disk_analyzer.py`

### Làm gì?
Quét toàn bộ ổ đĩa (hoặc một thư mục cụ thể) và phân tích:
- **Top file nặng nhất** — tên, dung lượng, ngày sửa đổi, đường dẫn
- **Top thư mục nặng nhất** — tính cả toàn bộ thư mục con bên trong
- **Thống kê theo định dạng** — `.mp4`, `.zip`, `.dll`, `.iso`... chiếm bao nhiêu %
- **Báo cáo HTML** — mở trình duyệt xem dashboard đẹp mắt, có tìm kiếm & click để copy đường dẫn

### Cách chạy

```
Double-click QuetDungLuong.bat
```

Hoặc để quét sâu hơn vào thư mục hệ thống:
```
Chuột phải → Run as administrator
```

### Menu lựa chọn

Sau khi chạy, công cụ hiện menu:

```
[1]  Quét ổ C:\
[2]  Quét ổ D:\  (nếu có)
[U]  Chỉ quét thư mục người dùng (C:\Users\<tên>)  ← Nhanh hơn
[A]  Quét TẤT CẢ ổ đĩa
[C]  Nhập hoặc kéo thả thư mục bất kỳ vào
[Q]  Thoát
```

> 💡 **Mẹo:** Nhấn `Ctrl+C` bất kỳ lúc nào để dừng quét sớm và xem kết quả đã thu thập được.

### Kết quả xuất ra

- **Terminal:** Bảng màu hiển thị top files/thư mục/extensions ngay trong cửa sổ
- **`BaoCao_DungLuong.html`:** Dashboard HTML lưu cùng thư mục, tự hỏi có muốn mở trình duyệt không

### Lưu ý
- Không xóa bất kỳ file nào — chỉ đọc và báo cáo
- Thư mục bị chặn quyền (System Volume Information, v.v.) sẽ được bỏ qua tự động

---

## 2. 🗑️ DonRacAnToan — Dọn file rác an toàn

**File:** `DonRacAnToan.bat`

### Làm gì?
Xóa tự động các loại file rác đã được kiểm chứng an toàn 100%:

| Mục tiêu | Đường dẫn | Lý do an toàn |
|---|---|---|
| Thư mục Temp | `%TEMP%` (`AppData\Local\Temp`) | File tạm thời, Windows tự tạo lại |
| Docker Installer cũ | `%USERPROFILE%\Downloads\Docker Desktop Installer.exe` | Đã cài xong, file này không cần nữa |
| npm cache | `%LOCALAPPDATA%\npm-cache` | Cache tải package Node.js, rebuild được |
| Dev tools cache | `%USERPROFILE%\.cache` | Cache của pip, cargo, huggingface... |

### Cách chạy

```
Double-click DonRacAnToan.bat
```

Không cần Admin. Script sẽ in `OK` hoặc `SKIP` cho từng mục (SKIP nghĩa là mục đó không tồn tại trên máy).

### Lưu ý
- Thư mục `Temp` sẽ được **tạo lại rỗng** ngay sau khi xóa (Windows yêu cầu thư mục này tồn tại)
- Nếu ứng dụng đang chạy đang dùng file trong `Temp`, Windows tự giữ lại file đó — không bị lỗi

---

## 3. ❌ TatChrome — Tắt Chrome toàn bộ

**File:** `TatChrome.bat`

### Vấn đề cần giải quyết

Khi bạn click X để đóng cửa sổ Chrome, Chrome **không thực sự tắt hoàn toàn**. Nó giữ nhiều tiến trình con chạy ngầm (renderer, GPU, extension...) để lần sau khởi động nhanh hơn. Điều này:
- Chiếm RAM không cần thiết
- Khóa các file trong thư mục Chrome User Data → **không xóa được profile** khi dùng `PhanTichChrome.bat`

### Làm gì?
Dùng `taskkill /F /IM chrome.exe` để kill toàn bộ tiến trình Chrome, hiển thị số lượng tiến trình đã tắt.

### Cách chạy

```
Double-click TatChrome.bat
```

### Lưu ý
- Download đang chạy dở sẽ bị ngắt — kiểm tra trước khi chạy
- Chrome tự khôi phục các tab khi mở lại (session restore)
- **Chạy trước `PhanTichChrome.bat`** để tránh lỗi file bị khóa

---

## 4. 🌐 PhanTichChrome — Phân tích Chrome Profiles

**Files:** `PhanTichChrome.bat` + `src/PhanTichChrome.py`

### Vấn đề cần giải quyết

Docker trên Windows (WSL2) lưu toàn bộ dữ liệu vào một file ảo có đuôi `.vhdx`. File này **tự động phình to** khi bạn pull/build image, nhưng **không tự co lại** khi bạn xóa image đi.

```
Ví dụ:
  Kéo 10 image về → vhdx phình lên 10 GB
  Xóa hết 8 image → vhdx vẫn là 10 GB  ← lãng phí 8 GB
  Chạy NenDockerVHDX.bat → vhdx co lại còn 2 GB ✅
```

### Làm gì?
- Dừng WSL (`wsl --shutdown`)
- Dùng `diskpart compact vdisk` để nén file `.vhdx` — loại bỏ phần trống bên trong
- **Không xóa** image, container hay volume nào

### Quy trình khuyến nghị

```
Bước 1: Mở Docker Desktop → xóa image/container không cần nữa
         (hoặc chạy: docker system prune -a)

Bước 2: Tắt Docker Desktop hoàn toàn

Bước 3: Chuột phải NenDockerVHDX.bat → Run as administrator
         (Script sẽ tự xin quyền Admin nếu chưa có)

Bước 4: Đợi 1–5 phút → xem kết quả dung lượng đã thu hồi
```

> ⚠️ **Bắt buộc cần quyền Administrator.** Script tự động xin quyền khi chạy.

### Kết quả
Script hiển thị dung lượng trước/sau và số GB đã thu hồi được.

---

## 4. 🌐 PhanTichChrome — Phân tích Chrome Profiles

**Files:** `PhanTichChrome.bat` + `PhanTichChrome.py`

### Vấn đề cần giải quyết

Thư mục `Chrome\User Data` có thể chiếm **10–15 GB** vì chứa nhiều profile (mỗi profile là một tài khoản Google riêng biệt). Không biết profile nào đang dùng, profile nào là rác → không dám xóa.

### Làm gì?
Đọc file cấu hình của Chrome để hiển thị bảng đầy đủ thông tin từng profile:

| Cột | Nội dung |
|---|---|
| # | Số thứ tự |
| Folder | Tên thư mục (`Default`, `Profile 3`...) |
| Name / Email | Tên tài khoản Google đang đăng nhập |
| Size | Dung lượng thực tế của profile đó |
| Last Active | Lần cuối dùng profile này |
| Status | `signed-in` (có tài khoản) / `local` (không đăng nhập) |

Sau đó cho phép chọn profile muốn xóa theo số thứ tự — **có xác nhận trước khi xóa**.

### Cách chạy

```
Double-click PhanTichChrome.bat
```

> ⚠️ **Đóng Chrome trước khi chạy** — Script cảnh báo nếu Chrome đang mở, nhưng tốt nhất nên đóng để tránh file bị khóa.

### Lưu ý quan trọng
- Xóa profile Chrome **không ảnh hưởng** đến tài khoản Google — chỉ xóa dữ liệu cache, lịch sử, mật khẩu lưu trên máy
- Nếu profile đó có tài khoản quan trọng và **bạn nhớ mật khẩu**, xóa đi rồi đăng nhập lại hoàn toàn được
- Nếu **không chắc**, hãy xuất mật khẩu trước: Chrome → `chrome://settings/passwords` → Export

---

## 📊 Bảng so sánh nhanh

| Công cụ | Xóa không hỏi? | Cần Admin? | Ước tính tiết kiệm |
|---|---|---|---|
| QuetDungLuong | ❌ Chỉ đọc | Không | — |
| DonRacAnToan | ✅ Tự động | Không | 1–5 GB |
| NenDockerVHDX | ✅ Tự động | **Có** | 1–10 GB |
| PhanTichChrome | ⚠️ Hỏi trước | Không | 2–10 GB |
