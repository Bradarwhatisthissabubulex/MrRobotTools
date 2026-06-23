"""[09] Username Tracker - check ~40 social/dev sites for a username."""

import concurrent.futures
import re

from core import http as requests

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr


SITES = [
    ("GitHub",        "https://github.com/{u}"),
    ("GitLab",        "https://gitlab.com/{u}"),
    ("Twitter/X",     "https://x.com/{u}"),
    ("Instagram",     "https://www.instagram.com/{u}/"),
    ("TikTok",        "https://www.tiktok.com/@{u}"),
    ("YouTube",       "https://www.youtube.com/@{u}"),
    ("Reddit",        "https://www.reddit.com/user/{u}"),
    ("Twitch",        "https://www.twitch.tv/{u}"),
    ("Facebook",      "https://www.facebook.com/{u}"),
    ("LinkedIn",      "https://www.linkedin.com/in/{u}/"),
    ("Medium",        "https://medium.com/@{u}"),
    ("DeviantArt",    "https://www.deviantart.com/{u}"),
    ("Pinterest",     "https://www.pinterest.com/{u}/"),
    ("Snapchat",      "https://www.snapchat.com/add/{u}"),
    ("Telegram",      "https://t.me/{u}"),
    ("Vimeo",         "https://vimeo.com/{u}"),
    ("SoundCloud",    "https://soundcloud.com/{u}"),
    ("Spotify",       "https://open.spotify.com/user/{u}"),
    ("Patreon",       "https://www.patreon.com/{u}"),
    ("Ko-fi",         "https://ko-fi.com/{u}"),
    ("Steam",         "https://steamcommunity.com/id/{u}"),
    ("Roblox",        "https://www.roblox.com/user.aspx?username={u}"),
    ("Mastodon (mstdn)","https://mstdn.social/@{u}"),
    ("Keybase",       "https://keybase.io/{u}"),
    ("HackerNews",    "https://news.ycombinator.com/user?id={u}"),
    ("Product Hunt",  "https://www.producthunt.com/@{u}"),
    ("Dev.to",        "https://dev.to/{u}"),
    ("CodePen",       "https://codepen.io/{u}"),
    ("Replit",        "https://replit.com/@{u}"),
    ("Docker Hub",    "https://hub.docker.com/u/{u}"),
    ("PyPI",          "https://pypi.org/user/{u}/"),
    ("NPM",           "https://www.npmjs.com/~{u}"),
    ("Stack Overflow","https://stackoverflow.com/users/{u}"),
    ("About.me",      "https://about.me/{u}"),
    ("Linktree",      "https://linktr.ee/{u}"),
    ("Gravatar",      "https://gravatar.com/{u}"),
    ("Wattpad",       "https://www.wattpad.com/user/{u}"),
    ("Goodreads",     "https://www.goodreads.com/{u}"),
    ("Trello",        "https://trello.com/{u}"),
    ("Behance",       "https://www.behance.net/{u}"),
]

NOT_FOUND_PATTERNS = [
    "not found", "page not found", "404", "doesn't exist", "does not exist",
    "user not found", "account not found", "unavailable", "suspended",
]


def _check(name, site_name, url_template):
    """Check one site. Returns (site_name, url, status)."""
    url = url_template.format(u=name)
    try:
        r = requests.get(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0 (MrRobotTools/1.0)"})
        body = r.text.lower()[:5000]
        if r.status_code == 404:
            return (site_name, url, "NOT_FOUND")
        if r.status_code >= 500:
            return (site_name, url, "ERROR")
        for pat in NOT_FOUND_PATTERNS:
            if pat in body and len(r.text) < 2000:
                return (site_name, url, "NOT_FOUND")
        if r.status_code == 200:
            return (site_name, url, "FOUND")
        return (site_name, url, f"HTTP_{r.status_code}")
    except requests.RequestException as e:
        return (site_name, url, f"ERR:{type(e).__name__}")


def run():
    print(f"\n{BOLD}{DARK_GREEN}[09] USERNAME TRACKER{RESET}")
    hr()
    print(f"{CYAN}[i]{RESET} Checks {len(SITES)} social/dev sites for a username.{RESET}\n")
    username = input(f"{GREEN}Username to track: {RESET}").strip()
    if not username:
        print(f"{RED}[-]{RESET} No username provided.")
        return
    username = re.sub(r"[^a-zA-Z0-9._-]", "", username)
    print(f"\n{CYAN}[i]{RESET} Searching for '{BOLD}{username}{RESET}' across {len(SITES)} sites...\n")

    found, not_found, errors = [], [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
        futures = [ex.submit(_check, username, n, u) for n, u in SITES]
        for fut in concurrent.futures.as_completed(futures):
            site, url, status = fut.result()
            if status == "FOUND":
                found.append((site, url))
                print(f"  {GREEN}[+]{RESET} {site:<20} {CYAN}{url}{RESET}")
            elif status == "NOT_FOUND":
                not_found.append((site, url))
            else:
                errors.append((site, url, status))

    print(f"\n{DARK_GREEN}== Summary =={RESET}")
    print(f"  {GREEN}Found:{RESET}      {len(found)} profile(s)")
    print(f"  {GREY}Not found:{RESET}  {len(not_found)} site(s)")
    print(f"  {YELLOW}Errors:{RESET}     {len(errors)} site(s)")
    for site, url, status in errors:
        print(f"    {GREY}- {site}: {status}{RESET}")

    if found:
        save = input(f"\n{GREEN}Save found URLs to file? (path or Enter to skip): {RESET}").strip()
        if save:
            try:
                with open(save, "w", encoding="utf-8") as f:
                    for site, url in found:
                        f.write(f"{site}\t{url}\n")
                print(f"{GREEN}[+]{RESET} Saved {len(found)} URLs.")
            except Exception as e:
                print(f"{RED}[-]{RESET} Save failed: {e}")
