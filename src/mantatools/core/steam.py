"""
Steam detection, library management, and game installation functions
"""

import json
import re
import urllib.request
from pathlib import Path as _Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Set, Tuple

# Try Windows registry for Steam detection
try:
    import winreg  # type: ignore
except Exception:
    winreg = None

# Cache paths
_APPNAME_CACHE = _Path.home() / ".mantatools_appnames.json"
_INST_DB = _Path.home() / ".manta_installed_files.json"
_ID_RE = re.compile(r'(\d{3,10})')


def _read_reg_value(path_tuple, name):
    """Read registry value"""
    try:
        if not winreg:
            return None
        root_name, sub = path_tuple
        root = getattr(winreg, root_name)
        key = winreg.OpenKey(root, sub)
        val, _t = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return val
    except Exception:
        return None


def _steam_root_candidates():
    """Get list of possible Steam installation paths"""
    cands = []
    # Registry (Windows)
    reg_paths = [
        ("HKEY_CURRENT_USER", r"Software\Valve\Steam"),
        ("HKEY_LOCAL_MACHINE", r"SOFTWARE\WOW6432Node\Valve\Steam"),
        ("HKEY_LOCAL_MACHINE", r"SOFTWARE\Valve\Steam"),
    ]
    for p in reg_paths:
        v = _read_reg_value(p, "SteamPath")
        if v:
            cands.append(_Path(v))
        v2 = _read_reg_value(p, "InstallPath")
        if v2:
            cands.append(_Path(v2))
    # Common fallbacks
    for p in [
        _Path(r"C:\Program Files (x86)\Steam"),
        _Path(r"C:\Program Files\Steam"),
        _Path.home() / "AppData/Local/Steam",
        _Path.home() / "AppData/Roaming/Steam",
    ]:
        cands.append(p)
    # Dedup while preserving order
    out = []
    seen = set()
    for p in cands:
        sp = str(p.resolve()) if p.exists() else str(p)
        if sp.lower() not in seen:
            seen.add(sp.lower())
            out.append(_Path(sp))
    return out


def find_steam_root() -> Optional[_Path]:
    """Find Steam installation root directory"""
    # Prefer one that has steamapps or Steam.exe
    for p in _steam_root_candidates():
        if p.exists():
            if (p / "steamapps").exists() or (p / "Steam.exe").exists():
                return p
    return None


def _library_folders(steam_root: _Path) -> List[_Path]:
    """Parse libraryfolders.vdf to collect Steam library paths."""
    out = []
    steamapps = steam_root / "steamapps"
    out.append(steamapps)  # default
    vdf = steamapps / "libraryfolders.vdf"
    if not vdf.exists():
        return out
    try:
        txt = vdf.read_text(encoding="utf-8", errors="ignore")
        # Capture lines like: "path" "D:\\SteamLibrary"
        paths = re.findall(r'"\s*path\s*"\s*"([^"]+)"', txt, flags=re.I)
        for p in paths:
            sp = _Path(p.replace("\\\\", "\\"))
            if sp.exists():
                out.append(sp / "steamapps")
    except Exception:
        pass
    # Dedup
    dedup = []
    seen = set()
    for p in out:
        rp = str(p.resolve()) if p.exists() else str(p)
        if rp.lower() not in seen:
            seen.add(rp.lower())
            dedup.append(_Path(rp))
    return dedup


def _parse_installdir(acf_text: str) -> Optional[str]:
    """Parse installdir from ACF file content"""
    m = re.search(r'"\s*installdir\s*"\s*"([^"]+)"', acf_text, flags=re.I)
    return m.group(1).strip() if m else None


def game_install_dir(appid: int) -> Optional[_Path]:
    """Return installed game folder (steamapps/common/installdir) if present."""
    steam_root = find_steam_root()
    if not steam_root:
        return None
    for lib in _library_folders(steam_root):
        manifest = lib / f"appmanifest_{appid}.acf"
        if manifest.exists():
            try:
                txt = manifest.read_text(encoding="utf-8", errors="ignore")
                inst = _parse_installdir(txt)
                if inst:
                    path = lib / "common" / inst
                    return path if path.exists() else path  # maybe not downloaded fully yet
            except Exception:
                continue
    return None


def _ensure_steam_dirs(steam_root: _Path) -> Tuple[_Path, _Path]:
    """Return (depotcache_dir, stplugin_dir) under Steam\\config, ensure exist."""
    cfg = steam_root / "config"
    depotcache = cfg / "depotcache"
    stplugin = cfg / "stplug-in"
    depotcache.mkdir(parents=True, exist_ok=True)
    stplugin.mkdir(parents=True, exist_ok=True)
    return depotcache, stplugin


def _load_name_cache():
    """Load app name cache"""
    try:
        if _APPNAME_CACHE.exists():
            return json.loads(_APPNAME_CACHE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_name_cache(d):
    """Save app name cache"""
    try:
        _APPNAME_CACHE.write_text(json.dumps(d), encoding="utf-8")
    except Exception:
        pass


def _resolve_stplugin_dir() -> Optional[_Path]:
    """Resolve stplug-in directory"""
    root = find_steam_root()
    if not root:
        return None
    _, stp = _ensure_steam_dirs(root)  # auto ensure "Steam\config\stplug-in"
    return stp


def _collect_appids_from_stplugin(stplugin: _Path) -> List[int]:
    """Ambil appid dari semua file .lua di Steam\\config\\stplug-in (by filename)."""
    appids: Set[int] = set()
    try:
        for fp in stplugin.glob("*.lua"):
            # ambil angka di nama file (paling aman & cepat)
            m = _ID_RE.findall(fp.stem)
            for g in m:
                try:
                    a = int(g)
                    if 100 <= a <= 999999999:
                        appids.add(a)
                except Exception:
                    pass
    except Exception:
        pass
    return sorted(appids)


def _fetch_app_name(appid: int, timeout: float = 6.0) -> str:
    """Ambil nama game dari store API (cached)."""
    cache = _load_name_cache()
    key = str(appid)
    if key in cache and cache[key]:
        return cache[key]
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&filters=basic"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        node = data.get(str(appid), {})
        if node.get("success") and isinstance(node.get("data"), dict):
            name = (node["data"].get("name") or f"App {appid}").strip()
        else:
            name = f"App {appid}"
    except Exception:
        name = f"App {appid}"
    cache[key] = name
    _save_name_cache(cache)
    return name


def _name_map_for(appids: List[int]) -> Dict[int, str]:
    """Sequential fallback (kept for compatibility)."""
    out: Dict[int, str] = {}
    for a in appids:
        out[a] = _fetch_app_name(a)
    return out



# ======== Install DB (track files we put) ========

def _db_load():
    """Load installation database"""
    try:
        if _INST_DB.exists():
            return json.loads(_INST_DB.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _db_save(d):
    """Save installation database"""
    try:
        _INST_DB.write_text(json.dumps(d, indent=2), encoding="utf-8")
    except Exception:
        pass


def _db_add(appid: int, files: List[str]):
    """Add files to installation database"""
    d = _db_load()
    key = str(appid)
    if key not in d:
        d[key] = []
    d[key].extend(files)
    _db_save(d)


def _db_list(appid: int) -> List[str]:
    """List files for appid from installation database"""
    d = _db_load()
    return d.get(str(appid), [])


def _db_remove_entries(appid: int, removed: List[str]):
    """Remove entries from installation database"""
    d = _db_load()
    key = str(appid)
    if key in d:
        d[key] = [f for f in d[key] if f not in removed]
        _db_save(d)
