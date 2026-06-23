"""[15] File Metadata Scanner - extract EXIF / PDF / Office / file metadata."""

import os
import hashlib
from datetime import datetime

from core.colors import GREEN, DARK_GREEN, GREY, RED, YELLOW, CYAN, BOLD, RESET, hr


def _file_stats(path):
    """Get filesystem metadata for a file."""
    st = os.stat(path)
    return {
        "Size (bytes)": st.st_size,
        "Last modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
        "Created": datetime.fromtimestamp(st.st_ctime).isoformat(),
        "Mode": oct(st.st_mode & 0o777),
        "Inode": st.st_ino,
        "Device": st.st_dev,
    }


def _md5_sha(path):
    """Compute MD5 and SHA-256 hashes."""
    md5 = hashlib.md5()
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            md5.update(chunk)
            sha.update(chunk)
    return md5.hexdigest(), sha.hexdigest()


def _extract_exif(path):
    """Try exifread, then PIL, to extract EXIF tags."""
    try:
        import exifread
        with open(path, "rb") as f:
            tags = exifread.process_file(f, details=False)
        return {str(k): str(v) for k, v in tags.items()}
    except ImportError:
        pass
    except Exception as e:
        return {"_error": f"exifread error: {e}"}

    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(path)
        raw = img._getexif() or {}
        out = {}
        for tag_id, value in raw.items():
            name = TAGS.get(tag_id, tag_id)
            out[name] = str(value)
        return out
    except ImportError:
        return {"_note": "Install exifread or Pillow for EXIF extraction."}
    except Exception as e:
        return {"_error": f"PIL error: {e}"}


def run():
    print(f"\n{BOLD}{DARK_GREEN}[15] FILE METADATA SCANNER{RESET}")
    hr()
    path = input(f"{GREEN}File path: {RESET}").strip().strip('"').strip("'")
    if not path or not os.path.isfile(path):
        print(f"{RED}[-]{RESET} File not found.")
        return

    print(f"\n{CYAN}[i]{RESET} Scanning {BOLD}{path}{RESET}\n")

    # 1. File-system metadata
    print(f"{DARK_GREEN}== File System Metadata =={RESET}")
    stats = _file_stats(path)
    for k, v in stats.items():
        print(f"  {GREEN}{k:<16}:{RESET} {v}")

    # 2. Hashes
    print(f"\n{DARK_GREEN}== Hashes =={RESET}")
    md5, sha = _md5_sha(path)
    print(f"  {GREEN}MD5:{RESET}     {md5}")
    print(f"  {GREEN}SHA-256:{RESET} {sha}")

    # 3. File-type detection
    print(f"\n{DARK_GREEN}== File Type =={RESET}")
    ext = os.path.splitext(path)[1].lower()
    print(f"  {GREEN}Extension:{RESET} {ext or '(none)'}")
    with open(path, "rb") as f:
        magic = f.read(16)
    print(f"  {GREEN}Magic bytes:{RESET} {magic.hex(' ')}")
    print(f"  {GREEN}Magic ASCII:{RESET} {magic.decode('ascii', errors='replace')!r}")

    # 4. EXIF (for images)
    image_exts = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic")
    if ext in image_exts:
        print(f"\n{DARK_GREEN}== EXIF Metadata =={RESET}")
        exif = _extract_exif(path)
        if not exif:
            print(f"  {GREY}[-] No EXIF data found.{RESET}")
        elif "_error" in exif:
            print(f"  {RED}[-]{RESET} {exif['_error']}")
        elif "_note" in exif:
            print(f"  {YELLOW}[!]{RESET} {exif['_note']}")
        else:
            interesting = ["Image Make", "Image Model", "EXIF DateTimeOriginal",
                           "EXIF GPSLatitude", "EXIF GPSLongitude",
                           "EXIF GPSLatitudeRef", "EXIF GPSLongitudeRef",
                           "Image Software", "Image Artist", "Image Copyright"]
            printed = 0
            for k in interesting:
                if k in exif:
                    val = exif[k]
                    if "GPS" in k and "Ref" not in k:
                        print(f"  {GREEN}{k:<22}:{RESET} {val} {exif.get(k + 'Ref', '')}")
                    else:
                        print(f"  {GREEN}{k:<22}:{RESET} {val}")
                    printed += 1
            print(f"\n  {GREY}(Total EXIF tags: {len(exif)}){RESET}")
            if printed < len(exif):
                show_all = input(f"{GREEN}Show all {len(exif)} tags? (y/N): {RESET}").strip().lower()
                if show_all == "y":
                    for k, v in exif.items():
                        print(f"  {GREY}{k:<30} = {v}{RESET}")
    else:
        print(f"\n{GREY}[i] Skipping EXIF extraction (not an image).{RESET}")

    # 5. PDF metadata
    if ext == ".pdf":
        print(f"\n{DARK_GREEN}== PDF Metadata =={RESET}")
        try:
            with open(path, "rb") as f:
                head = f.read(8192)
            for line in head.split(b"\n"):
                line = line.decode("latin-1", errors="ignore").strip()
                if line.startswith(("/Title", "/Author", "/Subject", "/Keywords",
                                    "/Creator", "/Producer", "/CreationDate",
                                    "/ModDate")):
                    print(f"  {GREEN}{line[:100]}{RESET}")
        except Exception as e:
            print(f"  {RED}[-]{RESET} {e}")

    # 6. Office docs
    if ext in (".docx", ".xlsx", ".pptx"):
        print(f"\n{DARK_GREEN}== Office Document Core Properties =={RESET}")
        try:
            import zipfile
            with zipfile.ZipFile(path) as z:
                core = [n for n in z.namelist() if "core.xml" in n.lower() or "app.xml" in n.lower()]
                for name in core:
                    print(f"  {GREY}--- {name} ---{RESET}")
                    content = z.read(name).decode("utf-8", errors="ignore")
                    import re
                    for tag in ("title", "creator", "subject", "description",
                                "keywords", "lastModifiedBy", "revision",
                                "created", "modified"):
                        m = re.search(rf"<(?:dc|cp|dcterms):{tag}[^>]*>([^<]*)</", content)
                        if m and m.group(1).strip():
                            print(f"  {GREEN}{tag:<16}:{RESET} {m.group(1).strip()[:80]}")
        except Exception as e:
            print(f"  {RED}[-]{RESET} {e}")
