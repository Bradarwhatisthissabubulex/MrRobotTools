"""[13] Phone Number Lookup - validate, parse country/carrier info."""

import re

from core import http as requests

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr


COUNTRY_CODES = {
    "1": ("United States / Canada", "+1"),
    "44": ("United Kingdom", "+44"),
    "33": ("France", "+33"),
    "49": ("Germany", "+49"),
    "34": ("Spain", "+34"),
    "39": ("Italy", "+39"),
    "31": ("Netherlands", "+31"),
    "61": ("Australia", "+61"),
    "81": ("Japan", "+81"),
    "82": ("South Korea", "+82"),
    "86": ("China", "+86"),
    "91": ("India", "+91"),
    "55": ("Brazil", "+55"),
    "52": ("Mexico", "+52"),
    "7": ("Russia / Kazakhstan", "+7"),
    "98": ("Iran", "+98"),
    "966": ("Saudi Arabia", "+966"),
    "971": ("UAE", "+971"),
    "90": ("Turkey", "+90"),
    "20": ("Egypt", "+20"),
    "27": ("South Africa", "+27"),
}


def _normalize(phone):
    """Strip formatting, normalize to +XXXXXXXXXX form."""
    digits = re.sub(r"[^\d+]", "", phone)
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    if not digits.startswith("+") and digits.startswith("0"):
        digits = "+" + digits[1:]
    return digits


def run():
    print(f"\n{BOLD}{DARK_GREEN}[13] PHONE NUMBER LOOKUP{RESET}")
    hr()
    raw = input(f"{GREEN}Phone number (international format preferred): {RESET}").strip()
    if not raw:
        print(f"{RED}[-]{RESET} No number provided.")
        return

    number = _normalize(raw)
    print(f"\n{CYAN}[i]{RESET} Normalized: {BOLD}{number}{RESET}\n")

    if not number.startswith("+"):
        print(f"{YELLOW}[!]{RESET} No country code detected. Try +1, +44, etc.")
        return

    cc_digits = number[1:]
    country = "Unknown"
    cc = ""
    for length in (3, 2, 1):
        candidate = cc_digits[:length]
        if candidate in COUNTRY_CODES:
            country, cc = COUNTRY_CODES[candidate]
            break

    print(f"{DARK_GREEN}== Number Analysis =={RESET}")
    print(f"  {GREEN}Raw input:{RESET}        {raw}")
    print(f"  {GREEN}Normalized:{RESET}       {number}")
    print(f"  {GREEN}Country code:{RESET}    {cc or ('+' + cc_digits[:2])}")
    print(f"  {GREEN}Likely country:{RESET}  {country}")
    print(f"  {GREEN}National number:{RESET} {cc_digits[len(cc)-1:] if cc else cc_digits}")
    print(f"  {GREEN}Digits total:{RESET}    {len(cc_digits)}")

    # Type heuristic
    print(f"\n{DARK_GREEN}== Type Heuristic =={RESET}")
    nlen = len(cc_digits)
    if nlen == 11 and cc_digits.startswith("1"):
        print(f"  {GREEN}[+]{RESET} Looks like a US/Canada NANP number.")
    elif nlen in (10, 11) and country.startswith("United Kingdom"):
        print(f"  {GREEN}[+]{RESET} Looks like a UK mobile or landline.")
    elif nlen >= 10:
        print(f"  {GREEN}[+]{RESET} Length consistent with a mobile number.")
    else:
        print(f"  {YELLOW}[!]{RESET} Length unusual - may be a short code or landline.")

    # Optional: try Telnyx free DCS endpoint
    print(f"\n{DARK_GREEN}== Online Enrichment =={RESET}")
    try:
        r = requests.get(
            f"https://api.telnyx.com/derived/v1/phone_number?phone_number={number}",
            timeout=8,
            headers={"User-Agent": "MrRobotTools-PhoneLookup/1.0"},
        )
        if r.status_code == 200:
            d = r.json()
            print(f"  {GREEN}[+]{RESET} Carrier: {d.get('carrier', {}).get('name', 'N/A')}")
            print(f"  {GREEN}[+]{RESET} Line type: {d.get('line_type', 'N/A')}")
            print(f"  {GREEN}[+]{RESET} Country: {d.get('country', {}).get('name', 'N/A')}")
        else:
            print(f"  {GREY}[i]{RESET} Free lookup endpoint returned {r.status_code}.{RESET}")
    except Exception as e:
        print(f"  {GREY}[i]{RESET} Online enrichment unavailable ({type(e).__name__}).{RESET}")

    print(f"\n{CYAN}[i]{RESET} Tip: search the number (without +) on Truecaller / Sync.me for caller ID.")
