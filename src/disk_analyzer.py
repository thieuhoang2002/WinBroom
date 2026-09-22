#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Disk Space Analyzer (Quét & Phân Tích Dung Lượng Ổ Đĩa)
Tác giả: Antigravity Assistant
Mô tả: Quét toàn bộ ổ đĩa hoặc thư mục, phát hiện file và thư mục chiếm dung lượng lớn nhất,
       thống kê định dạng file, xuất báo cáo HTML trực quan và tự động mở trình duyệt.
"""

import os
import sys
import time
import heapq
import ctypes
import datetime
import webbrowser
from pathlib import Path
from collections import defaultdict

# Thiết lập mã hóa UTF-8 cho console để in tiếng Việt không bị lỗi font hoặc crash charmap
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    os.system("")

class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def format_size(bytes_val):
    """Chuyển đổi số bytes sang định dạng dễ đọc (B, KB, MB, GB, TB)"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if abs(bytes_val) < 1024.0:
            return f"{bytes_val:6.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} EB"

def get_available_drives():
    """Lấy danh sách các ổ đĩa đang hoạt động trên Windows"""
    drives = []
    if sys.platform == "win32":
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in range(65, 91):
            if bitmask & (1 << (letter - 65)):
                drive = f"{chr(letter)}:\\"
                if os.path.exists(drive):
                    try:
                        free_b = ctypes.c_ulonglong(0)
                        total_b = ctypes.c_ulonglong(0)
                        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                            ctypes.c_wchar_p(drive),
                            None,
                            ctypes.byref(total_b),
                            ctypes.byref(free_b)
                        )
                        used_b = total_b.value - free_b.value
                        drives.append({
                            'path': drive,
                            'total': total_b.value,
                            'used': used_b,
                            'free': free_b.value
                        })
                    except Exception:
                        drives.append({'path': drive, 'total': 0, 'used': 0, 'free': 0})
    else:
        drives.append({'path': '/', 'total': 0, 'used': 0, 'free': 0})
    return drives

