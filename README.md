# MrRobotTools

> **For those who want tools but don't want to get infected by viruses.**

A clean, from-scratch security & OSINT toolkit with a Kali-style CLI.
17 tools across Pentesting, OSINT, and Utilities. Green-gradient ASCII
banner, smooth `(admin@mrrobot)-[path]$` prompt, ethics gate on launch.

## Why this exists

Plenty of "free" hacking toolkits on GitHub ship with backdoors,
stealers, or hidden crypto miners. MrRobotTools is the opposite: every
line of code is original, written in plain Python, and auditable in
minutes. No obfuscation, no telemetry, no network calls you can't see.

## Features

### Pentesting (6 tools)
- `[01]` **Advanced Scanner** - ICMP + port scan + banner grab + HTTP fingerprint
- `[02]` **Vuln Scanner** - Passive checks for missing security headers, cookie flags, sensitive file exposure, directory listing
- `[03]` **Port Scanner** - Multithreaded TCP connect scan
- `[04]` **URL Discovery Crawler** - BFS crawl of internal links
- `[05]` **IP Pinger** - ICMP echo via OS `ping`
- `[06]` **Host Discovery** - Sweep a CIDR or IP range for live hosts

### OSINT (8 tools)
- `[07]` **Dorking Query Engine** - Generate Google dorks for a domain you own
- `[08]` **Wallet Tracker** - BTC / ETH / LTC / BCH / DOGE wallet info (Blockchair, no API key)
- `[09]` **Username Tracker** - Check ~40 social/dev sites for a username
- `[10]` **Email Tracker** - MX records + HIBP breach search + Gravatar
- `[11]` **Email Lookup** - WHOIS + provider heuristics + email pattern detection
- `[12]` **IP Lookup** - Geo / ASN / org info (ipapi.co, no key)
- `[13]` **Phone Lookup** - Country code + carrier heuristics
- `[14]` **Instagram Profile** - Public profile metadata, no login

### Utilities (3 tools)
- `[15]` **Metadata Scanner** - EXIF / PDF / Office document metadata
- `[16]` **Metadata Deleter** - Strip EXIF from images, core-props from Office docs
- `[17]` **Website Cloner** - Multi-page or single-page site archiver (stdlib only, no wget)

## Requirements

- Python 3.8+
- Required pip packages: `beautifulsoup4`, `python-whois` (auto-installed on first run)
- Optional: `Pillow`, `exifread` for full EXIF support (auto-skipped if missing)
- **No `requests`/`urllib3` dependency** - uses Python's stdlib `urllib` via `core/http.py`

## Install & Run

```bash
python mrrobot.py
```

On first launch:
1. The ASCII banner shows
2. The ethics/authorization banner appears - type `I agree` to continue
3. The main menu loads with the 3-column tool layout
4. Type a number (1-17) to run a tool, or `99` to exit

## Build a Windows .exe (one click)

```bat
build_windows.bat
```

This installs deps + PyInstaller and produces `dist\MrRobotTools.exe`
(~25 MB, self-contained).

## Build a Linux binary

```bash
bash build_linux.sh
```

Produces `dist/MrRobotTools-Linux` (one-file ELF binary).

## Project layout

```
MrRobotTools/
├── mrrobot.py             # Entry point - menu + dispatch
├── core/
│   ├── colors.py          # Green palette + Kali prompt
│   ├── banner.py          # ASCII mask + gradient + screen render
│   ├── auth.py            # Authorization gate
│   └── http.py            # Stdlib HTTP wrapper (replaces requests)
├── modules/
│   ├── pentesting/        # Tools 01-06
│   ├── osint/             # Tools 07-14
│   └── utils/             # Tools 15-17
├── requirements.txt
├── build_windows.bat
├── build_linux.sh
├── mrrobot.spec
├── LICENSE.md
└── README.md
```

## Legal & Ethical Use

**For authorized security testing and OSINT research only.**

- Only run pentesting tools against systems you OWN or have WRITTEN
  AUTHORIZATION to test.
- OSINT tools query public sources (Blockchair, HIBP, ipapi.co, public
  web pages) - verify you have a lawful basis for any data you collect.
- Unauthorized scanning, port probing, or website cloning may violate
  computer-fraud, privacy, and telecommunications laws (e.g. US CFAA,
  UK Computer Misuse Act, EU GDPR).
- The author accepts no liability for misuse. You are solely responsible
  for your actions.

If you're unsure whether a target is in scope, **don't scan it**.

## License

MIT - see [LICENSE.md](LICENSE.md).
