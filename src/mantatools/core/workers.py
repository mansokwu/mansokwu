"""
Worker classes for background tasks
"""

import os
import tempfile
import zipfile
import shutil
import urllib.request
from PySide6.QtCore import QThread, QObject, Signal
from typing import List, Dict, Any
from pathlib import Path as _Path

from .lua_patch import scan_unpatched_lua, _patch_lua_for_app
from .steam_meta import ensure_types_for
from .steam import find_steam_root, _ensure_steam_dirs, _db_add


class AddToSteamWorker(QThread):
    """Worker for adding games to Steam"""
    progress = Signal(int)            # 0..100
    status = Signal(str)              # message
    finished = Signal(bool, str)      # ok, message

    def __init__(self, appid: int, parent=None):
        super().__init__(parent)
        self.appid = appid
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"

    def run(self):
        try:
            steam_root = find_steam_root()
            if not steam_root:
                self.finished.emit(False, "Steam directory tidak ditemukan (cek instalasi Steam).")
                return

            depotcache, stplugin = _ensure_steam_dirs(steam_root)

            # 1) Download zip
            url = f"https://mellyiscoolaf.pythonanywhere.com/{self.appid}"
            self.status.emit("Downloading…")
            tmpdir = _Path(tempfile.mkdtemp(prefix="manta_zip_"))
            zpath = tmpdir / f"{self.appid}.zip"

            req = urllib.request.Request(url, headers={"User-Agent": self.ua})
            with urllib.request.urlopen(req, timeout=60) as resp, open(zpath, "wb") as f:
                total = int(resp.headers.get("Content-Length") or 0)
                read = 0
                chunk = 1024 * 128
                while True:
                    data = resp.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    read += len(data)
                    if total > 0:
                        self.progress.emit(int(read * 100 / total))

            self.progress.emit(100)
            self.status.emit("Extracting…")

            # 2) Extract
            extract_dir = tmpdir / "unzipped"
            extract_dir.mkdir(parents=True, exist_ok=True)
            moved_files: List[str] = []
            with zipfile.ZipFile(zpath, "r") as zf:
                zf.extractall(extract_dir)

            # 3) Move files
            # Walk all extracted files and move by extension
            for root, dirs, files in os.walk(extract_dir):
                for name in files:
                    src = _Path(root) / name
                    low = name.lower()
                    if low.endswith(".manifest"):
                        dst = depotcache / name
                    elif low.endswith(".lua"):
                        dst = stplugin / name
                    else:
                        continue
                    try:
                        # overwrite
                        if dst.exists():
                            try: 
                                dst.unlink()
                            except Exception: 
                                pass
                        shutil.move(str(src), str(dst))
                        moved_files.append(str(dst))
                    except Exception:
                        # fallback: copy
                        try:
                            shutil.copy2(str(src), str(dst))
                            moved_files.append(str(dst))
                        except Exception:
                            pass

            # Track files in DB
            if moved_files:
                _db_add(self.appid, moved_files)
            else:
                self.finished.emit(False, "ZIP tidak berisi .manifest / .lua yang cocok.")
                shutil.rmtree(tmpdir, ignore_errors=True)
                return

            # Patch Lua for this app
            try:
                patched_count = _patch_lua_for_app(stplugin, self.appid, moved_files)
            except Exception:
                patched_count = 0

            # Clean temp
            shutil.rmtree(tmpdir, ignore_errors=True)

            self.finished.emit(True, f"Berhasil pasang {len(moved_files)} file (.manifest/.lua); patched {patched_count} lua.")
        except Exception as e:
            self.finished.emit(False, f"Gagal: {e!r}")
        finally:
            try:
                # Make sure the thread finishes gracefully
                self.msleep(50)
            except Exception:
                pass




class AuthGate(QObject):
    """Authentication gate for Steam integration"""
    authenticated = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._authenticated = False
    
    def check_auth(self):
        """Check if user is authenticated"""
        # TODO: Implement actual authentication check
        self._authenticated = True
        self.authenticated.emit(True)
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self._authenticated