def is_admin():
    """Kiểm tra quyền Administrator trên Windows"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

class Scanner:
    def __init__(self, target_paths, top_files_count=30, top_dirs_count=30):
        self.target_paths = target_paths
        self.top_files_count = top_files_count
        self.top_dirs_count = top_dirs_count
        self.total_files = 0
        self.total_dirs = 0
        self.total_size = 0
        self.error_count = 0
        self.top_files = []  # min-heap of (size, path, mtime)
        self.dir_sizes = defaultdict(int)
        self.ext_stats = defaultdict(lambda: {'size': 0, 'count': 0})
        self.start_time = 0
        self.elapsed = 0

    def scan(self):
        self.start_time = time.time()
        last_print_time = self.start_time

        print(f"{Colors.CYAN}{Colors.BOLD}Bắt đầu quét dữ liệu... Vui lòng đợi trong giây lát!{Colors.RESET}")
        print(f"{Colors.DIM}(Nhấn Ctrl+C bất kỳ lúc nào để dừng quét và xem kết quả hiện tại){Colors.RESET}\n")

        for root_target in self.target_paths:
            try:
                self._scan_directory(root_target, last_print_time)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}[!] Đã dừng quét theo yêu cầu của bạn. Đang tổng hợp dữ liệu...{Colors.RESET}")
                break

        self.elapsed = time.time() - self.start_time
        # Xóa dòng tiến trình
        print("\r" + " " * 95 + "\r", end="")

    def _scan_directory(self, current_path, last_print_time):
        stack = [current_path]
        dir_child_sizes = defaultdict(int)
        visited_dirs = []

        while stack:
            path = stack.pop()
            visited_dirs.append(path)
            self.total_dirs += 1

            now = time.time()
            if now - last_print_time > 0.3:
                last_print_time = now
                short_path = path if len(path) < 55 else "..." + path[-52:]
                sys.stdout.write(
                    f"\r{Colors.DIM}Đã quét: {self.total_files:,} files | {format_size(self.total_size).strip()} | {short_path:<55}{Colors.RESET}"
                )
                sys.stdout.flush()

            try:
                with os.scandir(path) as it:
                    for entry in it:
                        try:
                            # Bỏ qua reparse points / symlinks để tránh vòng lặp
                            if entry.is_symlink():
                                continue
                            
                            if entry.is_file(follow_symlinks=False):
                                try:
                                    stat = entry.stat(follow_symlinks=False)
                                    size = stat.st_size
                                    mtime = stat.st_mtime
                                except (PermissionError, FileNotFoundError, OSError):
                                    continue

                                self.total_files += 1
                                self.total_size += size
                                dir_child_sizes[path] += size

                                # Lưu extension stats
                                ext = Path(entry.name).suffix.lower()
                                if not ext:
                                    ext = "[không đuôi]"
                                self.ext_stats[ext]['size'] += size
                                self.ext_stats[ext]['count'] += 1

                                # Min-heap cho top files
                                file_info = (size, entry.path, mtime)
                                if len(self.top_files) < self.top_files_count:
                                    heapq.heappush(self.top_files, file_info)
                                else:
                                    if size > self.top_files[0][0]:
                                        heapq.heappushpop(self.top_files, file_info)

                            elif entry.is_dir(follow_symlinks=False):
                                stack.append(entry.path)

                        except (PermissionError, FileNotFoundError, OSError):
                            self.error_count += 1
                            continue

            except (PermissionError, FileNotFoundError, OSError):
                self.error_count += 1
                continue

        # Tính tổng kích thước cho từng thư mục (bao gồm cả thư mục con)
        # Sắp xếp các thư mục từ sâu nhất đến nông nhất
        for d in reversed(visited_dirs):
            self.dir_sizes[d] += dir_child_sizes[d]
            parent = os.path.dirname(d)
            if parent and parent != d:
                dir_child_sizes[parent] += self.dir_sizes[d]

    def get_top_files(self):
        return sorted(self.top_files, key=lambda x: x[0], reverse=True)

    def get_top_dirs(self):
        # Lọc bớt các thư mục gốc quá tổng quát nếu cần, lấy top dung lượng lớn nhất
        sorted_dirs = sorted(self.dir_sizes.items(), key=lambda x: x[1], reverse=True)
        return sorted_dirs[:self.top_dirs_count]

    def get_top_extensions(self, limit=15):
        return sorted(self.ext_stats.items(), key=lambda x: x[1]['size'], reverse=True)[:limit]

def display_cli_summary(scanner):
    print("=" * 80)
    print(f"{Colors.GREEN}{Colors.BOLD}   KẾT QUẢ QUÉT DUNG LƯỢNG CHI TIẾT   {Colors.RESET}")
    print("=" * 80)
    print(f" • Tổng dung lượng quét được : {Colors.YELLOW}{Colors.BOLD}{format_size(scanner.total_size)}{Colors.RESET}")
    print(f" • Tổng số file              : {Colors.CYAN}{scanner.total_files:,}{Colors.RESET}")
    print(f" • Tổng số thư mục           : {Colors.CYAN}{scanner.total_dirs:,}{Colors.RESET}")
    print(f" • Thời gian quét            : {scanner.elapsed:.1f} giây ({scanner.total_files / max(scanner.elapsed, 0.001):.0f} files/s)")
    if scanner.error_count > 0:
        print(f" • Thư mục bị chặn quyền     : {Colors.RED}{scanner.error_count:,}{Colors.RESET} (Chạy Run as Admin để quét sâu hơn)")
    print("-" * 80)

    # 1. TOP FILES
    print(f"\n{Colors.RED}{Colors.BOLD}▶ TOP {min(len(scanner.top_files), 15)} FILE NẶNG NHẤT TRÊN MÁY:{Colors.RESET}")
    print(f"{'Dung lượng':<12} | {'Ngày sửa đổi':<12} | {'Đường dẫn file'}")
    print("-" * 80)
    for size, path, mtime in scanner.get_top_files()[:15]:
        mdate = datetime.datetime.fromtimestamp(mtime).strftime("%d/%m/%Y")
        size_str = format_size(size).strip()
        print(f"{Colors.YELLOW}{size_str:<12}{Colors.RESET} | {mdate:<12} | {path}")

    # 2. TOP DIRECTORIES
    print(f"\n{Colors.BLUE}{Colors.BOLD}▶ TOP {min(len(scanner.dir_sizes), 15)} THƯ MỤC NẶNG NHẤT (ĐÃ GỒM THƯ MỤC CON):{Colors.RESET}")
    print(f"{'Dung lượng':<12} | {'Tỉ lệ':<7} | {'Đường dẫn thư mục'}")
    print("-" * 80)
    for path, size in scanner.get_top_dirs()[:15]:
        ratio = (size / scanner.total_size * 100) if scanner.total_size > 0 else 0
        size_str = format_size(size).strip()
        print(f"{Colors.CYAN}{size_str:<12}{Colors.RESET} | {ratio:5.1f}% | {path}")

    # 3. TOP FILE EXTENSIONS
    print(f"\n{Colors.GREEN}{Colors.BOLD}▶ PHÂN LOẠI THEO ĐỊNH DẠNG FILE (EXTENSIONS):{Colors.RESET}")
    print(f"{'Định dạng':<12} | {'Tổng dung lượng':<16} | {'Số lượng file':<15} | {'Tỉ lệ'}")
    print("-" * 80)
    for ext, data in scanner.get_top_extensions(10):
        ratio = (data['size'] / scanner.total_size * 100) if scanner.total_size > 0 else 0
        size_str = format_size(data['size']).strip()
        print(f"{Colors.BOLD}{ext:<12}{Colors.RESET} | {size_str:<16} | {data['count']:<15,} | {ratio:5.1f}%")
    print("=" * 80)

def generate_html_report(scanner, output_path):
    top_files = scanner.get_top_files()
    top_dirs = scanner.get_top_dirs()
    top_exts = scanner.get_top_extensions(15)

    def escape_html(text):
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    files_rows = ""
    for idx, (size, path, mtime) in enumerate(top_files, 1):
        mdate = datetime.datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M")
        size_str = format_size(size).strip()
        parent_dir = os.path.dirname(path)
        safe_path = escape_html(path)
        files_rows += f"""
        <tr>
            <td style="text-align: center; font-weight: bold; color: #888;">{idx}</td>
            <td style="color: #ffb74d; font-weight: bold; white-space: nowrap;">{size_str}</td>
            <td style="white-space: nowrap; color: #aaa;">{mdate}</td>
            <td class="code-cell" onclick="copyText('{safe_path.replace(chr(92), '/')}')" title="Click để sao chép đường dẫn">
                <span class="filename">{escape_html(os.path.basename(path))} <button class="copy-btn" title="Sao chép đường dẫn">📋</button></span>
                <span class="filedir">{escape_html(parent_dir)}</span>
            </td>
        </tr>"""

    dirs_rows = ""
    for idx, (path, size) in enumerate(top_dirs, 1):
        size_str = format_size(size).strip()
        ratio = (size / scanner.total_size * 100) if scanner.total_size > 0 else 0
        safe_path = escape_html(path)
        dirs_rows += f"""
        <tr>
            <td style="text-align: center; font-weight: bold; color: #888;">{idx}</td>
            <td style="color: #64b5f6; font-weight: bold; white-space: nowrap;">{size_str}</td>
            <td style="width: 140px;">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {min(ratio, 100):.1f}%;"></div>
                </div>
                <span style="font-size: 11px; color: #888;">{ratio:.1f}%</span>
            </td>
            <td class="code-cell" onclick="copyText('{safe_path.replace(chr(92), '/')}')" title="Click để sao chép đường dẫn">
                {safe_path} <button class="copy-btn" title="Sao chép đường dẫn">📋</button>
            </td>
        </tr>"""

    ext_bars = ""
    for ext, data in top_exts:
        size_str = format_size(data['size']).strip()
        ratio = (data['size'] / scanner.total_size * 100) if scanner.total_size > 0 else 0
        ext_bars += f"""
        <div class="ext-item">
            <div class="ext-header">
                <span class="ext-tag">{escape_html(ext)}</span>
                <span class="ext-count">{data['count']:,} files</span>
                <span class="ext-size">{size_str} ({ratio:.1f}%)</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill ext-fill" style="width: {min(ratio, 100):.1f}%;"></div>
            </div>
        </div>"""

    now_str = datetime.datetime.now().strftime("%d/%m/%Y lúc %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo Cáo Phân Tích Dung Lượng Ổ Đĩa</title>
    <style>
        :root {{
            --bg: #12141a;
            --surface: #1a1d26;
            --surface-hover: #222634;
            --border: #2c3144;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --secondary: #a855f7;
            --warning: #f59e0b;
            --danger: #ef4444;
            --success: #10b981;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            padding: 24px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        h1 {{ font-size: 26px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 10px; }}
        .badge {{ background: #0284c7; color: white; padding: 4px 10px; border-radius: 9999px; font-size: 12px; }}
        .header-meta {{ color: var(--text-muted); font-size: 13px; text-align: right; }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
        }}
        .stat-card .label {{ color: var(--text-muted); font-size: 13px; margin-bottom: 6px; }}
        .stat-card .value {{ font-size: 24px; font-weight: 700; color: #fff; }}
        .stat-card.c-primary .value {{ color: var(--primary); }}
        .stat-card.c-warning .value {{ color: var(--warning); }}
        .stat-card.c-success .value {{ color: var(--success); }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}
        @media (max-width: 1024px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
        
        .panel {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }}
        .panel-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .search-box {{
            background: var(--bg);
            border: 1px solid var(--border);
            color: #fff;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            outline: none;
            width: 250px;
        }}
        .search-box:focus {{ border-color: var(--primary); }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            text-align: left;
            padding: 10px 12px;
            background: rgba(255,255,255,0.02);
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
        }}
        tr:hover td {{ background: var(--surface-hover); }}
        .code-cell {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            word-break: break-all;
            max-width: 500px;
        }}
        .filename {{ display: block; font-weight: 600; color: #f1f5f9; }}
        .filedir {{ display: block; font-size: 11px; color: var(--text-muted); margin-top: 2px; }}
        
        .progress-bar {{
            background: rgba(255,255,255,0.06);
            border-radius: 6px;
            height: 8px;
            overflow: hidden;
            margin-bottom: 4px;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            height: 100%;
            border-radius: 6px;
        }}
        .ext-fill {{
            background: linear-gradient(90deg, #34d399, #10b981);
        }}
        .ext-item {{ margin-bottom: 14px; }}
        .ext-header {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 4px; }}
        .ext-tag {{ font-weight: 700; color: #34d399; font-family: monospace; }}
        .ext-count {{ color: var(--text-muted); }}
        .ext-size {{ font-weight: 600; color: #fff; }}
        
        .tip-box {{
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 10px;
            padding: 16px;
            margin-top: 20px;
        }}
        .tip-title {{ font-weight: 700; color: var(--warning); margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }}
        .tip-box ul {{ padding-left: 20px; font-size: 13px; color: #cbd5e1; }}
        .tip-box li {{ margin-bottom: 6px; }}

        .code-cell {{ cursor: pointer; }}
        .copy-btn {{
            background: none;
            border: none;
            cursor: pointer;
            font-size: 13px;
            opacity: 0.6;
            margin-left: 4px;
            vertical-align: middle;
        }}
        .copy-btn:hover {{ opacity: 1; }}

        #toast {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #10b981;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5);
            font-size: 14px;
            font-weight: 600;
            display: none;
            z-index: 9999;
            transition: all 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>💾 Báo Cáo Phân Tích Dung Lượng Ổ Đĩa <span class="badge">Vip Pro</span></h1>
                <p style="color: var(--text-muted); font-size: 14px; margin-top: 4px;">Khám phá các thư mục & tệp tin ngốn dung lượng nhiều nhất trên máy tính</p>
            </div>
            <div class="header-meta">
                Thời gian tạo: <strong>{now_str}</strong><br>
                Thời gian quét: <strong>{scanner.elapsed:.1f}s</strong> | Quét được: <strong>{scanner.total_files:,} files</strong>
            </div>
        </header>

        <div class="stat-grid">
            <div class="stat-card c-warning">
                <div class="label">TỔNG DUNG LƯỢNG QUÉT</div>
                <div class="value">{format_size(scanner.total_size)}</div>
            </div>
            <div class="stat-card c-primary">
                <div class="label">TỔNG SỐ TỆP TIN</div>
                <div class="value">{scanner.total_files:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">TỔNG SỐ THƯ MỤC</div>
                <div class="value">{scanner.total_dirs:,}</div>
            </div>
            <div class="stat-card c-success">
                <div class="label">FILE LỚN NHẤT</div>
                <div class="value">{format_size(top_files[0][0]) if top_files else '0 B'}</div>
            </div>
        </div>

        <div class="grid-2">
            <!-- TOP DIRECTORIES -->
            <div class="panel">
                <div class="panel-title">
                    <span>📁 Top Thư Mục Chiếm Nhiều Dung Lượng Nhất</span>
                    <input type="text" class="search-box" id="searchDirs" placeholder="Tìm kiếm thư mục..." onkeyup="filterTable('dirsTable', this.value)">
                </div>
                <div style="overflow-x: auto;">
                    <table id="dirsTable">
                        <thead>
                            <tr>
                                <th style="width: 40px; text-align: center;">#</th>
                                <th>Dung Lượng</th>
                                <th>Chiếm Tỉ Lệ</th>
                                <th>Đường Dẫn Thư Mục</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dirs_rows}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- EXTENSION STATS -->
            <div class="panel">
                <div class="panel-title">
                    <span>🏷️ Phân Loại Theo Định Dạng File</span>
                </div>
                <div>
                    {ext_bars}
                </div>

                <div class="tip-box">
                    <div class="tip-title">⚡ Mẹo giải phóng dung lượng nhanh:</div>
                    <ul>
                        <li><b>File nén (.zip, .rar, .iso, .7z):</b> Thường là file cài đặt hoặc backup cũ đã tải về nhưng không dùng đến.</li>
                        <li><b>File video (.mp4, .mkv):</b> Chiếm nhiều GB nhất, hãy kiểm tra thư mục <i>Videos</i> và <i>Downloads</i>.</li>
                        <li><b>File ảo hóa/Docker (.vmdk, .vhdx, .iso):</b> Nếu có dùng máy ảo WSL2 hoặc Docker, ổ ảo có thể phình to hàng chục GB.</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- TOP FILES -->
        <div class="panel">
            <div class="panel-title">
                <span>📄 Top File Nặng Nhất Cần Xem Xét Dọn Dẹp</span>
                <input type="text" class="search-box" id="searchFiles" placeholder="Tìm file, đuôi file..." onkeyup="filterTable('filesTable', this.value)">
            </div>
            <div style="overflow-x: auto;">
                <table id="filesTable">
                    <thead>
                        <tr>
                            <th style="width: 40px; text-align: center;">#</th>
                            <th>Kích Thước</th>
                            <th>Ngày Sửa Đổi</th>
                            <th>Đường Dẫn Tệp Tin</th>
                        </tr>
                    </thead>
                    <tbody>
                        {files_rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div id="toast">✔ Đã sao chép đường dẫn vào bộ nhớ tạm!</div>

    <script>
        function filterTable(tableId, query) {{
            query = query.toLowerCase();
            const rows = document.querySelectorAll('#' + tableId + ' tbody tr');
            rows.forEach(row => {{
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            }});
        }}

        function copyText(text) {{
            // Chuẩn hóa dấu gạch chéo Windows
            const formatted = text.split('/').join('\\\\');
            navigator.clipboard.writeText(formatted).then(() => {{
                const toast = document.getElementById('toast');
                toast.style.display = 'block';
                setTimeout(() => {{
                    toast.style.display = 'none';
                }}, 2500);
            }}).catch(err => {{
                console.error('Không thể sao chép: ', err);
            }});
        }}
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

def print_banner():
    print(Colors.CYAN + Colors.BOLD + """
 ╔═══════════════════════════════════════════════════════════════════════╗
 ║                DISK SPACE ANALYZER - QUÉT DUNG LƯỢNG VIP PRO          ║
 ║           Phát hiện thư mục & file chiếm nhiều bộ nhớ nhất            ║
 ╚═══════════════════════════════════════════════════════════════════════╝
