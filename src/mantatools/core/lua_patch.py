"""
Lua patch and scan utilities
"""

import re
from pathlib import Path as _Path
from typing import List, Tuple

_LUA_ACTIVE_RE = re.compile(r"^\s*(?!--)setManifestid\s*\(", re.IGNORECASE)


def _iter_lua_candidates(stplugin: _Path, appid: int) -> List[_Path]:
    """Kandidat file .lua untuk appid: <appid>.lua dan *<appid>*.lua (unik)."""
    if not stplugin or not stplugin.exists():
        return []
    pats = [f"{appid}.lua", f"*{appid}*.lua"]
    files: List[_Path] = []
    for pat in pats:
        try:
            files.extend([fp for fp in stplugin.glob(pat) if fp.is_file() and fp.suffix.lower() == ".lua"])
        except Exception:
            pass
    # unik
    seen, uniq = set(), []
    for f in files:
        k = f.resolve().as_posix().lower()
        if k not in seen:
            uniq.append(f)
            seen.add(k)
    return uniq


def scan_unpatched_lua(stplugin: _Path, appid: int) -> Tuple[int, int, List[Tuple[_Path, int]]]:
    """
    Return (lua_count, unpatched_count, detail)
      - lua_count        : jumlah file .lua yg relevan utk appid
      - unpatched_count  : jumlah baris aktif setManifestid(...) di semua file
      - detail           : [(path, unpatched_lines), ...] hanya file dgn unpatched>0
    """
    candidates = _iter_lua_candidates(stplugin, appid)
    lua_count = len(candidates)
    total = 0
    detail: List[Tuple[_Path, int]] = []
    for fp in candidates:
        try:
            cnt = 0
            for line in fp.read_text(encoding="utf-8", errors="ignore").splitlines():
                if _LUA_ACTIVE_RE.match(line):
                    cnt += 1
            if cnt > 0:
                detail.append((fp, cnt))
                total += cnt
        except Exception:
            continue
    return lua_count, total, detail


def _patch_lua_file(path: _Path) -> bool:
    """Comment setiap baris aktif setManifestid(...). Return True jika terjadi perubahan."""
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        changed = False
        for i, line in enumerate(lines):
            s = line.lstrip()
            if s.lower().startswith("setmanifestid") and not s.startswith("--"):
                lines[i] = "--" + line
                changed = True
        if changed:
            path.write_text("\n".join(lines), encoding="utf-8")
        return changed
    except Exception:
        return False


def _patch_lua_for_app(stplugin: _Path, appid: int, moved_files: List[str]) -> int:
    """Patch hanya file yg relevan (baru dipindah / mengandung appid). Return jumlah file yg berubah."""
    candidates: List[_Path] = []
    seen = set()

    # dari file yang baru dipindah
    for p in moved_files:
        try:
            if p.lower().endswith(".lua"):
                fp = _Path(p)
                k = fp.resolve().as_posix().lower()
                if k not in seen:
                    candidates.append(fp)
                    seen.add(k)
        except Exception:
            pass

    # main & varian
    for fp in _iter_lua_candidates(stplugin, appid):
        k = fp.resolve().as_posix().lower()
        if k not in seen:
            candidates.append(fp)
            seen.add(k)

    patched = 0
    for fp in candidates:
        if _patch_lua_file(fp):
            patched += 1
    return patched
