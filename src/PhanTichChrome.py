import sys
import os
import json
import datetime
import ctypes
import subprocess
import shutil

# ── encoding & console setup ──────────────────────────────────────────────────
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.system('')                                          # enable ANSI on Windows
ctypes.windll.kernel32.SetConsoleTitleW('Phan Tich Chrome Profiles')

# ── ANSI color constants ───────────────────────────────────────────────────────
class C:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'
    DIM     = '\033[2m'

# ── constants ─────────────────────────────────────────────────────────────────
CHROME_USER_DATA = os.path.join(
    os.environ.get('LOCALAPPDATA', ''),
    'Google', 'Chrome', 'User Data'
)
CHROME_EPOCH = datetime.datetime(1601, 1, 1)

# ── helpers ───────────────────────────────────────────────────────────────────

def chrome_time_to_dt(microseconds):
    """Convert Chrome FILETIME (µs since 1601-01-01) to a datetime object."""
    try:
        return CHROME_EPOCH + datetime.timedelta(microseconds=int(microseconds))
    except Exception:
        return None


def folder_size(path):
    """Return total size in bytes of a directory tree (recursive, no exceptions)."""
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        total += folder_size(entry.path)
                    else:
                        total += entry.stat(follow_symlinks=False).st_size
                except (PermissionError, OSError):
                    pass
    except (PermissionError, OSError):
        pass
    return total


def human_size(n):
    """Return a human-readable size string."""
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if n < 1024:
            return f'{n:.1f} {unit}'
        n /= 1024
    return f'{n:.1f} PB'


def is_profile_folder(name):
    """Return True if the folder name looks like a Chrome profile directory."""
    if name == 'Default':
        return True
    if name.startswith('Profile ') and name[8:].isdigit():
        return True
    return False


def read_preferences(profile_path):
    """
    Parse the Preferences JSON file inside *profile_path*.
    Returns a dict with keys: name, email, full_name, last_active_time.
    Missing / corrupt values are returned as None.
    """
    prefs_path = os.path.join(profile_path, 'Preferences')
    result = {
        'name': None,
        'email': None,
        'full_name': None,
        'last_active': None,
    }
    try:
        with open(prefs_path, 'r', encoding='utf-8', errors='replace') as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return result

    # profile.name
    try:
        result['name'] = data['profile']['name']
    except (KeyError, TypeError):
        pass

    # account_info[0].email / full_name
    try:
        accs = data['account_info']
        if accs:
            result['email']     = accs[0].get('email')
            result['full_name'] = accs[0].get('full_name')
    except (KeyError, TypeError, IndexError):
        pass

    # profile.last_active_time
    try:
        lat = data['profile']['last_active_time']
        result['last_active'] = chrome_time_to_dt(lat)
    except (KeyError, TypeError):
        pass

    return result


def check_chrome_running():
    """Return True if any Chrome process is detected via tasklist."""
    try:
        out = subprocess.check_output(
            ['tasklist', '/FI', 'IMAGENAME eq chrome.exe', '/NH'],
            stderr=subprocess.DEVNULL,
            encoding='utf-8',
            errors='replace',
        )
        return 'chrome.exe' in out.lower()
    except Exception:
        return False


def scan_profiles():
    """Scan Chrome User Data and return a list of profile info dicts."""
    profiles = []
    if not os.path.isdir(CHROME_USER_DATA):
        return profiles

    try:
        entries = sorted(os.listdir(CHROME_USER_DATA))
    except OSError:
        return profiles

    for name in entries:
        if not is_profile_folder(name):
            continue
        full_path = os.path.join(CHROME_USER_DATA, name)
        if not os.path.isdir(full_path):
            continue
        prefs = read_preferences(full_path)
        size  = folder_size(full_path)
        profiles.append({
            'folder':      name,
            'path':        full_path,
            'name':        prefs['name'],
            'email':       prefs['email'],
            'full_name':   prefs['full_name'],
            'last_active': prefs['last_active'],
            'size':        size,
        })

    return profiles


# ── display ───────────────────────────────────────────────────────────────────

def fmt_identity(p):
    """Build a compact Name / Email string for the table."""
    parts = []
    if p['name']:
        parts.append(p['name'])
    if p['email']:
        parts.append(p['email'])
    elif p['full_name']:
        parts.append(p['full_name'])
    return ' / '.join(parts) if parts else C.DIM + '(no info)' + C.RESET


def fmt_last_active(dt):
    if dt is None:
        return C.DIM + 'unknown' + C.RESET
    # Filter out sentinel "never used" times (before year 2000)
    if dt.year < 2000:
        return C.DIM + 'never' + C.RESET
    return dt.strftime('%Y-%m-%d  %H:%M')


def fmt_status(p):
    if p['email']:
        return C.GREEN + 'signed-in' + C.RESET
    return C.YELLOW + 'local' + C.RESET


def print_banner():
    print()
    print(C.BOLD + C.CYAN +
          '╔══════════════════════════════════════════════════╗' + C.RESET)
    print(C.BOLD + C.CYAN +
          '║         CHROME PROFILE ANALYZER  v1.0           ║' + C.RESET)
    print(C.BOLD + C.CYAN +
          '╚══════════════════════════════════════════════════╝' + C.RESET)
    print()


