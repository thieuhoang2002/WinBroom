<div align="center">

# 🧹 WinBroom

**Bộ công cụ dọn dẹp & tối ưu hóa Windows — không cần cài thêm phần mềm**

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?logo=windows)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Language](https://img.shields.io/badge/Language-VI%20%7C%20EN-orange)](#)

*A lightweight Windows cleanup & optimization toolkit — no third-party software required*

</div>

---

## 📋 Mục lục / Table of Contents

- [Tổng quan](#-tổng-quan)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Danh sách công cụ](#-danh-sách-công-cụ)
- [Cách dùng nhanh](#-cách-dùng-nhanh)
- [Câu hỏi thường gặp](#-câu-hỏi-thường-gặp)
- [Lưu ý an toàn](#️-lưu-ý-an-toàn)

---

## 🔍 Tổng quan

**WinBroom** là bộ công cụ nhẹ, không cài đặt, chạy trực tiếp bằng file `.bat` và Python để:

- 📊 **Phân tích** dung lượng ổ đĩa — tìm ra file/thư mục nặng nhất
- 🗑️ **Dọn rác** an toàn — Temp, npm cache, cache dev tools
- 🐳 **Tối ưu Docker** — nén VHDX để lấy lại dung lượng trống
- 🌐 **Phân tích Chrome** — xem & xóa profile không dùng một cách an toàn

> Tất cả công cụ đều **không xóa dữ liệu cá nhân** mà không có xác nhận rõ ràng từ người dùng.

---

## 💻 Yêu cầu hệ thống

| Yêu cầu | Chi tiết |
|---|---|
| Hệ điều hành | Windows 10 / 11 (64-bit) |
| Python | 3.8 trở lên — [tải tại python.org](https://python.org) hoặc Microsoft Store |
| Thư viện Python | **Không cần** — chỉ dùng thư viện chuẩn |
| Quyền hạn | Một số tool cần **Run as Administrator** (có ghi chú rõ) |

---

## 🧰 Danh sách công cụ

| File | Mô tả ngắn | Cần Admin? |
|---|---|---|
| 🔍 [`QuetDungLuong.bat`](QuetDungLuong.bat) | Quét & phân tích dung lượng toàn bộ ổ đĩa | Không bắt buộc |
| 🗑️ [`DonRacAnToan.bat`](DonRacAnToan.bat) | Xóa Temp, npm cache, .cache, installer cũ | Không |
| 🐳 [`NenDockerVHDX.bat`](NenDockerVHDX.bat) | Nén file VHDX của Docker để lấy lại dung lượng | **Có** |
| 🌐 [`PhanTichChrome.bat`](PhanTichChrome.bat) | Phân tích Chrome profiles — xem account & dung lượng | Không |

> Chi tiết từng công cụ xem tại [`TOOLS.md`](TOOLS.md)

---

## ⚡ Cách dùng nhanh

### Bước 1 — Tải về
```
# Clone repo
git clone https://github.com/<your-username>/winbroom.git

# Hoặc tải ZIP rồi giải nén vào Desktop
```

### Bước 2 — Chạy công cụ muốn dùng
**Cách đơn giản nhất:** Double-click vào file `.bat` tương ứng.

**Cần Admin:** Chuột phải vào file `.bat` → chọn **"Run as administrator"**

> ⚠️ Xem [`TOOLS.md`](TOOLS.md) để biết tool nào cần quyền Admin trước khi chạy.

---

## ❓ Câu hỏi thường gặp

**Q: Python không tìm thấy / lỗi "python is not recognized"?**  
A: Cài Python từ [python.org](https://python.org) và nhớ tick ✅ **"Add Python to PATH"** lúc cài.

**Q: Các file `.bat` có an toàn không?**  
A: Mã nguồn hoàn toàn mở — bạn có thể click chuột phải → Edit để đọc từng dòng lệnh trước khi chạy.

**Q: Chạy xong máy có cần restart không?**  
A: Thường thì không. Riêng `NenDockerVHDX.bat` cần tắt Docker Desktop trước khi chạy.

---

## 🛡️ Lưu ý an toàn

- ✅ Không có tool nào tự động xóa file mà **không hỏi xác nhận** (trừ `DonRacAnToan.bat` — nhưng chỉ xóa file rác hệ thống đã được kiểm chứng an toàn)
- ✅ Không kết nối internet, không thu thập dữ liệu
- ✅ Không chỉnh sửa Registry hay cài dịch vụ nền
- ❌ **Không chỉnh sửa script** nếu bạn không chắc về lệnh đang thêm vào

---

## 📄 License

MIT License — xem [`LICENSE`](LICENSE)
