"""[17] Website Cloner - multi-page or single-page site archiver.

Uses only the Python standard library (via core/http.py). No wget needed.
For archiving sites you own or have permission to mirror.
"""

import os
import re
import time
import urllib.parse
from collections import deque

from core import http as requests
from bs4 import BeautifulSoup

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr


def _safe_filename(url, is_html=False):
    """Convert a URL into a safe filesystem path that mirrors the URL structure."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    if path.endswith("/"):
        path = path + "index"
    if is_html and "." not in os.path.basename(path):
        path = path + ".html"
    path = re.sub(r'[<>:"|?*]', "_", path)
    return path


def _download_asset(url, assets_dir, headers):
    """Download an asset (image/css/js) into assets_dir. Returns local path or None."""
    try:
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        if r.status_code != 200:
            return None
    except requests.RequestException:
        return None
    parsed = urllib.parse.urlparse(url)
    fname = os.path.basename(parsed.path) or "asset.bin"
    fname = re.sub(r'[<>:"|?*\\/]', "_", fname)
    fpath = os.path.join(assets_dir, fname)
    counter = 1
    base, ext = os.path.splitext(fname)
    while os.path.exists(fpath):
        try:
            with open(fpath, "rb") as f:
                if f.read() == r.content:
                    return f"assets/{fname}"
        except Exception:
            pass
        fname = f"{base}_{counter}{ext}"
        fpath = os.path.join(assets_dir, fname)
        counter += 1
    try:
        with open(fpath, "wb") as f:
            f.write(r.content)
        return f"assets/{fname}"
    except Exception:
        return None


def _same_domain(url1, url2):
    return urllib.parse.urlparse(url1).netloc == urllib.parse.urlparse(url2).netloc


def _clone_page(url, out_dir, headers, seen, page_count, max_pages, delay):
    """Clone a single page. Returns list of new URLs to crawl."""
    try:
        r = requests.get(url, headers=headers, timeout=20, verify=False)
    except requests.RequestException as e:
        print(f"  {RED}[-]{RESET} {url} -> error: {e}")
        return []

    if r.status_code != 200:
        print(f"  {YELLOW}[!]{RESET} {url} -> HTTP {r.status_code}")
        return []

    if "text/html" not in r.headers.get("Content-Type", ""):
        return []

    final_url = r.url
    print(f"  {GREEN}[{page_count:>3}]{RESET} {final_url}  {GREY}({r.status_code}){RESET}")

    assets_dir = os.path.join(out_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    try:
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception:
        return []

    # Download + rewrite images
    for img in soup.find_all("img", src=True):
        src = img["src"]
        abs_url = urllib.parse.urljoin(final_url, src)
        local = _download_asset(abs_url, assets_dir, headers)
        if local:
            img["src"] = local

    # Download + rewrite CSS
    for link in soup.find_all("link", href=True):
        href = link["href"]
        if not href or href.startswith(("data:", "#", "mailto:", "javascript:")):
            continue
        abs_url = urllib.parse.urljoin(final_url, href)
        if _same_domain(abs_url, url):
            local = _download_asset(abs_url, assets_dir, headers)
            if local:
                link["href"] = local

    # Download + rewrite JS
    for script in soup.find_all("script", src=True):
        src = script["src"]
        if not src or src.startswith(("data:", "#")):
            continue
        abs_url = urllib.parse.urljoin(final_url, src)
        if _same_domain(abs_url, url):
            local = _download_asset(abs_url, assets_dir, headers)
            if local:
                script["src"] = local

    # Save HTML
    rel_path = _safe_filename(final_url, is_html=True)
    html_path = os.path.join(out_dir, rel_path)
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
    except Exception as e:
        print(f"  {RED}[-]{RESET} Could not save {html_path}: {e}")

    # Collect same-domain links to crawl next
    new_urls = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue
        abs_url = urllib.parse.urljoin(final_url, href).split("#")[0]
        if _same_domain(abs_url, url) and abs_url not in seen and abs_url.startswith(("http://", "https://")):
            new_urls.append(abs_url)
    return new_urls


def run():
    print(f"\n{BOLD}{DARK_GREEN}[17] WEBSITE CLONER{RESET}")
    hr()
    print(f"{YELLOW}[!]{RESET} For archiving sites you own / have permission to mirror.{RESET}\n")
    url = input(f"{GREEN}URL to clone (e.g. https://example.com): {RESET}").strip()
    if not url:
        print(f"{RED}[-]{RESET} No URL provided.")
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    out_dir = input(f"{GREEN}Output directory (default ./cloned_site): {RESET}").strip() or "./cloned_site"
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    mode = input(
        f"{GREEN}Mode  [1] full mirror (multi-page)  [2] single page (default): {RESET}"
    ).strip() or "2"

    headers = {"User-Agent": "Mozilla/5.0 (MrRobotTools-Cloner/1.0)"}

    if mode == "1":
        try:
            max_pages = int(input(f"{GREEN}Max pages to mirror (default 30): {RESET}").strip() or "30")
        except ValueError:
            max_pages = 30
        try:
            delay = float(input(f"{GREEN}Delay between requests sec (default 0.5): {RESET}").strip() or "0.5")
        except ValueError:
            delay = 0.5

        print(f"\n{CYAN}[i]{RESET} Mirroring {url} (max {max_pages} pages) into {out_dir} ...\n")

        seen = set()
        queue = deque([url])
        page_count = 0
        start_time = time.time()

        while queue and page_count < max_pages:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            page_count += 1
            new_urls = _clone_page(current, out_dir, headers, seen,
                                   page_count, max_pages, delay)
            for u in new_urls:
                if u not in seen:
                    queue.append(u)
            if delay > 0:
                time.sleep(delay)

        elapsed = time.time() - start_time
        print(f"\n{GREEN}[+]{RESET} Mirror complete: {page_count} page(s) in {elapsed:.1f}s")

    else:
        print(f"\n{CYAN}[i]{RESET} Cloning single page {url} into {out_dir} ...\n")
        _clone_page(url, out_dir, headers, set(), 1, 1, 0)

    # Summary
    total_files = sum(len(files) for _, _, files in os.walk(out_dir))
    total_size = sum(os.path.getsize(os.path.join(r, f))
                     for r, _, fs in os.walk(out_dir) for f in fs)
    print(f"{CYAN}[i]{RESET} Cloned {total_files} file(s), {total_size:,} bytes total.")
    print(f"{CYAN}[i]{RESET} Output: {out_dir}")
