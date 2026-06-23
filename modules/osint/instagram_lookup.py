"""[14] Instagram Profile Lookup - public profile metadata, no login."""

import re
import json

from core import http as requests

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr


def run():
    print(f"\n{BOLD}{DARK_GREEN}[14] INSTAGRAM PROFILE LOOKUP{RESET}")
    hr()
    print(f"{CYAN}[i]{RESET} Public profile data only - no login, no API key.{RESET}\n")
    username = input(f"{GREEN}Instagram username: {RESET}").strip().lstrip("@")
    if not username:
        print(f"{RED}[-]{RESET} No username provided.")
        return

    url = f"https://www.instagram.com/{username}/"
    print(f"{CYAN}[i]{RESET} Fetching {url} ...\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
    except requests.RequestException as e:
        print(f"{RED}[-]{RESET} Request failed: {e}")
        return

    if r.status_code != 200:
        print(f"{RED}[-]{RESET} HTTP {r.status_code} - account may be private/suspended/not found.")
        return

    text = r.text
    user_data = None

    # Pattern 1: window._sharedData
    m = re.search(r"window\._sharedData\s*=\s*({.*?})\s*;</script>", text)
    if m:
        try:
            shared = json.loads(m.group(1))
            user_data = (shared.get("entry_data", {})
                                .get("ProfilePage", [{}])[0]
                                .get("graphql", {})
                                .get("user", {}))
        except Exception:
            user_data = None

    # Pattern 2: <script type="application/ld+json">
    if not user_data:
        for m in re.finditer(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', text, re.DOTALL):
            try:
                ld = json.loads(m.group(1))
                if isinstance(ld, dict) and ld.get("@type") == "ProfilePage":
                    user_data = {
                        "full_name": ld.get("name"),
                        "biography": ld.get("description"),
                        "external_url": ld.get("mainEntityofPage", {}).get("@id") if isinstance(ld.get("mainEntityofPage"), dict) else None,
                        "profile_pic_url": ld.get("image"),
                    }
                    interaction = ld.get("interactionStatistic", [])
                    if isinstance(interaction, list):
                        for stat in interaction:
                            if stat.get("@type") == "InteractionCounter":
                                t = stat.get("interactionType", "")
                                if "UserComments" in t:
                                    user_data["edge_media_to_comment"] = {"count": stat.get("userInteractionCount")}
                                elif "LikeAction" in t or "UserPageVisits" in t:
                                    user_data["edge_followed_by"] = {"count": stat.get("userInteractionCount")}
                    break
            except Exception:
                continue

    # Pattern 3: meta tags fallback
    if not user_data:
        user_data = {}
        m = re.search(r'<meta property="og:title" content="([^"]+)"', text)
        if m:
            user_data["full_name"] = m.group(1).split("(")[0].strip().strip("• ").strip()
        m = re.search(r'<meta property="og:description" content="([^"]+)"', text)
        if m:
            desc = m.group(1)
            stats_match = re.search(r"([\d,.]+)\s*Followers?,?\s*([\d,.]+)\s*Following,?\s*([\d,.]+)\s*Posts?", desc)
            if stats_match:
                user_data["edge_followed_by"] = {"count": stats_match.group(1)}
                user_data["edge_follow"] = {"count": stats_match.group(2)}
                user_data["edge_owner_to_timeline_media"] = {"count": stats_match.group(3)}
            user_data["biography"] = desc
        m = re.search(r'<meta property="og:image" content="([^"]+)"', text)
        if m:
            user_data["profile_pic_url"] = m.group(1)

    if not user_data:
        print(f"{YELLOW}[!]{RESET} Could not extract profile data (Instagram may be rate-limiting).")
        return

    print(f"{DARK_GREEN}== Profile =={RESET}")
    print(f"  {GREEN}Username:{RESET}      @{username}")
    print(f"  {GREEN}Display name:{RESET}  {user_data.get('full_name', 'N/A')}")
    print(f"  {GREEN}Followers:{RESET}     {(user_data.get('edge_followed_by') or {}).get('count', 'N/A')}")
    print(f"  {GREEN}Following:{RESET}     {(user_data.get('edge_follow') or {}).get('count', 'N/A')}")
    print(f"  {GREEN}Posts:{RESET}         {(user_data.get('edge_owner_to_timeline_media') or {}).get('count', 'N/A')}")
    bio = user_data.get('biography', '')
    if bio:
        print(f"  {GREEN}Bio:{RESET}           {bio[:300]}")
    if user_data.get('external_url'):
        print(f"  {GREEN}External URL:{RESET} {user_data['external_url']}")
    if user_data.get('is_private'):
        print(f"  {YELLOW}[!]{RESET} Account is PRIVATE.")
    if user_data.get('is_verified'):
        print(f"  {GREEN}[+]{RESET} Verified account.")
    if user_data.get('profile_pic_url'):
        print(f"  {GREEN}Profile pic:{RESET}   {user_data['profile_pic_url'][:80]}...")
    print(f"\n  {CYAN}Profile URL:{RESET} https://www.instagram.com/{username}/")
