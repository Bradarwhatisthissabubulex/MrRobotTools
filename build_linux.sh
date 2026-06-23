#!/usr/bin/env bash
# Build MrRobotTools Linux ELF binary with PyInstaller (one-file)
# Output: dist/MrRobotTools-Linux
set -e
cd "$(dirname "$0")"

echo "[MrRobotTools] Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

echo ""
echo "[MrRobotTools] Building Linux binary with PyInstaller (--onefile)..."
python3 -m PyInstaller \
    --onefile \
    --name MrRobotTools \
    --console \
    --collect-all core \
    --collect-all modules \
    --hidden-import=core \
    --hidden-import=core.colors \
    --hidden-import=core.banner \
    --hidden-import=core.auth \
    --hidden-import=core.http \
    --hidden-import=modules \
    --hidden-import=modules.pentesting \
    --hidden-import=modules.pentesting.advanced_scanner \
    --hidden-import=modules.pentesting.vulnerability_scanner \
    --hidden-import=modules.pentesting.port_scanner \
    --hidden-import=modules.pentesting.url_crawler \
    --hidden-import=modules.pentesting.pinger \
    --hidden-import=modules.pentesting.host_discovery \
    --hidden-import=modules.osint \
    --hidden-import=modules.osint.dorking \
    --hidden-import=modules.osint.wallet_tracker \
    --hidden-import=modules.osint.username_tracker \
    --hidden-import=modules.osint.email_tracker \
    --hidden-import=modules.osint.email_lookup \
    --hidden-import=modules.osint.ip_lookup \
    --hidden-import=modules.osint.phone_lookup \
    --hidden-import=modules.osint.instagram_lookup \
    --hidden-import=modules.utils \
    --hidden-import=modules.utils.metadata_scanner \
    --hidden-import=modules.utils.metadata_deleter \
    --hidden-import=modules.utils.website_cloner \
    --hidden-import=whois \
    --hidden-import=bs4 \
    --hidden-import=PIL \
    --hidden-import=exifread \
    mrrobot.py

echo ""
if [ -f "dist/MrRobotTools" ]; then
    mv dist/MrRobotTools dist/MrRobotTools-Linux
    chmod +x dist/MrRobotTools-Linux
    echo "[SUCCESS] Built: dist/MrRobotTools-Linux"
    echo "Run it with: ./dist/MrRobotTools-Linux"
    ls -lh dist/MrRobotTools-Linux
else
    echo "[ERROR] Build failed. Check the output above."
    exit 1
fi
