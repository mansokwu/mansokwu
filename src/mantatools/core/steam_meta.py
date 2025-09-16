"""
Steam metadata and app type fetching functionality
"""

import json
import urllib.request
from pathlib import Path as _Path
from typing import List, Dict, Optional

# Cache path for metadata
_META_CACHE_PATH = _Path.home() / ".mantatools_appmeta.json"


def _load_meta_cache():
    """Load metadata cache from disk"""
    try:
        if _META_CACHE_PATH.exists():
            return json.loads(_META_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_meta_cache(d):
    """Save metadata cache to disk"""
    try:
        _META_CACHE_PATH.write_text(json.dumps(d), encoding="utf-8")
    except Exception:
        pass


def _fetch_app_type(appid: int) -> Optional[str]:
    """Fetch app type from Steam API"""
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
        obj = json.loads(data)
        node = obj.get(str(appid), {})
        if node.get("success") and isinstance(node.get("data"), dict):
            return node["data"].get("type")
    except Exception:
        return None
    return None


def ensure_types_for(appids: List[int]) -> Dict[int, str]:
    """Ensure app types are fetched and cached for given appids"""
    cache = _load_meta_cache()
    out = {}
    need = []
    for a in appids:
        t = cache.get(str(a))
        if t is not None:
            out[a] = t
        else:
            need.append(a)
    for a in need:
        t = _fetch_app_type(a) or ""
        cache[str(a)] = t
        out[a] = t
    if need:
        _save_meta_cache(cache)
    return out


def ensure_types_for_cached(appids: List[int]) -> Dict[int, str]:
    """Get app types from cache only (no API calls)"""
    cache = _load_meta_cache()
    out = {}
    for a in appids:
        t = cache.get(str(a))
        out[a] = t if t is not None else ""
    return out
