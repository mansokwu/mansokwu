"""
Settings management for MantaTools
"""

import json
from pathlib import Path as _Path
from typing import Dict, Any


def load_user_settings() -> Dict[str, Any]:
    """Load user settings from file"""
    try:
        settings_file = _Path.home() / ".mantatools_settings.json"
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    
    # Return default settings
    return {
        "auto_patch_scan": True,
        "notify_up_to_date": True,
        "steam_exe": "",
    }


def save_user_settings(settings: Dict[str, Any]) -> bool:
    """Save user settings to file"""
    try:
        settings_file = _Path.home() / ".mantatools_settings.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False