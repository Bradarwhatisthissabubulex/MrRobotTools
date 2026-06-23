"""[12] IP Lookup - geolocation / ASN / org info via ipapi.co (no key)."""

import socket

from core import http as requests

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr


def run():
    print(f"\n{BOLD}{DARK_GREEN}[12] IP LOOKUP{RESET}")
    hr()
    target = input(f"{GREEN}IP or domain: {RESET}").strip()
    if not target:
        print(f"{RED}[-]{RESET} No target provided.")
        return

    # Resolve to IP if domain
    try:
        ip = socket.gethostbyname(target)
        if ip != target:
            print(f"{CYAN}[i]{RESET} Resolved {target} -> {ip}")
    except socket.gaierror:
        print(f"{RED}[-]{RESET} Could not resolve.")
        return
    target = ip

    print(f"\n{CYAN}[i]{RESET} Looking up {BOLD}{target}{RESET} via ipapi.co ...\n")

    try:
        r = requests.get(f"https://ipapi.co/{target}/json/", timeout=15,
                         headers={"User-Agent": "MrRobotTools-IPLookup/1.0"})
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        print(f"{RED}[-]{RESET} API request failed: {e}")
        return
    except ValueError:
        print(f"{RED}[-]{RESET} Could not parse JSON response.")
        return

    if data.get("error"):
        print(f"{RED}[-]{RESET} API error: {data.get('reason', 'unknown')}")
        return

    print(f"{DARK_GREEN}== IP Details =={RESET}")
    print(f"  {GREEN}IP:{RESET}              {data.get('ip', 'N/A')}")
    print(f"  {GREEN}Version:{RESET}         {data.get('version', 'N/A')}")
    print(f"  {GREEN}City:{RESET}            {data.get('city', 'N/A')}")
    print(f"  {GREEN}Region:{RESET}          {data.get('region', 'N/A')}")
    print(f"  {GREEN}Country:{RESET}         {data.get('country_name', 'N/A')} ({data.get('country', 'N/A')})")
    print(f"  {GREEN}Continent:{RESET}       {data.get('continent_code', 'N/A')}")
    print(f"  {GREEN}Postal:{RESET}          {data.get('postal', 'N/A')}")
    print(f"  {GREEN}Latitude:{RESET}        {data.get('latitude', 'N/A')}")
    print(f"  {GREEN}Longitude:{RESET}       {data.get('longitude', 'N/A')}")
    print(f"  {GREEN}Timezone:{RESET}        {data.get('timezone', 'N/A')}")
    print(f"  {GREEN}UTC offset:{RESET}      {data.get('utc_offset', 'N/A')}")
    print(f"  {GREEN}Org:{RESET}             {data.get('org', 'N/A')}")
    print(f"  {GREEN}ASN:{RESET}             {data.get('asn', 'N/A')}")
    print(f"  {GREEN}Languages:{RESET}       {data.get('languages', 'N/A')}")
    print(f"  {GREEN}Currency:{RESET}        {data.get('currency', 'N/A')} ({data.get('currency_name', 'N/A')})")

    if data.get("latitude") and data.get("longitude"):
        lat, lon = data["latitude"], data["longitude"]
        print(f"\n{CYAN}[i]{RESET} Map: {GREY}https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=10/{lat}/{lon}{RESET}")
