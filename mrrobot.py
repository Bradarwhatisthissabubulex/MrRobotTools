"""MrRobotTools - main entry point. Run: python mrrobot.py"""

import os
import sys
import time

# Make sibling packages importable
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from core.colors import (
    GREEN, DARK_GREEN, BRIGHT_GREEN, RED, YELLOW, CYAN, GREY, BOLD, RESET, hr,
    prompt, print_section, print_tool, print_info, print_ok, print_warn, print_err,
)
from core.banner import show_banner, render_screen
from core.auth import require_authorization


# Auto-install missing deps (beautifulsoup4, python-whois).
# No requests/urllib3 needed - we use stdlib urllib via core/http.py.
def _ensure_deps():
    missing = []
    try:
        import bs4  # noqa
    except ImportError:
        missing.append("beautifulsoup4")
    try:
        import whois  # noqa
    except ImportError:
        missing.append("python-whois")
    if not missing:
        return
    print(f"{YELLOW}[!]{RESET} Missing dependencies: {', '.join(missing)}")
    print(f"{CYAN}[i]{RESET} Auto-installing via pip (one-time)...")
    import subprocess
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + missing,
            stdout=subprocess.DEVNULL if os.name == "nt" else None,
            stderr=subprocess.STDOUT,
        )
        print(f"{GREEN}[+]{RESET} Dependencies installed. Continuing...\n")
    except Exception as e:
        print(f"{RED}[-]{RESET} Auto-install failed: {e}")
        print(f"\n{YELLOW}[!]{RESET} Install manually:\n    pip install {' '.join(missing)}\n")
        sys.exit(1)


_ensure_deps()


# Import tool modules - show friendly fix message if a dep is broken.
try:
    from modules.pentesting import (
        advanced_scanner,
        vulnerability_scanner,
        port_scanner,
        url_crawler,
        pinger,
        host_discovery,
    )
    from modules.osint import (
        dorking,
        wallet_tracker,
        username_tracker,
        email_tracker,
        email_lookup,
        ip_lookup,
        phone_lookup,
        instagram_lookup,
    )
    from modules.utils import (
        metadata_scanner,
        metadata_deleter,
        website_cloner,
    )
except ImportError as _e:
    print(f"\n{RED}[-]{RESET} Dependency error: {_e}\n")
    print(f"{YELLOW}[!]{RESET} A required Python package is missing or broken.")
    print(f"{GREEN}[+]{RESET} Fix by running:\n")
    print(f"    {sys.executable} -m pip install beautifulsoup4 python-whois Pillow exifread\n")
    print(f"    Then re-run this script.\n")
    sys.exit(1)


VERSION = "1.0.0"
AUTHOR = "MrRobotTools (clean rebuild)"

# (number, name, module, description)
PENTESTING = [
    (1, "Advanced Scanner",       advanced_scanner,   "Ping + ports + banners + HTTP fingerprint"),
    (2, "Vuln Scanner",           vulnerability_scanner, "Passive misconfig & header checks"),
    (3, "Port Scanner",           port_scanner,       "Multithreaded TCP port scan"),
    (4, "URL Discovery Crawler",  url_crawler,        "BFS crawl of internal links"),
    (5, "IP Pinger",              pinger,             "ICMP echo via OS ping"),
    (6, "Host Discovery",         host_discovery,     "Sweep CIDR / range for live hosts"),
]
OSINT = [
    (7,  "Dorking Query Engine",  dorking,            "Generate Google dorks for a domain"),
    (8,  "Wallet Tracker",        wallet_tracker,     "BTC/ETH/LTC/BCH/DOGE wallet info"),
    (9,  "Username Tracker",      username_tracker,   "Check ~40 sites for a username"),
    (10, "Email Tracker",         email_tracker,      "MX + breach + Gravatar check"),
    (11, "Email Lookup",          email_lookup,       "WHOIS + provider + pattern"),
    (12, "IP Lookup",             ip_lookup,          "Geo/ASN/org via ipapi.co"),
    (13, "Phone Lookup",          phone_lookup,       "Country code + carrier heuristic"),
    (14, "Instagram Profile",     instagram_lookup,   "Public profile metadata, no login"),
]
UTILITIES = [
    (15, "Metadata Scanner",      metadata_scanner,   "EXIF / PDF / Office metadata"),
    (16, "Metadata Deleter",      metadata_deleter,   "Strip EXIF + Office core props"),
    (17, "Website Cloner",        website_cloner,     "wget --mirror or single-page clone"),
]

ALL_TOOLS = {t[0]: t for t in (PENTESTING + OSINT + UTILITIES)}


# Column layout helpers
import shutil
import re as _re

COL_WIDTH = 28  # width of each menu column


def _term_width(default=80):
    try:
        return max(shutil.get_terminal_size((default, 24)).columns, 60)
    except Exception:
        return default