""" + Colors.RESET)

def main():
    print_banner()

    admin_status = is_admin()
    if admin_status:
        print(f" {Colors.GREEN}[✓] Đang chạy với quyền Administrator (Toàn quyền quét hệ thống){Colors.RESET}\n")
    else:
        print(f" {Colors.YELLOW}[!] Chạy thường (Không có quyền Admin). Một số thư mục hệ thống có thể bị chặn.{Colors.RESET}")
        print(f"     {Colors.DIM}Để quét toàn diện hơn, bạn có thể chạy file QuetDungLuong.bat (Run as Administrator){Colors.RESET}\n")

    drives = get_available_drives()

    print(f"{Colors.BOLD}Danh sách ổ đĩa trên máy tính:{Colors.RESET}")
    for idx, d in enumerate(drives, 1):
        if d['total'] > 0:
            used_gb = d['used'] / (1024**3)
            total_gb = d['total'] / (1024**3)
            free_gb = d['free'] / (1024**3)
            percent = (d['used'] / d['total']) * 100
            print(f"  [{idx}] Ổ {Colors.BOLD}{d['path']}{Colors.RESET} - Đã dùng: {used_gb:.1f}/{total_gb:.1f} GB ({percent:.1f}%) | Trống: {Colors.GREEN}{free_gb:.1f} GB{Colors.RESET}")
        else:
            print(f"  [{idx}] Ổ {Colors.BOLD}{d['path']}{Colors.RESET}")

    user_profile = os.environ.get("USERPROFILE", "C:\\Users")
    print(f"  [U] Thư mục cá nhân người dùng ({user_profile})")
    print(f"  [A] Quét TẤT CẢ các ổ đĩa trên máy")
    print(f"  [C] Nhập đường dẫn thư mục bất kỳ để quét (Custom Path)")
    print(f"  [Q] Thoát chương trình\n")

    choice = input(f"{Colors.YELLOW}Chọn mục tiêu muốn quét [1-{len(drives)} / U / A / C / Q] (Mặc định: 1): {Colors.RESET}").strip().upper()

    targets = []
    if choice == "Q":
        print("Tạm biệt!")
        return
    elif choice == "A":
        targets = [d['path'] for d in drives]
    elif choice == "U":
        targets = [user_profile]
    elif choice == "C":
        custom = input("Nhập đường dẫn thư mục cần quét (hoặc kéo thả folder vào đây): ").strip().strip('"').strip("'")
        if os.path.exists(custom):
            targets = [custom]
        else:
            print(f"{Colors.RED}Đường dẫn không tồn tại! Thoát.{Colors.RESET}")
            return
    elif choice == "" or choice == "1":
        targets = [drives[0]['path']]
    elif choice.isdigit() and 1 <= int(choice) <= len(drives):
        targets = [drives[int(choice) - 1]['path']]
    else:
        print(f"{Colors.RED}Lựa chọn không hợp lệ! Mặc định quét ổ đầu tiên: {drives[0]['path']}{Colors.RESET}")
        targets = [drives[0]['path']]

    print(f"\n Mục tiêu quét: {Colors.BOLD}{', '.join(targets)}{Colors.RESET}\n")

    scanner = Scanner(targets, top_files_count=35, top_dirs_count=35)
    scanner.scan()

    if scanner.total_files == 0:
        print(f"{Colors.YELLOW}Không tìm thấy file nào hoặc không đủ quyền truy cập.{Colors.RESET}")
        return

    # Hiển thị trên màn hình console
    display_cli_summary(scanner)

    # Xuất báo cáo HTML
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_file = os.path.join(script_dir, "BaoCao_DungLuong.html")
    generate_html_report(scanner, report_file)

    print(f"\n{Colors.GREEN}{Colors.BOLD}✔ Đã tạo báo cáo trực quan dạng Web tại:{Colors.RESET}")
    print(f"  👉 {report_file}")

    open_web = input(f"\n{Colors.CYAN}Bạn có muốn tự động mở báo cáo trên trình duyệt ngay bây giờ không? (Y/n): {Colors.RESET}").strip().lower()
    if open_web in ["", "y", "yes", "có", "c"]:
        webbrowser.open(f"file:///{os.path.abspath(report_file).replace(os.sep, '/')}")
        print(f"{Colors.GREEN}Đã mở báo cáo trên trình duyệt của bạn!{Colors.RESET}")

    input(f"\n{Colors.DIM}Nhấn phím Enter để kết thúc chương trình...{Colors.RESET}")

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            ctypes.windll.kernel32.SetConsoleTitleW("VIP PRO - Quét & Phân Tích Dung Lượng Ổ Đĩa")
        except Exception:
            pass
    main()
