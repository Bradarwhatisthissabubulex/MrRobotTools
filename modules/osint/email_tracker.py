"""[10] Email Tracker - MX, breach check (HIBP), and Gravatar lookup."""

import re
import socket

from core import http as requests

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _check_mx(domain):
    """Get MX records via nslookup."""
    try:
        import subprocess
        r = subprocess.run(["nslookup", "-type=mx", domain], capture_output=True, text=True, timeout=8)
        out = r.stdout + r.stderr
        if "mail exchanger" in out.lower():
            return [l.strip() for l in out.splitlines() if "mail exchanger" in l.lower()]
        return []
    except Exception:
        return []


def run():
    print(f"\n{BOLD}{DARK_GREEN}[10] EMAIL TRACKER{RESET}")
    hr()
    email = input(f"{GREEN}Email address: {RESET}").strip().lower()
    if not email or not EMAIL_RE.match(email):
        print(f"{RED}[-]{RESET} Invalid email format.")
        return

    user, domain = email.split("@")
    print(f"\n{CYAN}[i]{RESET} Analyzing {BOLD}{email}{RESET}\n")

    # 1. Syntax
    print(f"{DARK_GREEN}== Syntax =={RESET}")
    print(f"  {GREEN}[+]{RESET} Format valid.")
    print(f"  {GREEN}[+]{RESET} Local part:  {user}")
    print(f"  {GREEN}[+]{RESET} Domain:      {domain}")

    # 2. MX records
    print(f"\n{DARK_GREEN}== Mail Exchange (MX) =={RESET}")
    mxs = _check_mx(domain)
    if mxs:
        print(f"  {GREEN}[+]{RESET} Domain accepts mail. MX records found:")
        for mx in mxs[:5]:
            print(f"     {GREY}{mx}{RESET}")
    else:
        print(f"  {YELLOW}[!]{RESET} No MX records found - domain may not accept email.")

    # 3. Breach check (HIBP free domain endpoint)
    print(f"\n{DARK_GREEN}== Public Breach Data (HIBP domain endpoint) =={RESET}")
    try:
        r = requests.get(
            f"https://haveibeenpwned.com/api/v3/breacheddomain/{domain}",
            headers={"User-Agent": "MrRobotTools-EmailTracker/1.0"},
            timeout=10,
        )
        if r.status_code == 200:
            breaches = r.json()
            if breaches:
                print(f"  {YELLOW}[!]{RESET} Domain {domain} appears in {len(breaches)} known breach(es):")
                for b in breaches[:20]:
                    name = b.get("Name", "?")
                    pwn_count = b.get("PwnCount", "?")
                    print(f"     {RED}- {name:<30} ({pwn_count} accounts){RESET}")
            else:
                print(f"  {GREEN}[+]{RESET} No breaches indexed for this domain.")
        elif r.status_code == 404:
            print(f"  {GREEN}[+]{RESET} No breaches indexed for this domain.")
        elif r.status_code == 403:
            print(f"  {YELLOW}[!]{RESET} HIBP rate-limited or requires API key. Skipping.")
        else:
            print(f"  {GREY}[i]{RESET} HIBP returned HTTP {r.status_code}.{RESET}")
    except requests.RequestException as e:
        print(f"  {RED}[-]{RESET} HIBP request failed: {e}")

    # 4. Gravatar avatar check
    print(f"\n{DARK_GREEN}== Gravatar Avatar =={RESET}")
    import hashlib
    h = hashlib.md5(email.encode("utf-8")).hexdigest()
    grav_url = f"https://www.gravatar.com/avatar/{h}?d=404"
    try:
        r = requests.get(grav_url, timeout=8)
        if r.status_code == 200:
            print(f"  {GREEN}[+]{RESET} Gravatar exists: {CYAN}https://www.gravatar.com/{h}{RESET}")
        else:
            print(f"  {GREY}[-] No Gravatar registered.{RESET}")
    except requests.RequestException:
        print(f"  {GREY}[-] Gravatar check failed.{RESET}")