def _center_block_line(text):
    """Center a string (which may contain ANSI codes) in the terminal."""
    visible = _re.sub(r"\033\[[0-9;]*m", "", text)
    width = _term_width()
    pad = max(0, (width - len(visible)) // 2)
    return " " * pad + text


def _fmt_tool(num, name):
    """Format a single tool entry for a column: '[01] Name'"""
    return f"{DARK_GREEN}[{num:02d}]{RESET} {GREEN}{name}{RESET}"

def _fmt_header(title, count):
    """Format a column header: '[Pentesting] (6)'"""
    return f"{BOLD}{DARK_GREEN}[{title}]{RESET} {GREY}({count}){RESET}"

def _pad(text, width):
    """Pad a string to `width` visible columns, accounting for ANSI codes."""
    visible = _re.sub(r"\033\[[0-9;]*m", "", text)
    return text + " " * max(0, width - len(visible))


def _print_menu():
    """Print the menu as 3 centered side-by-side columns."""
    print()
    columns = [
        ("Pentesting", PENTESTING),
        ("Osint",      OSINT),
        ("Utilities",  UTILITIES),
    ]

    def _visible_len(s):
        return len(_re.sub(r"\033\[[0-9;]*m", "", s))

    # Build all rows as raw strings (without per-row centering)
    header_cells = [_fmt_header(t, len(items)) for t, items in columns]
    header_line = _pad(header_cells[0], COL_WIDTH) + _pad(header_cells[1], COL_WIDTH) + header_cells[2]
    block_width = _visible_len(header_line)

    rows = [header_line]
    max_rows = max(len(items) for _, items in columns)
    for row in range(max_rows):
        cells = []
        for _, items in columns:
            if row < len(items):
                num, name, _, _ = items[row]
                cells.append(_fmt_tool(num, name))
            else:
                cells.append("")
        line = _pad(cells[0], COL_WIDTH) + _pad(cells[1], COL_WIDTH) + cells[2]
        rows.append(line)

    # Pad every row to block_width, then center the whole block
    pad = max(0, (_term_width() - block_width) // 2)
    left_pad = " " * pad

    print(left_pad + header_line)
    print(left_pad + f"{DARK_GREEN}{'-' * block_width}{RESET}")
    for line in rows[1:]:
        vp = _visible_len(line)
        trailing = " " * max(0, block_width - vp)
        print(left_pad + line + trailing)
    print()
    footer = f"{DARK_GREEN}[99]{RESET} {GREY}Exit{RESET}    {DARK_GREEN}[0]{RESET} {GREY}Refresh{RESET}"
    footer_pad = max(0, (_term_width() - _visible_len(footer)) // 2)
    print(" " * footer_pad + footer)
    print(left_pad + f"{DARK_GREEN}{'-' * block_width}{RESET}")


def _run_tool(num):
    """Run a tool, then wait for Enter to return to menu."""
    if num not in ALL_TOOLS:
        print_err(f"No tool #{num}.")
        time.sleep(1)
        return
    _, name, module, _ = ALL_TOOLS[num]
    render_screen()
    print(f"{CYAN}[i]{RESET} Launching: {BOLD}{name}{RESET}\n")
    try:
        module.run()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!]{RESET} Interrupted.")
    except Exception as e:
        print_err(f"Tool crashed: {type(e).__name__}: {e}")
    print()
    hr(COL_WIDTH * 3 + 2)
    input(f"{GREY}Press Enter to return to menu...{RESET}")


def main():
    # Enable ANSI colors on Windows consoles
    if sys.platform.startswith("win"):
        try:
            os.system("")
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

    # Authorization screen
    def _auth_screen():
        print(f"{GREY}  v{VERSION}  |  {AUTHOR}{RESET}")
        print(f"{GREY}  For authorized security testing & OSINT research only.{RESET}")
        hr()

    render_screen(_auth_screen)
    if not require_authorization():
        sys.exit(1)

    # Main menu loop - clears and reprints banner each iteration
    while True:
        render_screen(_print_menu)
        try:
            choice = input(prompt("~/mrrobot")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{GREY}Goodbye.{RESET}")
            break

        if choice in ("99", "exit", "quit", "q"):
            print(f"{GREEN}[+]{RESET} Goodbye, admin.")
            time.sleep(0.5)
            break
        if choice in ("0", "banner", "refresh", "clear"):
            continue
        if choice == "help":
            print(f"{CYAN}[i]{RESET} Type a tool number (1-17) to run, or '99' to exit.")
            time.sleep(1.5)
            continue

        try:
            num = int(choice)
        except ValueError:
            print_err(f"Unknown command: {choice!r}. Type a number 1-17 or '99'.")
            time.sleep(1.2)
            continue

        _run_tool(num)


if __name__ == "__main__":
    main()
