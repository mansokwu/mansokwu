"""
Core functionality for MantaTools
"""

from .paths import resource_path, _guess_steam_dir, ensure_hid_dll_first_run
from .warmup import TypeWarmupWorker
from .steam_meta import _load_meta_cache, _save_meta_cache, _fetch_app_type, ensure_types_for, ensure_types_for_cached
from .lua_patch import scan_unpatched_lua, _patch_lua_file, _patch_lua_for_app
from .settings import load_user_settings, save_user_settings
from .steam import (find_steam_root, game_install_dir, _library_folders, _ensure_steam_dirs,
                   _collect_appids_from_stplugin, _name_map_for, _db_load, _db_save, 
                   _db_add, _db_list, _db_remove_entries)
from .workers import AddToSteamWorker

__all__ = [
    'resource_path', '_guess_steam_dir', 'ensure_hid_dll_first_run',
    'TypeWarmupWorker', 'ensure_types_for', 'ensure_types_for_cached',
    '_load_meta_cache', '_save_meta_cache', '_fetch_app_type',
    'scan_unpatched_lua', '_patch_lua_file', '_patch_lua_for_app',
    # Removed: delisted/images exports (not used by QML runtime)
    'load_user_settings', 'save_user_settings',
    'find_steam_root', 'game_install_dir', '_library_folders', '_ensure_steam_dirs',
    '_collect_appids_from_stplugin', '_name_map_for', '_db_load', '_db_save', 
    '_db_add', '_db_list', '_db_remove_entries',
    'AddToSteamWorker'
]
