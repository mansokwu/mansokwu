"""
Type warmup functionality for Steam games
"""

from typing import List, Dict, Optional
from PySide6.QtCore import QThread

from .steam_meta import ensure_types_for


class TypeWarmupWorker(QThread):
    """Worker thread for prefetching game types"""
    _pool: set["TypeWarmupWorker"] = set()
    
    def __init__(self, appids, parent=None):
        super().__init__(parent)
        seen = set()
        self.appids = [a for a in appids if not (a in seen or seen.add(a))][:128]
    
    def run(self):
        try:
            ensure_types_for(self.appids)
        except Exception:
            try:
                from mantatools.core.steam_meta import ensure_types_for
                ensure_types_for(self.appids)
            except Exception:
                pass
    
    @staticmethod
    def prefetch(appids):
        if not appids:
            return
        w = TypeWarmupWorker(appids)
        if not w.appids:
            return
        TypeWarmupWorker._pool.add(w)
        w.finished.connect(lambda: TypeWarmupWorker._pool.discard(w))
        w.start()
