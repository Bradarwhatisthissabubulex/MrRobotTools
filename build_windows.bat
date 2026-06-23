@echo off
REM ============================================================
REM  MrRobotTools - one-click Windows .exe build script
REM  Requires: Python 3.8+ and pip on PATH
REM  Output:   dist\MrRobotTools.exe
REM ============================================================

setlocal
cd /d "%~dp0"

echo.
echo [MrRobotTools] Installing dependencies...
python -m pip install --upgrade pip
REM No more requests/urllib3 dependency! We use stdlib urllib via core/http.py.
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo.
echo [MrRobotTools] Building .exe with PyInstaller (--onefile)...
python -m PyInstaller ^
    --onefile ^
    --name MrRobotTools ^
    --console ^
    --collect-all core ^
    --collect-all modules ^
    --hidden-import=core ^
    --hidden-import=core.colors ^
    --hidden-import=core.banner ^
    --hidden-import=core.auth ^
    --hidden-import=core.http ^
    --hidden-import=modules ^
    --hidden-import=modules.pentesting ^
    --hidden-import=modules.pentesting.advanced_scanner ^
    --hidden-import=modules.pentesting.vulnerability_scanner ^
    --hidden-import=modules.pentesting.port_scanner ^
    --hidden-import=modules.pentesting.url_crawler ^
    --hidden-import=modules.pentesting.pinger ^
    --hidden-import=modules.pentesting.host_discovery ^
    --hidden-import=modules.osint ^
    --hidden-import=modules.osint.dorking ^
    --hidden-import=modules.osint.wallet_tracker ^
    --hidden-import=modules.osint.username_tracker ^
    --hidden-import=modules.osint.email_tracker ^
    --hidden-import=modules.osint.email_lookup ^
    --hidden-import=modules.osint.ip_lookup ^
    --hidden-import=modules.osint.phone_lookup ^
    --hidden-import=modules.osint.instagram_lookup ^
    --hidden-import=modules.utils ^
    --hidden-import=modules.utils.metadata_scanner ^
    --hidden-import=modules.utils.metadata_deleter ^
    --hidden-import=modules.utils.website_cloner ^
    --hidden-import=whois ^
    --hidden-import=bs4 ^
    --hidden-import=PIL ^
    --hidden-import=exifread ^
    mrrobot.py

echo.
if exist "dist\MrRobotTools.exe" (
    echo [SUCCESS] Built: dist\MrRobotTools.exe
    echo Copy that file anywhere and double-click to run.
) else (
    echo [ERROR] Build failed. Check the output above.
)

pause
endlocal
