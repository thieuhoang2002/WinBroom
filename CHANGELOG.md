# Changelog

Tất cả thay đổi đáng chú ý của dự án WinBroom được ghi lại tại đây.

---

## [1.0.0] — 2026-09-22

### ✨ Ra mắt lần đầu

#### Thêm mới
- **`QuetDungLuong.bat` + `disk_analyzer.py`**
  - Quét dung lượng ổ đĩa tốc độ cao bằng `os.scandir`
  - Hiển thị top file/thư mục nặng nhất theo dung lượng thực tế
  - Phân loại dung lượng theo định dạng file (extension)
  - Xuất báo cáo HTML Dashboard Dark Mode tự động mở trình duyệt
  - Click vào đường dẫn trong báo cáo để copy vào clipboard
  - Hỗ trợ chọn ổ đĩa, thư mục tùy chỉnh, quét tất cả ổ cùng lúc
  - Có thể dừng bằng Ctrl+C bất kỳ lúc nào mà không mất dữ liệu đã quét

- **`DonRacAnToan.bat`**
  - Tự động xóa thư mục `%TEMP%` và tạo lại
  - Xóa npm cache (`AppData\Local\npm-cache`)
  - Xóa dev tools cache (`%USERPROFILE%\.cache`)
  - Xóa Docker Desktop Installer cũ trong Downloads (nếu có)
  - In trạng thái OK / SKIP rõ ràng cho từng mục

- **`NenDockerVHDX.bat` + `NenDockerVHDX.ps1`**
  - Tự động xin quyền Administrator nếu chưa có
  - Dừng WSL2 (`wsl --shutdown`) trước khi nén
  - Dùng `diskpart compact vdisk` để nén file `.vhdx`
  - Fallback sang `Optimize-VHD` nếu diskpart không thành công
  - Hiển thị dung lượng trước/sau và GB đã thu hồi

- **`PhanTichChrome.bat` + `PhanTichChrome.py`**
  - Đọc `Preferences` JSON của từng Chrome profile
  - Hiển thị tên tài khoản, email, dung lượng, lần dùng cuối
  - Cảnh báo nếu Chrome đang chạy
  - Cho phép chọn và xóa profile theo số thứ tự, có xác nhận trước khi xóa
