"""
Path utilities and Steam directory detection
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

# Import QMessageBox for error dialogs
try:
    from PySide6.QtWidgets import QMessageBox
except ImportError:
    QMessageBox = None



def resource_path(rel: str) -> str:
    """
    Resolve resource path for PyInstaller or dev-run.
    Looks for file next to the executable (PyInstaller _MEIPASS) or current dir.
    """
    base = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(sys.argv[0])))
    cand = os.path.join(base, rel)
    if os.path.exists(cand):
        return cand
    return rel


def _guess_steam_dir() -> Path:
    """Windows registry lookup; fallbacks to common locations"""
    try:
        import winreg
        for hive in (winreg.HKEY_LOCAL_MACHINE, ):
            for sub in (r"SOFTWARE\Valve\Steam", r"SOFTWARE\WOW6432Node\Valve\Steam"):
                try:
                    with winreg.OpenKey(hive, sub) as k:
                        val, _ = winreg.QueryValueEx(k, "InstallPath")
                        if val and os.path.isdir(val):
                            return Path(val)
                except OSError:
                    pass
    except Exception:
        pass
    for p in (Path(os.environ.get("PROGRAMFILES", "")) / "Steam",
              Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Steam"):
        if p.exists():
            return p
    return Path(r"C:\Program Files (x86)\Steam")


def ensure_hid_dll_first_run(parent=None) -> None:
    """
    Copy hid.dll to Steam root if missing.
    Non-fatal if not on Windows or file not found.
    """
    try:
        steam = _guess_steam_dir()
        target = steam / "hid.dll"
        if target.exists():
            return
        src = Path(resource_path("src/assets/resource/hid.dll"))
        if not src.exists():
            return
        try:
            shutil.copy2(src, target)
        except PermissionError:
            # notify user to run as admin / use installer
            if parent is not None:
                try:
                    QMessageBox.warning(parent, "Permission required",
                                        f"Gagal menyalin ke {target}.\nJalankan sebagai Administrator atau gunakan installer.")
                except Exception:
                    pass
    except Exception:
        # silent fallback
        pass
