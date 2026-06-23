"""[16] File Metadata Deleter - strip EXIF from images, core-props from Office docs."""

import os

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr


def _strip_image_pil(src, dst):
    """Re-save image without EXIF using Pillow."""
    from PIL import Image
    img = Image.open(src)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    fmt = img.format or "JPEG"
    clean.save(dst, format=fmt)


def _strip_office_zip(src, dst):
    """Remove core/app properties XML content from Office .docx/.xlsx/.pptx."""
    import zipfile
    import re
    with zipfile.ZipFile(src, "r") as zin:
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if any(x in item.lower() for x in ("core.xml", "app.xml")):
                    # Strip values but keep tags (so the doc still opens)
                    data = re.sub(rb">[^<]+<", b"><", data)
                zout.writestr(item, data)


def run():
    print(f"\n{BOLD}{DARK_GREEN}[16] FILE METADATA DELETER{RESET}")
    hr()
    path = input(f"{GREEN}File path: {RESET}").strip().strip('"').strip("'")
    if not path or not os.path.isfile(path):
        print(f"{RED}[-]{RESET} File not found.")
        return

    ext = os.path.splitext(path)[1].lower()
    image_exts = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp")
    office_exts = (".docx", ".xlsx", ".pptx")

    if ext not in image_exts and ext not in office_exts:
        print(f"{RED}[-]{RESET} Unsupported file type. Supported: {', '.join(image_exts + office_exts)}")
        return

    out_dir = input(
        f"{GREEN}Output directory (Enter = same as source): {RESET}"
    ).strip().strip('"').strip("'") or os.path.dirname(os.path.abspath(path))

    base, _ext = os.path.splitext(os.path.basename(path))
    dst = os.path.join(out_dir, f"{base}_cleaned{_ext or ext}")
    if os.path.exists(dst):
        overwrite = input(f"{YELLOW}[!]{RESET} {dst} exists. Overwrite? (y/N): {RESET}").strip().lower()
        if overwrite != "y":
            print(f"{RED}[-]{RESET} Cancelled.")
            return

    print(f"\n{CYAN}[i]{RESET} Stripping metadata from {BOLD}{path}{RESET}")
    print(f"{CYAN}[i]{RESET} Output: {dst}\n")

    try:
        if ext in image_exts:
            try:
                _strip_image_pil(path, dst)
            except ImportError:
                print(f"{RED}[-]{RESET} Pillow not installed. Install with: pip install Pillow")
                return
        elif ext in office_exts:
            _strip_office_zip(path, dst)
    except Exception as e:
        print(f"{RED}[-]{RESET} Failed: {e}")
        return

    # Compare sizes
    src_size = os.path.getsize(path)
    dst_size = os.path.getsize(dst)
    diff = src_size - dst_size
    print(f"{GREEN}[+]{RESET} Cleaned file written.")
    print(f"  Original size:  {src_size:>10} bytes")
    print(f"  Cleaned size:   {dst_size:>10} bytes")
    print(f"  Difference:     {diff:>+10} bytes ({(diff/src_size*100) if src_size else 0:+.1f}%)")

    # Verify
    print(f"\n{DARK_GREEN}== Verification =={RESET}")
    if ext in image_exts:
        try:
            from PIL import Image
            img = Image.open(dst)
            raw = img._getexif() or {}
            print(f"  {GREEN}[+]{RESET} EXIF tags remaining: {len(raw)}")
            if raw:
                print(f"  {YELLOW}[!]{RESET} Some EXIF may remain (color profiles, etc.).")
        except Exception as e:
            print(f"  {YELLOW}[!]{RESET} Verify failed: {e}")
    elif ext in office_exts:
        import zipfile, re
        with zipfile.ZipFile(dst) as z:
            core = [n for n in z.namelist() if "core.xml" in n.lower()]
            for name in core:
                content = z.read(name).decode("utf-8", errors="ignore")
                m = re.search(r"<(?:dc|cp):creator[^>]*>([^<]*)</", content)
                if m and m.group(1).strip():
                    print(f"  {YELLOW}[!]{RESET} {name} still has: creator='{m.group(1)}'")
                else:
                    print(f"  {GREEN}[+]{RESET} {name} looks clean.")
