"""[11] Email Lookup - validate email, get domain WHOIS + provider info."""

import re
import socket

from core import http as requests

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def run():
    print(f"\n{BOLD}{DARK_GREEN}[11] EMAIL LOOKUP{RESET}")
    hr()
    email = input(f"{GREEN}Email address: {RESET}").strip().lower()
    if not email or not EMAIL_RE.match(email):
        print(f"{RED}[-]{RESET} Invalid email format.")
        return

    user, domain = email.split("@")
    print(f"\n{CYAN}[i]{RESET} Looking up {BOLD}{email}{RESET}\n")

    # 1. Syntax
    print(f"{DARK_GREEN}== Syntax & Pattern =={RESET}")
    print(f"  {GREEN}[+]{RESET} Format valid.")
    patterns = {
        "firstname.lastname": r"^[a-z]+\.[a-z]+$",
        "firstname.lastname<N>": r"^[a-z]+\.[a-z]+[0-9]+$",
        "firstinitial+lastname": r"^[a-z][a-z]+$",
        "nickname (digits)": r"^[a-z]+[0-9]+$",
        "firstname<N>": r"^[a-z]+[0-9]{1,4}$",
    }
    matched = [n for n, p in patterns.items() if re.match(p, user)]
    if matched:
        print(f"  {GREEN}[+]{RESET} Probable pattern: {CYAN}{', '.join(matched)}{RESET}")
    else:
        print(f"  {GREY}[i]{RESET} Local-part doesn't match common patterns.{RESET}")

    # 2. Domain resolution
    print(f"\n{DARK_GREEN}== Domain Resolution =={RESET}")
    try:
        ip = socket.gethostbyname(domain)
        print(f"  {GREEN}[+]{RESET} A record: {ip}")
    except socket.gaierror:
        print(f"  {RED}[-]{RESET} Domain does not resolve.")

    # 3. WHOIS
    print(f"\n{DARK_GREEN}== WHOIS (Domain) =={RESET}")
    try:
        import whois
        w = whois.whois(domain)
        if w and (w.registrar or w.creation_date):
            print(f"  {GREEN}[+]{RESET} Registrar:     {w.registrar or 'N/A'}")
            created = w.creation_date
            if isinstance(created, list):
                created = created[0]
            print(f"  {GREEN}[+]{RESET} Created:       {created}")
            expires = w.expiration_date
            if isinstance(expires, list):
                expires = expires[0]
            print(f"  {GREEN}[+]{RESET} Expires:       {expires}")
            print(f"  {GREEN}[+]{RESET} Name servers:  {', '.join(w.name_servers or [])[:80]}")
            if w.emails:
                emails = w.emails[0] if isinstance(w.emails, list) else w.emails
                print(f"  {GREEN}[+]{RESET} Abuse contact: {emails}")
        else:
            print(f"  {GREY}[-] No WHOIS data returned.{RESET}")
    except Exception as e:
        print(f"  {YELLOW}[!]{RESET} WHOIS lookup failed: {e}")

    # 4. MX check via nslookup
    print(f"\n{DARK_GREEN}== MX Records =={RESET}")
    try:
        import subprocess
        r = subprocess.run(["nslookup", "-type=mx", domain], capture_output=True, text=True, timeout=8)
        out = r.stdout + r.stderr
        mx_lines = [l.strip() for l in out.splitlines() if "mail exchanger" in l.lower()]
        if mx_lines:
            for mx in mx_lines[:5]:
                print(f"  {GREEN}[+]{RESET} {mx}")
        else:
            print(f"  {GREY}[-] No MX records.{RESET}")
    except Exception as e:
        print(f"  {RED}[-]{RESET} MX lookup failed: {e}")

    # 5. Mail provider heuristic
    print(f"\n{DARK_GREEN}== Provider =={RESET}")
    providers = {
        "gmail.com": "Google Gmail",
        "outlook.com": "Microsoft Outlook",
        "hotmail.com": "Microsoft Hotmail",
        "yahoo.com": "Yahoo Mail",
        "icloud.com": "Apple iCloud",
        "protonmail.com": "ProtonMail",
        "proton.me": "ProtonMail",
        "tutanota.com": "Tutanota",
        "zoho.com": "Zoho Mail",
        "gmx.com": "GMX",
    }
    if domain in providers:
        print(f"  {GREEN}[+]{RESET} Free provider: {providers[domain]}")
    else:
        print(f"  {GREEN}[+]{RESET} Likely a custom / corporate domain.")
