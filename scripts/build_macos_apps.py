from __future__ import annotations

import shutil
import subprocess
import plistlib
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
ICON_DIR = ROOT / "assets" / "icons"
DESKTOP_APP = ROOT / "app" / "desktop_app.py"
LOG_DIR = Path.home() / "Desktop" / "Voice2Text_OnDesktop" / "logs"


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def build_iconset(source_png: Path, name: str) -> Path:
    icns_path = DIST / f"{name}.icns"
    if icns_path.exists():
        icns_path.unlink()
    with Image.open(source_png) as source:
        source.save(
            icns_path,
            format="ICNS",
            sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)],
        )
    return icns_path


def build_on_shell_script() -> str:
    return f"""#!/bin/zsh
export PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin
PYTHON_BIN="$(command -v python3)"
APP_ROOT='{ROOT}'
APP_SCRIPT='{DESKTOP_APP}'
LOG_DIR='{LOG_DIR}'
mkdir -p "$LOG_DIR"
if pgrep -f "$APP_SCRIPT" >/dev/null; then
  exit 0
fi
cd "$APP_ROOT"
exec "$PYTHON_BIN" "$APP_SCRIPT" >> "$LOG_DIR/desktop_app_stdout.log" 2>> "$LOG_DIR/desktop_app_stderr.log"
"""


def build_off_shell_script() -> str:
    return f"""#!/bin/zsh
APP_SCRIPT='{DESKTOP_APP}'
pkill -f "$APP_SCRIPT" || true
"""


def compile_app(app_name: str, shell_script_text: str, icns_path: Path) -> Path:
    app_path = DIST / f"{app_name}.app"
    if app_path.exists():
        shutil.rmtree(app_path)
    contents_dir = app_path / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    macos_dir.mkdir(parents=True)
    resources_dir.mkdir(parents=True)

    executable_name = app_name.replace(" ", "")
    executable_path = macos_dir / executable_name
    write_text(executable_path, shell_script_text)
    executable_path.chmod(0o755)

    icon_name = f"{executable_name}.icns"
    shutil.copy2(icns_path, resources_dir / icon_name)

    plist_path = contents_dir / "Info.plist"
    plist_data = {
        "CFBundleDevelopmentRegion": "English",
        "CFBundleDisplayName": app_name,
        "CFBundleExecutable": executable_name,
        "CFBundleIconFile": executable_name,
        "CFBundleIdentifier": f"com.riteshxsharma.{executable_name.lower()}",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": app_name,
        "CFBundlePackageType": "APPL",
        "CFBundleSignature": "V2TX",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "1",
        "LSUIElement": False,
        "NSPrincipalClass": "NSApplication",
        "NSHighResolutionCapable": True,
    }
    with plist_path.open("wb") as handle:
        plistlib.dump(plist_data, handle)

    write_text(contents_dir / "PkgInfo", "APPL????")
    run(["SetFile", "-a", "C", str(app_path)])
    return app_path


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    on_icns = build_iconset(ICON_DIR / "voice2text_on.png", "voice2text_on")
    off_icns = build_iconset(ICON_DIR / "voice2text_off.png", "voice2text_off")
    on_app = compile_app("Voice2Text On", build_on_shell_script(), on_icns)
    off_app = compile_app("Voice2Text Off", build_off_shell_script(), off_icns)
    print(on_app)
    print(off_app)


if __name__ == "__main__":
    main()