def print_table(profiles):
    # column widths (visual, no ANSI codes in measurement)
    W_IDX    = 3
    W_FOLDER = 12
    W_IDENT  = 38
    W_SIZE   = 10
    W_DATE   = 18
    W_STATUS = 10

    sep = (C.DIM + '─' * (W_IDX + W_FOLDER + W_IDENT + W_SIZE + W_DATE + W_STATUS + 13) + C.RESET)

    def header(t, w):
        return (C.BOLD + C.BLUE + t.ljust(w) + C.RESET)

    # header row
    print(sep)
    print(
        ' ' + header('#', W_IDX) +
        ' │ ' + header('Folder', W_FOLDER) +
        ' │ ' + header('Name / Email', W_IDENT) +
        ' │ ' + header('Size', W_SIZE) +
        ' │ ' + header('Last Active', W_DATE) +
        ' │ ' + header('Status', W_STATUS)
    )
    print(sep)

    for idx, p in enumerate(profiles, start=1):
        identity = fmt_identity(p)
        last_act = fmt_last_active(p['last_active'])
        status   = fmt_status(p)
        size_str = human_size(p['size'])

        # strip ANSI for padding calculation
        def visible(s):
            import re
            return re.sub(r'\033\[[0-9;]*m', '', s)

        # pad to column width accounting for invisible ANSI bytes
        def col(s, w):
            pad = w - len(visible(s))
            return s + ' ' * max(pad, 0)

        row_color = C.WHITE if idx % 2 == 0 else ''
        print(
            row_color +
            ' ' + col(str(idx), W_IDX) +
            ' │ ' + col(C.MAGENTA + p['folder'] + C.RESET, W_FOLDER) +
            ' │ ' + col(identity, W_IDENT) +
            ' │ ' + col(C.CYAN + size_str + C.RESET, W_SIZE) +
            ' │ ' + col(last_act, W_DATE) +
            ' │ ' + status +
            C.RESET
        )

    print(sep)
    print()


# ── deletion ──────────────────────────────────────────────────────────────────

def delete_profiles(profiles):
    print(C.BOLD + 'Enter profile numbers to DELETE (comma-separated), or press Enter to skip:' + C.RESET)
    raw = input(C.YELLOW + '  >> ' + C.RESET).strip()

    if not raw:
        print(C.DIM + 'No profiles selected. Exiting.' + C.RESET)
        return

    chosen = []
    for token in raw.split(','):
        token = token.strip()
        if not token.isdigit():
            print(C.RED + f'  Ignoring invalid token: {token!r}' + C.RESET)
            continue
        i = int(token)
        if 1 <= i <= len(profiles):
            chosen.append(profiles[i - 1])
        else:
            print(C.RED + f'  Index {i} out of range.' + C.RESET)

    if not chosen:
        print(C.DIM + 'Nothing to delete.' + C.RESET)
        return

    print()
    print(C.BOLD + C.RED + 'The following profiles will be PERMANENTLY DELETED:' + C.RESET)
    for p in chosen:
        print(f'  {C.MAGENTA}{p["folder"]}{C.RESET}  {p["path"]}')
    print()

    confirm = input(C.BOLD + C.RED + 'Type YES to confirm deletion: ' + C.RESET).strip()
    if confirm != 'YES':
        print(C.YELLOW + 'Deletion cancelled.' + C.RESET)
        return

    for p in chosen:
        try:
            shutil.rmtree(p['path'])
            print(C.GREEN + f'  ✓ Deleted: {p["folder"]}' + C.RESET)
        except Exception as exc:
            print(C.RED + f'  ✗ Failed to delete {p["folder"]}: {exc}' + C.RESET)

    print()


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    print_banner()

    # Chrome running check
    if check_chrome_running():
        print(C.BOLD + C.RED +
              '  ⚠  WARNING: Chrome is currently running!' + C.RESET)
        print(C.YELLOW +
              '     Close Chrome before deleting profiles to avoid data loss.\n' + C.RESET)

    # Chrome User Data directory check
    if not os.path.isdir(CHROME_USER_DATA):
        print(C.RED + f'Chrome User Data folder not found:\n  {CHROME_USER_DATA}' + C.RESET)
        input('\nPress Enter to exit...')
        sys.exit(1)

    print(C.DIM + f'Scanning: {CHROME_USER_DATA}\n' + C.RESET)

    profiles = scan_profiles()

    if not profiles:
        print(C.YELLOW + 'No Chrome profile folders found.' + C.RESET)
        input('\nPress Enter to exit...')
        sys.exit(0)

    total_size = sum(p['size'] for p in profiles)
    print(C.BOLD + f'Found {len(profiles)} profile(s)  —  '
          f'Total size: {human_size(total_size)}' + C.RESET)
    print()

    print_table(profiles)

    delete_profiles(profiles)

    input(C.DIM + 'Press Enter to exit...' + C.RESET)


if __name__ == '__main__':
    main()
