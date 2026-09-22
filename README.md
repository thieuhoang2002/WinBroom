<div align="center">

# 🧹 WinBroom

**Bộ công cụ dọn dẹp & tối ưu hóa Windows — không cần cài thêm phần mềm**

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?logo=windows)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

*A lightweight Windows cleanup & optimization toolkit — no third-party software required*

</div>

---

## 📋 Mục lục

- [Tổng quan](#-tổng-quan)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Danh sách công cụ](#-danh-sách-công-cụ)
- [Cách dùng nhanh](#-cách-dùng-nhanh)
- [Lưu ý an toàn](#️-lưu-ý-an-toàn)

---

## 🔍 Tổng quan

**WinBroom** là bộ công cụ nhẹ, không cài đặt, chạy trực tiếp bằng file `.bat` và Python để:

- 📊 **Phân tích** dung lượng ổ đĩa — tìm file/thư mục nặng nhất
- 🗑️ **Dọn rác** an toàn — Temp, npm cache, cache dev tools
- 🌐 **Phân tích Chrome** — xem account & dung lượng từng profile, xóa an toàn
- 🐳 **Tối ưu Docker** — nén VHDX lấy lại dung lượng mà không mất image
- ❌ **Tắt Chrome** — kill toàn bộ tiến trình nền Chrome ngay lập tức

> Tất cả công cụ đều **không xóa dữ liệu cá nhân** mà không có xác nhận rõ ràng.

---

## 💻 Yêu cầu hệ thống

| Yêu cầu | Chi tiết |
|---|---|
| Hệ điều hành | Windows 10 / 11 (64-bit) |
| Python | 3.8+ — [tải tại python.org](https://python.org) hoặc Microsoft Store |
| Thư viện ngoài | **Không cần** — chỉ dùng thư viện chuẩn |
| Quyền hạn | Một số tool cần **Run as Administrator** (ghi chú rõ bên dưới) |

---

## 📁 Cấu trúc dự án

```
WinBroom/
├── DonRacAnToan.bat        # Dọn Temp, npm cache, dev cache
├── NenDockerVHDX.bat       # Nén VHDX Docker (cần Admin)
├── PhanTichChrome.bat      # Phân tích & dọn Chrome profiles
├── QuetDungLuong.bat       # Quét & phân tích dung lượng ổ đĩa
├── TatChrome.bat           # Tắt toàn bộ tiến trình Chrome
│
├── src/                    # Mã nguồn Python & PowerShell
│   ├── disk_analyzer.py
│   ├── NenDockerVHDX.ps1
│   └── PhanTichChrome.py
│
├── docs/                   # Tài liệu chi tiết
│   ├── TOOLS.md
│   └── CHANGELOG.md
│
├── README.md
├── LICENSE
└── .gitignore
```

> **Cách dùng:** Double-click file `.bat` tương ứng — các file trong `src/` và `docs/` không cần mở trực tiếp.

---

## 🧰 Danh sách công cụ

| File | Mô tả | Cần Admin? |
|---|---|---|
| 🔍 [`QuetDungLuong.bat`](QuetDungLuong.bat) | Quét ổ đĩa, xuất báo cáo HTML dashboard | Không bắt buộc |
| 🗑️ [`DonRacAnToan.bat`](DonRacAnToan.bat) | Xóa Temp, npm cache, dev cache tự động | Không |
| ❌ [`TatChrome.bat`](TatChrome.bat) | Kill toàn bộ tiến trình Chrome chạy ngầm | Không |
| 🧹 [`XoaCacheChrome.bat`](XoaCacheChrome.bat) | Xóa cache Chrome — giữ nguyên tài khoản, mật khẩu, bookmark | Không |
| 🌐 [`PhanTichChrome.bat`](PhanTichChrome.bat) | Xem account/dung lượng Chrome profiles, xóa có xác nhận | Không |
| 🐳 [`NenDockerVHDX.bat`](NenDockerVHDX.bat) | Nén VHDX Docker để lấy lại dung lượng | **Có** |

📖 Chi tiết từng công cụ: [`docs/TOOLS.md`](docs/TOOLS.md)

---

## ⚡ Cách dùng nhanh

**Bước 1 — Tải về:**
```bash
git clone https://github.com/<your-username>/winbroom.git
```
Hoặc tải ZIP → giải nén vào Desktop.

**Bước 2 — Chạy tool:**
- **Thông thường:** Double-click file `.bat`
- **Cần Admin:** Chuột phải → **"Run as administrator"**

**Gợi ý thứ tự dọn dẹp lần đầu:**
```
1. QuetDungLuong.bat    → Xem máy đang dùng bao nhiêu GB ở đâu
2. DonRacAnToan.bat     → Dọn rác tự động trước
3. TatChrome.bat        → Tắt Chrome nền
4. XoaCacheChrome.bat   → Xóa cache Chrome (giữ nguyên tài khoản)
5. PhanTichChrome.bat   → Xem & xóa Chrome profile không dùng
6. NenDockerVHDX.bat    → Nén Docker nếu đã xóa image (cần Admin)
```

---

## 🛡️ Lưu ý an toàn

- ✅ Không kết nối internet, không thu thập dữ liệu
- ✅ Không chỉnh sửa Registry hay cài dịch vụ nền
- ✅ Mã nguồn mở — đọc từng dòng lệnh bằng cách chuột phải → Edit
- ⚠️ `DonRacAnToan.bat` xóa tự động (không hỏi) — chỉ nhắm vào file rác hệ thống đã kiểm chứng
- ⚠️ `TatChrome.bat` đóng toàn bộ Chrome — download dang dở sẽ bị ngắt

---

## 📄 License

[MIT License](LICENSE)
