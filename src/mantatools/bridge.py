"""
QML Bridge for MantaTools - Connects Python backend with QML frontend
"""

from PySide6.QtCore import QObject, Signal, Property, Slot
import json
import urllib.request
import urllib.error
import threading
from PySide6.QtQml import qmlRegisterType
import subprocess
import time
import re
import queue
import urllib.parse
import html as _html
import glob
from .core.workers import AddToSteamWorker
from .ui.auth_gate import AuthGate
from .core.steam import find_steam_root, game_install_dir
from .core.steam_meta import ensure_types_for_cached
from .core.warmup import TypeWarmupWorker
from pathlib import Path as _Path


# ===== Local caches for extra metadata (genres) =====
_GENRE_CACHE_PATH = _Path.home() / ".mantatools_genres.json"
_SYSREQ_CACHE_PATH = _Path.home() / ".mantatools_sysreq.json"


def _load_genre_cache():
    try:
        if _GENRE_CACHE_PATH.exists():
            return json.loads(_GENRE_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_genre_cache(d):
    try:
        _GENRE_CACHE_PATH.write_text(json.dumps(d), encoding="utf-8")
    except Exception:
        pass


def _load_sysreq_cache():
    """Load system requirements cache from disk"""
    try:
        if _SYSREQ_CACHE_PATH.exists():
            return json.loads(_SYSREQ_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _save_sysreq_cache(d):
    """Save system requirements cache to disk"""
    try:
        _SYSREQ_CACHE_PATH.write_text(json.dumps(d), encoding="utf-8")
    except Exception:
        pass


class QMLBridge(QObject):
    """Main QML Bridge for connecting Python backend with QML frontend"""
    
    # Signals
    gamesLoaded = Signal(list)
    gameDetailsLoaded = Signal(int, dict)
    progressUpdated = Signal(int)
    statusUpdated = Signal(str)
    addToSteamFinished = Signal(bool, str)
    errorOccurred = Signal(str)
    patchStatusUpdated = Signal(str, str)  # status, variant
    # Settings signals temporarily disabled
    
    # Steam API signals (forwarded from SteamAPI)
    steamGamesLoaded = Signal(list)
    steamErrorOccurred = Signal(str)
    librarySyncStarted = Signal()
    librarySyncProgress = Signal(int, int)
    librarySyncGameProgress = Signal(int, int, str)
    librarySyncFinished = Signal(list)
    loadingStarted = Signal()  # Signal untuk memulai loading
    loadingFinished = Signal()  # Signal untuk selesai loading
    
    # Properties
    steamApi = Property(QObject, lambda self: self._steamApi, constant=True)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._steamApi = SteamAPI()
        self._steamApi.setQMLBridge(self)
        # Settings and file manager temporarily disabled
        
        # Check and install hid.dll on startup
        self._check_and_install_hid_dll()
        
        # Connect SteamAPI signals to QMLBridge signals
        print("Connecting SteamAPI signals to QMLBridge...")
        self._steamApi.gamesLoaded.connect(self.steamGamesLoaded.emit)
        self._steamApi.errorOccurred.connect(self.steamErrorOccurred.emit)
        self._steamApi.librarySyncStarted.connect(self.librarySyncStarted.emit)
        self._steamApi.librarySyncProgress.connect(self.librarySyncProgress.emit)
        self._steamApi.librarySyncGameProgress.connect(self.librarySyncGameProgress.emit)
        self._steamApi.librarySyncFinished.connect(self.librarySyncFinished.emit)
        self._steamApi.loadingStarted.connect(self.loadingStarted.emit)
        self._steamApi.loadingFinished.connect(self.loadingFinished.emit)
        print("SteamAPI signals connected successfully")
    
    @Slot()
    def loadGames(self):
        """Load games from Steam"""
        self._steamApi.loadGames()
    
    def _check_and_install_hid_dll(self):
        """Check and install hid.dll to Steam directory on first run"""
        try:
            # Get Steam root directory
            steam_root = find_steam_root()
            if not steam_root:
                print("Steam directory not found, skipping hid.dll installation")
                return
            
            # Source path for hid.dll
            source_path = _Path(__file__).parent.parent.parent / "src" / "assets" / "resource" / "hid.dll"
            if not source_path.exists():
                print("hid.dll not found in resources, skipping installation")
                return
            
            # Destination path in Steam directory
            dest_path = steam_root / "hid.dll"
            
            # Check if hid.dll already exists in Steam directory
            if dest_path.exists():
                print("hid.dll already exists in Steam directory")
                return
            
            # Copy hid.dll to Steam directory
            import shutil
            shutil.copy2(str(source_path), str(dest_path))
            print(f"hid.dll successfully installed to Steam directory: {dest_path}")
            
        except Exception as e:
            print(f"Error installing hid.dll: {e}")
    
    @Slot()
    def showAuthGate(self):
        """Show authentication gate dialog"""
        try:
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                print("Creating AuthGate dialog...")
                auth_dialog = AuthGate()
                print("AuthGate dialog created, showing...")
                result = auth_dialog.exec_and_passed()
                print(f"AuthGate result: {result}")
                return result
        except Exception as e:
            print(f"Error showing auth gate: {e}")
            import traceback
            traceback.print_exc()
        return False
    
    # Authentication signals
    authenticationSuccess = Signal()
    authenticationFailed = Signal(str)
    
    @Slot(str)
    def authenticateUser(self, token):
        """Authenticate user with token from QML (asynchronous)"""
        print(f"authenticateUser called with token: {token[:10]}...")
        
        def _authenticate():
            try:
                print(f"Starting authentication thread for token: {token[:10]}...")
                
                # Import AuthGate for authentication logic
                from .ui.auth_gate import AuthGate
                
                # Create temporary AuthGate instance for authentication
                auth_gate = AuthGate()
                
                # Use the authentication logic
                payload = {"code": token, "device": auth_gate._fingerprint()}
                print(f"Sending authentication request...")
                status, body = auth_gate._api_post_json(auth_gate.VERIFY_PATH, payload)
                print(f"Authentication response: status={status}, body={body}")
                
                if status == 200 and isinstance(body, dict) and body.get("valid") is True:
                    print("Authentication successful! Emitting success signal...")
                    self.authenticationSuccess.emit()
                else:
                    msg = (body.get("detail") if isinstance(body, dict) else None) \
                          or ("Server auth tidak bisa dihubungi." if status == 0 else "Token tidak valid.")
                    print(f"Authentication failed: {msg}. Emitting failed signal...")
                    self.authenticationFailed.emit(msg)
                    
            except Exception as e:
                print(f"Error during authentication: {e}")
                import traceback
                traceback.print_exc()
                self.authenticationFailed.emit(f"Error: {e}")
        
        # Run authentication in background thread
        print("Starting authentication thread...")
        threading.Thread(target=_authenticate, daemon=True).start()
    
    @Slot(int)
    def loadGameDetails(self, appid):
        """Load game details"""
        self._steamApi.loadGameDetails(appid)
    
    @Slot(int)
    def addGameToSteam(self, appid):
        """Add game to Steam"""
        self._steamApi.addGameToSteam(appid)
    
    # Settings methods temporarily disabled


class SteamAPI(QObject):
    """Steam API wrapper for QML"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.qmlBridge = None
        self.allGames = []  # Cache semua games
        self.isLoading = False
        # Cache ketersediaan header image per appid
        self.imageAvailabilityCache = {}
        self._queuedAppids = set()
        self._imageCheckQueue = queue.PriorityQueue()
        self._imageWorkers = []
        self.appidToGame = {}
        self.verifiedGames = []
        # In-memory cache untuk tipe app (mempercepat filter Games Only)
        self._typeCache = {}
        # CDN hosts untuk header image
        self._headerHosts = [
            "https://cdn.akamai.steamstatic.com/steam/apps/",
            "https://steamcdn-a.akamaihd.net/steam/apps/",
        ]
        self._httpHeaders = {"User-Agent": "Mozilla/5.0", "Accept": "image/*"}
        # Genres metadata cache
        self._genreCache = _load_genre_cache()
        self._genreFetching = set()
        # System requirements cache (in-memory + disk)
        self._sysreqCache = _load_sysreq_cache()
        self._sysreqFetching = set()
        # Game names cache for faster sync
        self._gameNamesCache = {}
        # Keep strong refs to running QThreads to avoid premature destruction
        self._activeWorkers = []
        # Disable Steam network hits (store API/CDN) if requested
        self._noSteamNetwork = False
    
    # Emitted to QML listeners (GameListPage connects to qmlBridge.steamApi)
    gamesLoaded = Signal(list)
    errorOccurred = Signal(str)
    imageCacheUpdated = Signal()
    metaCacheUpdated = Signal()
    librarySyncStarted = Signal()
    librarySyncProgress = Signal(int, int)  # current, total
    librarySyncGameProgress = Signal(int, int, str)  # current, total, game_name
    librarySyncFinished = Signal(list)  # user library
    loadingStarted = Signal()  # Signal untuk memulai loading
    loadingFinished = Signal()  # Signal untuk selesai loading
    
    def setQMLBridge(self, bridge):
        """Set reference to QML bridge for signal emission"""
        self.qmlBridge = bridge
    
    # Expose flag to QML: avoid any request to Steam domains
    def _get_noSteamNetwork(self):
        return self._noSteamNetwork
    def _set_noSteamNetwork(self, v):
        try:
            self._noSteamNetwork = bool(v)
        except Exception:
            self._noSteamNetwork = True
    noSteamNetwork = Property(bool, _get_noSteamNetwork, _set_noSteamNetwork)
    
    @Slot()
    def loadGames(self):
        """Load all games from GitHub repository and emit to QML"""
        if self.isLoading:
            return
            
        def _worker():
            try:
                self.isLoading = True
                print("Memulai loading semua games dari GitHub repository...")
                
                # Emit signal loading started
                self.loadingStarted.emit()
                if self.qmlBridge:
                    self.qmlBridge.loadingStarted.emit()

                # URL untuk raw file dari GitHub repository
                github_url = "https://raw.githubusercontent.com/mansokwu/applist/main/applist.json"
                
                # Headers untuk request
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json"
                }
                
                print(f"Memuat applist dari: {github_url}")
                
                # Buat request ke GitHub
                req = urllib.request.Request(github_url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = json.loads(response.read().decode("utf-8"))

                # Dukungan dua format:
                # 1) Format resmi: {"applist": {"apps": [{"appid": 10, "name": "..."}, ...]}}
                # 2) Format map sederhana: {"10": "Half-Life", "20": "...", ...}
                apps = None
                try:
                    maybe_list = data.get("applist", {}).get("apps") if isinstance(data, dict) else None
                except Exception:
                    maybe_list = None
                if isinstance(maybe_list, list) and maybe_list:
                    apps = maybe_list
                else:
                    # Coba map di bawah key applist.apps (jika dict)
                    mapping = None
                    if isinstance(data, dict):
                        try:
                            node = data.get("applist")
                            if isinstance(node, dict) and isinstance(node.get("apps"), dict):
                                mapping = node.get("apps")
                        except Exception:
                            mapping = None
                        if mapping is None:
                            mapping = data
                    if isinstance(mapping, dict):
                        apps = [{"appid": k, "name": v} for k, v in mapping.items()]
                    else:
                        apps = []

                print(f"Ditemukan {len(apps)} apps dari GitHub repository")
                
                out = []
                seen = set()
                processed = 0
                
                for it in apps:
                    name = (it.get("name") or "").strip()
                    appid = it.get("appid")
                    
                    try:
                        appid = int(appid)
                    except Exception:
                        continue
                    
                    # Filter out invalid entries
                    if not name or appid <= 0:
                        continue

                    # Heuristik cepat: skip judul yang jelas bukan game untuk kurangi dataset awal
                    try:
                        sname = name.lower()
                        if (" dlc" in sname or sname.startswith("dlc ") or
                            " demo" in sname or sname.endswith(" demo") or
                            "soundtrack" in sname or " ost" in sname or
                            "pre-purchase" in sname or "pre purchase" in sname or "prepurchase" in sname or
                            "season pass" in sname or
                            " beta" in sname or sname.endswith(" beta") or
                            " alpha" in sname or sname.endswith(" alpha") or
                            " editor" in sname or sname.endswith(" editor") or
                            "benchmark" in sname or
                            sname.endswith(" trailer") or sname.endswith(" teaser") or
                            " dedicated server" in sname or "test server" in sname):
                            continue
                    except Exception:
                        pass
                    
                    # Skip duplicates
                    key = (appid, name)
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    # Add to results
                    out.append({"title": name, "appid": appid})
                    processed += 1
                    
                    # Progress update setiap 1000 games
                    if processed % 1000 == 0:
                        print(f"Processed {processed} games...")
                
                # Jangan sort: pertahankan urutan sesuai baris di file sumber

                print(f"Total games yang berhasil dimuat: {len(out)}")
                
                # Simpan ke cache
                self.allGames = out
                # Reset cache image saat dataset berubah
                self.imageAvailabilityCache = {}
                self._queuedAppids = set()
                self.appidToGame = {g["appid"]: g for g in out}
                self.verifiedGames = []
                try:
                    # Warmup sebagian app type agar filter Games Only akurat sejak awal
                    TypeWarmupWorker.prefetch([g["appid"] for g in out[:256]])
                except Exception:
                    pass
                
                # Prefetch sebagian tipe dan isi cache memori agar filter cepat (non-blocking untuk UI)
                try:
                    head_appids = [g["appid"] for g in out[:512]]
                    TypeWarmupWorker.prefetch(head_appids)
                except Exception:
                    pass
                
                # Prefetch system requirements untuk game populer (background)
                try:
                    self._prefetch_sysreq_for_popular_games(out[:50])
                except Exception:
                    pass

                # Emit signal untuk QML (tanpa payload besar agar UI tidak freeze)
                print(f"Emitting gamesLoaded signal (notify only)")
                self.gamesLoaded.emit([])
                if self.qmlBridge:
                    print(f"Emitting QMLBridge gamesLoaded signal (notify only)")
                    self.qmlBridge.gamesLoaded.emit([])
                
                # Mulai pemindaian awal header image secara paralel dan masif
                try:
                    self._ensure_image_workers()
                    # Prioritaskan sebagian besar entri teratas agar halaman 1 cepat terisi
                    self._queue_checks_for_candidates((g for g in self.allGames), limit=50000, priority=1)
                except Exception:
                    pass
                    
            except Exception as e:
                msg = f"Gagal memuat daftar game dari GitHub: {e}"
                print(f"Error: {msg}")
                self.errorOccurred.emit(msg)
                if self.qmlBridge:
                    self.qmlBridge.errorOccurred.emit(msg)
            finally:
                self.isLoading = False
                print("Loading selesai")
                
                # Emit signal loading finished
                self.loadingFinished.emit()
                if self.qmlBridge:
                    self.qmlBridge.loadingFinished.emit()
                
        threading.Thread(target=_worker, daemon=True).start()
    
    @Slot(str, int, int, result=list)
    @Slot(str, int, int, bool, result=list)
    def searchGames(self, searchText, page, pageSize, withImageOnly=False):
        """Search games dengan pagination.
        Jika withImageOnly=True, hanya kembalikan game yang benar-benar memiliki header image.
        """
        if not self.allGames:
            return []

        searchText = (searchText or "").strip().lower()

        # Generator kandidat untuk mode withImageOnly (gunakan Games Only heuristik)
        if searchText:
            def _candidates():
                for game in self.allGames:
                    if not self._is_game_only(game):
                        continue
                    if (searchText in game["title"].lower() or searchText in str(game["appid"])):
                        yield game
        else:
            def _candidates():
                for game in self.allGames:
                    if self._is_game_only(game):
                        yield game

        start_index = max(0, (page - 1) * pageSize)
        end_index = start_index + pageSize

        if not withImageOnly:
            # Pertahankan urutan asli sesuai file; tanpa filter tipe. Hanya filter keyword jika ada.
            if not searchText:
                try:
                    return self.allGames[start_index:end_index]
                except Exception:
                    return []
            pool = []
            pool_limit = min(end_index * 4, 20000)
            for g in self.allGames:
                if (searchText in g["title"].lower() or searchText in str(g["appid"])):
                    pool.append(g)
                    if len(pool) >= pool_limit:
                        break
            return pool[start_index:end_index]

        # withImageOnly=True → pertahankan urutan asli, filter hanya yang punya header image (berdasar cache)
        self._ensure_image_workers()
        # Antrikan cek untuk kandidat agar cache terisi di background
        try:
            var_limit = max(20000, pageSize * (page + 120))
        except Exception:
            var_limit = 20000
        self._queue_checks_for_candidates(_candidates(), limit=min(30000, var_limit), priority=1)

        search = (searchText or "").strip().lower()
        ordered_matched = []
        for g in self.allGames:
            # Games Only + search match
            if search and (search not in g["title"].lower() and search not in str(g["appid"])):
                continue
            if not self._is_game_only(g):
                continue
            try:
                aid = int(g.get("appid", 0))
            except Exception:
                continue
            if not self.imageAvailabilityCache.get(aid):
                continue
            ordered_matched.append(g)
        return ordered_matched[start_index:end_index]

    # Convenience APIs (avoid overload ambiguity in QML)
    @Slot(str, int, int, result=list)
    def searchGamesFiltered(self, searchText, page, pageSize):
        # Paginasi langsung dari verifiedGames agar halaman 1 cepat terisi dengan item ber-image
        search = (searchText or "").strip().lower()
        start_index = max(0, (page - 1) * pageSize)
        end_index = start_index + pageSize
        matched = []
        for g in self.verifiedGames:
            if search and (search not in g["title"].lower() and search not in str(g["appid"])):
                continue
            matched.append(g)
        return matched[start_index:end_index]

    def _has_header_image(self, appid: int) -> bool:
        """Cek cepat apakah header.jpg tersedia untuk appid tertentu (cached)."""
        cached = self.imageAvailabilityCache.get(appid)
        if cached is not None:
            return cached

        exists = False
        for base in self._headerHosts:
            url = f"{base}{appid}/header.jpg"
            if self._url_image_exists(url):
                exists = True
                break
        self.imageAvailabilityCache[appid] = exists
        return exists

    def _url_image_exists(self, url: str, timeout: float = 2.5) -> bool:
        """Kembalikan True jika CDN mengembalikan 200/206 untuk HEAD atau GET Range."""
        # Coba HEAD terlebih dahulu
        try:
            try:
                req = urllib.request.Request(url, headers=self._httpHeaders, method='HEAD')
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    code = getattr(resp, 'status', None) or resp.getcode()
                    if code in (200, 206):
                        return True
            except TypeError:
                # Python tanpa dukungan method= → gunakan subclass Request
                class _HeadRequest(urllib.request.Request):
                    def get_method(self):
                        return 'HEAD'
                req = _HeadRequest(url, headers=self._httpHeaders)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    code = getattr(resp, 'status', None) or resp.getcode()
                    if code in (200, 206):
                        return True
        except Exception:
            pass

        # Fallback: GET hanya 1 byte via Range
        try:
            req2 = urllib.request.Request(url, headers=dict(self._httpHeaders))
            req2.add_header('Range', 'bytes=0-0')
            with urllib.request.urlopen(req2, timeout=timeout) as resp2:
                code = getattr(resp2, 'status', None) or resp2.getcode()
                return code in (200, 206)
        except Exception:
            return False

    # ===== Background image-check worker =====
    def _ensure_image_workers(self, num_workers: int = 16):
        # Start a pool of background workers if not already running
        alive = [t for t in getattr(self, "_imageWorkers", []) if t.is_alive()]
        self._imageWorkers = alive
        if len(self._imageWorkers) >= num_workers:
            return
        def _worker():
            while True:
                try:
                    prio, appid = self._imageCheckQueue.get(timeout=0.5)
                except queue.Empty:
                    continue
                if appid is None:
                    break
                if appid in self.imageAvailabilityCache:
                    continue
                exists = self._has_header_image(appid)
                self.imageAvailabilityCache[appid] = exists
                if exists:
                    try:
                        g = next((x for x in self.allGames if x.get("appid") == appid), None)
                        if g is not None and self._is_game_only(g):
                            self.verifiedGames.append(g)
                    except Exception:
                        pass
                # Beri tahu pendengar bahwa cache berubah agar UI bisa refresh
                try:
                    self.imageCacheUpdated.emit()
                except Exception:
                    pass
        for _ in range(num_workers - len(self._imageWorkers)):
            t = threading.Thread(target=_worker, daemon=True)
            t.start()
            self._imageWorkers.append(t)

    def _queue_checks_for_candidates(self, candidates, limit=500, priority: int = 10):
        """Enqueue appid dari candidates hingga limit item baru untuk pengecekan gambar.
        Prioritas lebih kecil diproses lebih dulu.
        """
        added = 0
        for g in candidates:
            if added >= limit:
                break
            try:
                appid = int(g.get("appid", 0))
            except Exception:
                continue
            if appid <= 0:
                continue
            if appid in self.imageAvailabilityCache or appid in self._queuedAppids:
                continue
            try:
                self._imageCheckQueue.put_nowait((priority, appid))
                self._queuedAppids.add(appid)
                added += 1
            except Exception:
                break

    def _types_for_appids(self, appids):
        """Ambil tipe app untuk sekumpulan appid memakai in-memory cache + cache disk (tanpa jaringan)."""
        out = {}
        to_fetch = []
        for a in appids:
            try:
                aid = int(a)
            except Exception:
                continue
            t = self._typeCache.get(aid)
            if t is None:
                to_fetch.append(aid)
            else:
                out[aid] = t
        if to_fetch:
            try:
                typed = ensure_types_for_cached(to_fetch)
                for aid, t in typed.items():
                    tt = t or ""
                    out[int(aid)] = tt
                    try:
                        self._typeCache[int(aid)] = tt
                    except Exception:
                        pass
            except Exception:
                for aid in to_fetch:
                    out[aid] = ""
        return out

    # ===== Genres metadata =====
    @Slot(int, result=str)
    def getGenres(self, appid):
        try:
            aid = int(appid)
        except Exception:
            return ""
        g = self._genreCache.get(str(aid)) or self._genreCache.get(aid)
        if g:
            if isinstance(g, list):
                return ", ".join([x for x in g if x])
            return str(g)
        self._schedule_genre_fetch(aid)
        return ""

    def _schedule_genre_fetch(self, appid: int):
        if appid in self._genreFetching:
            return
        self._genreFetching.add(appid)
        def _worker():
            try:
                genres = self._fetch_app_genres(appid)
                if genres is None:
                    genres = []
                self._genreCache[str(appid)] = genres
                _save_genre_cache(self._genreCache)
                try:
                    self.metaCacheUpdated.emit()
                except Exception:
                    pass
            except Exception:
                pass
            finally:
                try:
                    self._genreFetching.discard(appid)
                except Exception:
                    pass
        threading.Thread(target=_worker, daemon=True).start()

    def _fetch_app_genres(self, appid: int):
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            node = data.get(str(appid), {})
            if node.get("success") and isinstance(node.get("data"), dict):
                genres = node["data"].get("genres")
                if isinstance(genres, list):
                    out = []
                    for it in genres[:4]:
                        try:
                            name = (it.get("description") or it.get("name") or "").strip()
                            if name:
                                out.append(name)
                        except Exception:
                            continue
                    return out
        except Exception:
            return None
        return None

    def _fetch_sysreq_from_web(self, title: str, appid: int) -> dict:
        """Fast fetch of system requirements via web search with aggressive caching.
        Returns {"minimum": str, "recommended": str} with HTML-friendly content.
        """
        # Check cache first (instant return)
        cache_key = f"{appid}_{title.lower().strip()}"
        cached = self._sysreqCache.get(cache_key)
        if cached and isinstance(cached, dict):
            if cached.get("minimum") or cached.get("recommended"):
                return cached
        
        # Avoid duplicate fetches
        if appid in self._sysreqFetching:
            return {"minimum": "", "recommended": ""}
        
        self._sysreqFetching.add(appid)
        
        def _http_get_fast(url: str, timeout: float = 3.0) -> str:
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept-Language": "en-US,en;q=0.8",
                })
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    return resp.read().decode("utf-8", errors="ignore")
            except Exception:
                return ""

        def _clean_html(s: str) -> str:
            try:
                txt = _html.unescape(s or "")
                txt = txt.replace("\r", "").replace("\n", "<br>")
                txt = re.sub(r"\sstyle=\"[^\"]*\"", "", txt, flags=re.I)
                txt = re.sub(r"<\s*style[^>]*>[\s\S]*?<\/\s*style\s*>", "", txt, flags=re.I)
                txt = re.sub(r"<\s*li\s*>", "• ", txt, flags=re.I)
                txt = re.sub(r"<\s*\/\s*li\s*>", "<br>", txt, flags=re.I)
                # Keep only a few tags
                txt = re.sub(r"<(?!br\b|/br\b|b\b|/b\b|strong\b|/strong\b)[^>]+>", "", txt, flags=re.I)
                return txt
            except Exception:
                return s or ""

        def _extract_fast(html: str) -> dict:
            if not html:
                return {"minimum": "", "recommended": ""}
            h = html
            # Fast patterns - prioritize common structures
            patterns = [
                # Most common: PCGamingWiki style
                (r"Minimum requirements[\s\S]{0,200}?(<ul[\s\S]*?</ul>)", r"Recommended requirements[\s\S]{0,300}?(<ul[\s\S]*?</ul>)"),
                # Generic system requirements
                (r"Minimum system requirements[\s\S]{0,200}?(<ul[\s\S]*?</ul>)", r"Recommended system requirements[\s\S]{0,300}?(<ul[\s\S]*?</ul>)"),
                # Fallback patterns
                (r">\s*Minimum\s*<[^>]*>[\s\S]{0,100}?(<ul[\s\S]*?</ul>)", r">\s*Recommended\s*<[^>]*>[\s\S]{0,150}?(<ul[\s\S]*?</ul>)"),
                (r"Minimum[\s\S]{0,150}?(<ul[\s\S]*?</ul>)", r"Recommended[\s\S]{0,200}?(<ul[\s\S]*?</ul>)"),
            ]
            min_html = ""
            rec_html = ""
            for pmin, prec in patterns:
                try:
                    m1 = re.search(pmin, h, flags=re.I)
                    m2 = re.search(prec, h, flags=re.I)
                    if m1 and not min_html:
                        min_html = m1.group(1)
                    if m2 and not rec_html:
                        rec_html = m2.group(1)
                    if (min_html and len(min_html) > 15) or (rec_html and len(rec_html) > 15):
                        break
                except Exception:
                    continue
            return {"minimum": _clean_html(min_html), "recommended": _clean_html(rec_html)}

        def _google_search_fast(q: str, num: int = 4) -> list:
            try:
                url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(q) + "&hl=en&num=" + str(num)
                html = _http_get_fast(url, timeout=2.5)
                if not html:
                    return []
                # Extract external result URLs from "/url?q=..."
                urls = re.findall(r"/url\?q=([^&]+)&", html)
                out = []
                for u in urls:
                    try:
                        uu = urllib.parse.unquote(u)
                    except Exception:
                        uu = u
                    if any(dom in uu for dom in ["google.com", "webcache.googleusercontent.com", "steamcommunity.com", "store.steampowered.com"]):
                        continue
                    out.append(uu)
                # Dedup while preserving order
                seen = set(); dedup = []
                for u in out:
                    if u in seen:
                        continue
                    seen.add(u)
                    dedup.append(u)
                return dedup[:num]
            except Exception:
                return []

        title = (title or "").strip()
        if not title:
            title = f"App {appid}"
        
        # Fast queries - fewer, more targeted
        queries = [
            f"{title} system requirements",
            f"{title} PC requirements",
        ]
        
        # Prioritize fastest domains
        fast_domains = [
            "pcgamingwiki.com",
            "pcgamebenchmark.com", 
            "gamedebate.com",
            "systemrequirements.com",
        ]
        
        results = []
        for q in queries:
            hits = _google_search_fast(q, num=3)
            if hits:
                results.extend(hits)
        
        # Prioritize fast domains
        prioritized = [u for u in results if any(d in u for d in fast_domains)]
        others = [u for u in results if u not in prioritized]
        ordered = prioritized + others
        
        out = {"minimum": "", "recommended": ""}
        
        # Try only top 3 URLs for speed
        for u in ordered[:3]:
            html = _http_get_fast(u, timeout=2.0)
            ex = _extract_fast(html)
            if (ex.get("minimum") and len(ex["minimum"]) > 20) or (ex.get("recommended") and len(ex["recommended"]) > 20):
                out = ex
                break
        
        # Cache the result
        try:
            self._sysreqCache[cache_key] = out
            _save_sysreq_cache(self._sysreqCache)
        except Exception:
            pass
        
        # Remove from fetching set
        try:
            self._sysreqFetching.discard(appid)
        except Exception:
            pass
        
        return out
    
    def _prefetch_sysreq_for_popular_games(self, games: list):
        """Prefetch system requirements for popular games in background"""
        def _worker():
            for game in games:
                try:
                    appid = game.get("appid", 0)
                    title = game.get("title", "").strip()
                    if appid > 0 and title:
                        # Check if already cached
                        cache_key = f"{appid}_{title.lower().strip()}"
                        if cache_key not in self._sysreqCache:
                            # Fetch in background (non-blocking)
                            self._fetch_sysreq_from_web(title, appid)
                except Exception:
                    continue
        threading.Thread(target=_worker, daemon=True).start()
    
    @Slot(str, result=int)
    @Slot(str, bool, result=int)
    def getTotalGamesCount(self, searchText, withImageOnly=False):
        """Get total count of filtered games.
        Jika withImageOnly=True, hitung hanya yang memiliki header image.
        """
        if not self.allGames:
            return 0

        searchText = (searchText or "").strip().lower()

        # Super fast path: startup (no search) and not filtering by image → jangan scan besar
        if not withImageOnly and not searchText:
            try:
                return sum(1 for g in self.allGames if self._is_game_only(g))
            except Exception:
                return 0

        # Fast path: withImageOnly + tanpa kata kunci → hindari scan full dataset
        if withImageOnly and not searchText:
            self._ensure_image_workers()
            try:
                if not getattr(self, "_initialWarmQueued", False):
                    self._initialWarmQueued = True
                    # Antrikan sebagian besar kandidat secara bertahap di background
                    self._queue_checks_for_candidates((g for g in self.allGames), limit=50000, priority=2)
            except Exception:
                pass
            # verifiedGames sudah difilter Games Only saat worker menambahkan entri
            return len(self.verifiedGames)

        def _matches(g):
            # Games Only filter
            if not self._is_game_only(g):
                return False
            if not searchText:
                return True
            return (searchText in g["title"].lower() or searchText in str(g["appid"]))

        if not withImageOnly:
            return sum(1 for g in self.allGames if _matches(g))

        # withImageOnly=True → hitung berdasarkan cache image (non-blocking) dengan urutan asli
        self._ensure_image_workers()
        def _iter_for_queue():
            for g in self.allGames:
                if _matches(g):
                    yield g
        # Hangatkan cache untuk subset kandidat
        self._queue_checks_for_candidates(_iter_for_queue(), limit=50000, priority=2)

        total = 0
        for g in self.allGames:
            if not _matches(g):
                continue
            try:
                aid = int(g.get("appid", 0))
            except Exception:
                continue
            if self.imageAvailabilityCache.get(aid):
                total += 1
        return total

    # ===== Games Only filter helpers =====
    def _is_game_only(self, game: dict) -> bool:
        """Kembalikan True hanya untuk entri bertipe 'game'.
        Gunakan cache tipe jika ada, fallback ke heuristik judul untuk memfilter Demo/DLC/Pre-Purchase, dll.
        """
        try:
            appid = int(game.get("appid", 0))
        except Exception:
            return False
        title = (game.get("title") or "").strip()

        # Cek tipe dari cache memori saja (hindari I/O per-item yang berat)
        t = self._typeCache.get(appid)
        if t:
            return str(t).lower() == "game"
        if t == "":
            return False

        # Heuristik berdasarkan judul jika tipe belum diketahui
        s = title.lower()
        disallow_keywords = [
            "dlc",
            " demo",
            "soundtrack",
            " ost",
            "pre-purchase",
            "pre purchase",
            "prepurchase",
            "season pass",
            " beta",
            " alpha",
            " editor",
            "benchmark",
            " trailer",
            " teaser",
            " dedicated server",
            "test server",
        ]
        for kw in disallow_keywords:
            if kw in s:
                return False
        return True

    @Slot(str, result=int)
    def getTotalGamesCountFiltered(self, searchText):
        return self.getTotalGamesCount(searchText, True)
    
    @Slot(int)
    def loadGameDetails(self, appid):
        """Load basic game details and system requirements for an app asynchronously.
        Honor noSteamNetwork flag to avoid Steam requests.
        """
        try:
            aid = int(appid)
        except Exception:
            return
        if self._noSteamNetwork:
            # Skip Steam, but still try to fetch system requirements via web search
            def _offline_worker():
                try:
                    try:
                        game = self.appidToGame.get(aid) or {}
                    except Exception:
                        game = {}
                    title = (game.get("title") or "").strip()
                    sysreq = self._fetch_sysreq_from_web(title, aid)
                    if self.qmlBridge:
                        try:
                            self.qmlBridge.gameDetailsLoaded.emit(aid, {"sysreq": sysreq})
                            self.qmlBridge.statusUpdated.emit("Game details loaded")
                        except Exception:
                            pass
                except Exception:
                    pass
            threading.Thread(target=_offline_worker, daemon=True).start()
            return
        def _worker():
            try:
                print(f"Loading game details for appid {aid}…")
                
                # Try fetch system requirements (best-effort)
                sysreq = {"minimum": "", "recommended": ""}
                try:
                    url2 = f"https://store.steampowered.com/api/appdetails?appids={aid}&filters=platforms,pc_requirements"
                    req3 = urllib.request.Request(url2, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req3, timeout=5) as resp3:
                        data2 = json.loads(resp3.read().decode("utf-8", errors="ignore"))
                    node2 = data2.get(str(aid), {})
                    if node2.get("success") and isinstance(node2.get("data"), dict):
                        pc = node2["data"].get("pc_requirements") or {}
                        # Some responses escape HTML; unescape basic sequences
                        def _clean(s):
                            try:
                                txt = (s or "")
                                txt = txt.replace("\r", "").replace("\n", "<br>")
                                # Strip inline styles/backgrounds
                                txt = re.sub(r"\sstyle=\"[^\"]*\"", "", txt, flags=re.I)
                                txt = re.sub(r"<\s*style[^>]*>[\s\S]*?<\/\s*style\s*>", "", txt, flags=re.I)
                                # Convert list items to bullet points
                                txt = re.sub(r"<\s*li\s*>", "• ", txt, flags=re.I)
                                txt = re.sub(r"<\s*/\s*li\s*>", "<br>", txt, flags=re.I)
                                # Drop most tags except <br>, <b>, <strong>
                                txt = re.sub(r"<(?!br\b|/br\b|b\b|/b\b|strong\b|/strong\b)[^>]+>", "", txt, flags=re.I)
                                return txt
                            except Exception:
                                return s or ""
                        sysreq["minimum"] = _clean(pc.get("minimum"))
                        sysreq["recommended"] = _clean(pc.get("recommended"))
                        # Fallback: parse from Steam Store HTML when API is empty/short
                        if ((not sysreq["minimum"] and not sysreq["recommended"]) or
                            (len(sysreq["minimum"]) < 16 and len(sysreq["recommended"]) < 16)):
                            try:
                                html_url2 = f"https://store.steampowered.com/app/{aid}?l=en&agecheck=1"
                                req4 = urllib.request.Request(html_url2, headers={
                                    "User-Agent": "Mozilla/5.0",
                                    "Accept-Language": "en-US,en;q=0.8",
                                    "Cookie": "birthtime=568022401; lastagecheckage=1-January-1988; mature_content=1; wants_mature_content=1",
                                })
                                with urllib.request.urlopen(req4, timeout=8) as resp4:
                                    html2 = resp4.read().decode("utf-8", errors="ignore")
                                def _extract(pattern: str):
                                    m = re.search(pattern, html2, flags=re.I)
                                    return m.group(1) if m else ""
                                # Two-column layout
                                left = _extract(r'class="game_area_sys_req_leftCol"[\s\S]*?<ul[\s\S]*?>([\s\S]*?)</ul')
                                right = _extract(r'class="game_area_sys_req_rightCol"[\s\S]*?<ul[\s\S]*?>([\s\S]*?)</ul')
                                # Single-column layout
                                if not left and not right:
                                    full = _extract(r'class="game_area_sys_req_full"[\s\S]*?<ul[\s\S]*?>([\s\S]*?)</ul')
                                    left = left or full
                                # New wrapper variant (autocollapse block)
                                if not left and not right:
                                    wrapper = _extract(r'class="game_page_autocollapse sysreq_content"[\s\S]*?>([\s\S]*?)</div>')
                                    if wrapper:
                                        l2 = re.search(r'Minimum[\s\S]*?<ul[\s\S]*?>([\s\S]*?)</ul', wrapper, flags=re.I)
                                        r2 = re.search(r'Recommended[\s\S]*?<ul[\s\S]*?>([\s\S]*?)</ul', wrapper, flags=re.I)
                                        left = left or (l2.group(1) if l2 else "")
                                        right = right or (r2.group(1) if r2 else "")
                                # Header-labelled variant
                                if not left and not right:
                                    block = _extract(r'id="game_area_sys_req"[\s\S]*?>([\s\S]*?)</div>')
                                    if block:
                                        m1 = re.search(r'<strong>\s*Minimum\s*:</strong>([\s\S]*?)(?:<strong>\s*Recommended\s*:</strong>|$)', block, flags=re.I)
                                        m2 = re.search(r'<strong>\s*Recommended\s*:</strong>([\s\S]*?)$', block, flags=re.I)
                                        left = left or (m1.group(1) if m1 else "")
                                        right = right or (m2.group(1) if m2 else "")
                                def _format(htmlfrag: str) -> str:
                                    if not htmlfrag:
                                        return ""
                                    frag = re.sub(r'<\s*li\s*>', '• ', htmlfrag, flags=re.I)
                                    frag = re.sub(r'<\s*/\s*li\s*>', '<br>', frag, flags=re.I)
                                    frag = frag.replace('\r', '').replace('\n', '<br>')
                                    return _clean(frag)
                                mtxt = _format(left)
                                rtxt = _format(right)
                                if mtxt:
                                    sysreq["minimum"] = mtxt
                                if rtxt:
                                    sysreq["recommended"] = rtxt
                            except Exception:
                                pass
                except Exception:
                    pass
                # Override sysreq with non-Steam web search results if available
                try:
                    game = self.appidToGame.get(aid) or {}
                except Exception:
                    game = {}
                title2 = (game.get("title") or "").strip()
                try:
                    web_sysreq = self._fetch_sysreq_from_web(title2, aid)
                except Exception:
                    web_sysreq = {"minimum": "", "recommended": ""}
                try:
                    if (web_sysreq.get("minimum") or web_sysreq.get("recommended")):
                        sysreq = web_sysreq
                except Exception:
                    pass
                if self.qmlBridge:
                    try:
                        self.qmlBridge.gameDetailsLoaded.emit(aid, {"sysreq": sysreq})
                        self.qmlBridge.statusUpdated.emit("Game details loaded")
                    except Exception:
                        pass
            except Exception as e:
                try:
                    if self.qmlBridge:
                        self.qmlBridge.errorOccurred.emit(f"Gagal memuat detail game: {e!r}")
                except Exception:
                    pass
        threading.Thread(target=_worker, daemon=True).start()
    
    @Slot(int)
    def startPatchScan(self, appid):
        """Start patch scan - check for unpatched Lua files"""
        self._kickoff_patch_scan(appid)
    
    def _kickoff_patch_scan(self, appid: int):
        """Start patch scan for the specified appid"""
        try:
            # Reset badge on rescan
            try:
                self._set_pill(None)
            except Exception:
                pass
            
            # Resolve Steam stplug-in directory
            from .core.steam import find_steam_root, _ensure_steam_dirs
            steam_root = find_steam_root()
            if not steam_root:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Steam path tidak ditemukan.")
                return
            
            _, stp = _ensure_steam_dirs(steam_root)
            if not stp:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Steam path tidak ditemukan.")
                return
            
            # Import Lua patch functions
            from .core.lua_patch import scan_unpatched_lua
            
            # Scan for unpatched Lua files
            lua_count, unpatched, detail = scan_unpatched_lua(stp, appid)
            
            if lua_count == 0:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Belum di-Add to Steam • tidak ada .lua.")
                    # Emit patch status signal
                    self.qmlBridge.patchStatusUpdated.emit("Not Added", "error")
                return
            
            if unpatched == 0:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Game is Up to Date ✅")
                    self._set_pill("Up to date", "ok")
                    # Emit patch status signal
                    self.qmlBridge.patchStatusUpdated.emit("Up to Date", "ok")
            else:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit(f"Found {unpatched} unpatched lines in {len(detail)} files")
                    self._set_pill(f"{unpatched} unpatched", "warn")
                    # Emit patch status signal
                    self.qmlBridge.patchStatusUpdated.emit(f"{unpatched} Unpatched", "warn")
            
        except Exception as e:
            if self.qmlBridge:
                self.qmlBridge.errorOccurred.emit(f"Gagal scan patch: {e}")
    
    def _fetch_app_name_from_store(self, appid: int) -> str:
        """Fetch game name from Steam Store API with optimized rate limiting"""
        try:
            import urllib.request
            import json
            import time
            
            # Try cache first
            if hasattr(self, '_name_cache') and str(appid) in self._name_cache:
                return self._name_cache[str(appid)]
            
            # Reduced rate limiting for better responsiveness
            if hasattr(self, '_last_request_time'):
                time_since_last = time.time() - self._last_request_time
                if time_since_last < 0.3:  # Reduced from 1 second to 0.3 seconds
                    time.sleep(0.3 - time_since_last)
            
            self._last_request_time = time.time()
            
            # Fetch from Steam Store API with shorter timeout
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}&filters=basic"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            with urllib.request.urlopen(req, timeout=8) as resp:  # Reduced from 15 to 8 seconds
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            
            node = data.get(str(appid), {})
            if node.get("success"):
                name = node.get("data", {}).get("name", f"App {appid}")
                # Cache the result
                if not hasattr(self, '_name_cache'):
                    self._name_cache = {}
                self._name_cache[str(appid)] = name
                return name
            
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Too Many Requests
                print(f"Rate limited for appid {appid}, using fallback name")
                # Cache the fallback to avoid repeated requests
                if not hasattr(self, '_name_cache'):
                    self._name_cache = {}
                self._name_cache[str(appid)] = f"App {appid}"
                return f"App {appid}"
            else:
                print(f"HTTP Error {e.code} for appid {appid}: {e}")
        except Exception as e:
            print(f"Error fetching name for appid {appid}: {e}")
        
        return f"App {appid}"
    
    @Slot()
    def syncUserLibrary(self):
        """Sync user's Steam library (games added via MantaTools) - async with progress updates"""
        def _worker():
            try:
                from .core.steam import find_steam_root, _ensure_steam_dirs
                from .core.steam_meta import _load_meta_cache
                import re
                import time
                from pathlib import Path
                
                # Emit sync started signal
                self.librarySyncStarted.emit()
                
                # Find Steam installation
                steam_root = find_steam_root()
                if not steam_root:
                    print("Steam root not found")
                    self.librarySyncFinished.emit([])
                    return
                
                # Get stplug-in directory
                _, stplugin_path = _ensure_steam_dirs(steam_root)
                if not stplugin_path or not stplugin_path.exists():
                    print("stplug-in directory not found")
                    self.librarySyncFinished.emit([])
                    return
                
                # Load metadata cache for game names
                meta_cache = _load_meta_cache()
                
                # Collect appids from .lua files in stplug-in directory
                appids = set()
                id_re = re.compile(r'(\d{3,10})')
                
                try:
                    for lua_file in stplugin_path.glob("*.lua"):
                        # Extract appid from filename
                        matches = id_re.findall(lua_file.stem)
                        for match in matches:
                            try:
                                appid = int(match)
                                if 100 <= appid <= 999999999:
                                    appids.add(appid)
                            except ValueError:
                                continue
                except Exception as e:
                    print(f"Error scanning stplug-in files: {e}")
                    self.librarySyncFinished.emit([])
                    return
                
                if not appids:
                    print("No appids found in stplug-in")
                    self.librarySyncFinished.emit([])
                    return
                
                # Convert to list and sort
                appids = sorted(list(appids))
                print(f"Found {len(appids)} games in stplug-in, processing...")
                
                user_library = []
                total_games = len(appids)
                processed_games = 0
                
                # Process in larger batches with parallel processing for better responsiveness
                batch_size = 15  # Increased batch size
                total_batches = (len(appids) + batch_size - 1) // batch_size
                
                # Pre-load library folders once to avoid repeated calls
                from .core.steam import _library_folders
                library_folders = _library_folders(steam_root)
                
                for i in range(0, len(appids), batch_size):
                    batch = appids[i:i + batch_size]
                    current_batch = i // batch_size + 1
                    print(f"Processing batch {current_batch}/{total_batches} ({len(batch)} games)")
                    
                    # Emit progress update
                    self.librarySyncProgress.emit(current_batch, total_batches)
                    
                    # Process batch in parallel using ThreadPoolExecutor
                    from concurrent.futures import ThreadPoolExecutor, as_completed
                    
                    def process_single_game(appid):
                        # Get game name from multiple cache layers for maximum speed
                        game_name = f"App {appid}"
                        
                        # First check in-memory cache
                        if appid in self._gameNamesCache:
                            game_name = self._gameNamesCache[appid]
                        # Then check metadata cache
                        elif appid in meta_cache:
                            game_name = meta_cache[appid].get("name", f"App {appid}")
                            # Store in memory cache for next time
                            self._gameNamesCache[appid] = game_name
                        else:
                            # Try to fetch from Steam Store API if not in cache
                            game_name = self._fetch_app_name_from_store(appid)
                            # Store in memory cache for next time
                            self._gameNamesCache[appid] = game_name
                        
                        # Check if game is actually installed in Steam
                        installed = False
                        try:
                            for lib_folder in library_folders:
                                acf_file = lib_folder / f"appmanifest_{appid}.acf"
                                if acf_file.exists():
                                    installed = True
                                    break
                        except Exception:
                            pass
                        
                        return {
                            "appid": appid,
                            "title": game_name,
                            "name": game_name,
                            "installed": installed
                        }
                    
                    # Process batch in parallel
                    with ThreadPoolExecutor(max_workers=min(8, len(batch))) as executor:
                        future_to_appid = {executor.submit(process_single_game, appid): appid for appid in batch}
                        for future in as_completed(future_to_appid):
                            try:
                                game_data = future.result()
                                user_library.append(game_data)
                                processed_games += 1
                                
                                # Emit per-game progress update
                                self.librarySyncGameProgress.emit(processed_games, total_games, game_data["title"])
                                
                            except Exception as e:
                                appid = future_to_appid[future]
                                print(f"Error processing appid {appid}: {e}")
                                # Add fallback data
                                fallback_data = {
                                    "appid": appid,
                                    "title": f"App {appid}",
                                    "name": f"App {appid}",
                                    "installed": False
                                }
                                user_library.append(fallback_data)
                                processed_games += 1
                                
                                # Emit per-game progress update for fallback
                                self.librarySyncGameProgress.emit(processed_games, total_games, fallback_data["title"])
                    
                    # Minimal delay between batches for maximum responsiveness
                    if i + batch_size < len(appids):
                        time.sleep(0.1)  # Reduced to 0.1 seconds for maximum speed
                
                print(f"Successfully processed {len(user_library)} games")
                self.librarySyncFinished.emit(user_library)
                
            except Exception as e:
                print(f"Error getting user library: {e}")
                self.librarySyncFinished.emit([])
        
        # Start worker thread
        import threading
        threading.Thread(target=_worker, daemon=True).start()
    
    @Slot(result=list)
    def getUserLibrary(self):
        """Get user's Steam library (games added via MantaTools) - sync from stplug-in (legacy sync method)"""
        try:
            from .core.steam import find_steam_root, _ensure_steam_dirs
            from .core.steam_meta import _load_meta_cache
            import re
            import time
            from pathlib import Path
            
            # Find Steam installation
            steam_root = find_steam_root()
            if not steam_root:
                print("Steam root not found")
                return []
            
            # Get stplug-in directory
            _, stplugin_path = _ensure_steam_dirs(steam_root)
            if not stplugin_path or not stplugin_path.exists():
                print("stplug-in directory not found")
                return []
            
            # Load metadata cache for game names
            meta_cache = _load_meta_cache()
            
            # Collect appids from .lua files in stplug-in directory
            appids = set()
            id_re = re.compile(r'(\d{3,10})')
            
            try:
                for lua_file in stplugin_path.glob("*.lua"):
                    # Extract appid from filename
                    matches = id_re.findall(lua_file.stem)
                    for match in matches:
                        try:
                            appid = int(match)
                            if 100 <= appid <= 999999999:
                                appids.add(appid)
                        except ValueError:
                            continue
            except Exception as e:
                print(f"Error scanning stplug-in files: {e}")
                return []
            
            if not appids:
                print("No appids found in stplug-in")
                return []
            
            # Convert to list and sort
            appids = sorted(list(appids))
            print(f"Found {len(appids)} games in stplug-in, processing...")
            
            user_library = []
            
            # Process in batches to avoid rate limiting
            batch_size = 5
            for i in range(0, len(appids), batch_size):
                batch = appids[i:i + batch_size]
                print(f"Processing batch {i//batch_size + 1}/{(len(appids) + batch_size - 1)//batch_size}")
                
                for appid in batch:
                    # Get game name from metadata cache first, then from Store API
                    game_name = f"App {appid}"
                    if appid in meta_cache:
                        game_name = meta_cache[appid].get("name", f"App {appid}")
                    else:
                        # Try to fetch from Steam Store API if not in cache
                        game_name = self._fetch_app_name_from_store(appid)
                    
                    # Check if game is actually installed in Steam
                    installed = False
                    try:
                        from .core.steam import _library_folders
                        library_folders = _library_folders(steam_root)
                        for lib_folder in library_folders:
                            acf_file = lib_folder / f"appmanifest_{appid}.acf"
                            if acf_file.exists():
                                installed = True
                                break
                    except Exception:
                        pass
                    
                    user_library.append({
                        "appid": appid,
                        "title": game_name,
                        "name": game_name,
                        "installed": installed
                    })
                
                # Add delay between batches to avoid rate limiting
                if i + batch_size < len(appids):
                    time.sleep(2)  # 2 second delay between batches
            
            print(f"Successfully processed {len(user_library)} games")
            return user_library
            
        except Exception as e:
            print(f"Error getting user library: {e}")
            return []
    
    @Slot(int)
    def addGameToSteam(self, appid):
        """Add game to Steam using worker"""
        worker = AddToSteamWorker(appid, self)
        worker.progress.connect(self.qmlBridge.progressUpdated.emit)
        worker.status.connect(self.qmlBridge.statusUpdated.emit)
        worker.finished.connect(self.qmlBridge.addToSteamFinished.emit)
        # Track & cleanup to prevent: QThread destroyed while running
        try:
            self._activeWorkers.append(worker)
            worker.finished.connect(lambda ok, msg, w=worker: self._cleanupWorker(w))
        except Exception:
            pass
        worker.start()

    def _cleanupWorker(self, worker):
        try:
            if worker in self._activeWorkers:
                self._activeWorkers.remove(worker)
            # Ensure thread stopped
            if worker.isRunning():
                try:
                    worker.quit()
                    worker.wait(2000)
                except Exception:
                    pass
        except Exception:
            pass
    
    @Slot()
    def restartSteam(self):
        """Gracefully close Steam and relaunch it."""
        try:
            root = find_steam_root()
            if not root:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Steam directory tidak ditemukan.")
                return
            exe = (root / "Steam.exe")
            if self.qmlBridge:
                self.qmlBridge.statusUpdated.emit("Menutup Steam…")
            # Ask Steam to shutdown gracefully
            try:
                subprocess.run([str(exe), "-shutdown"], timeout=5)
            except Exception:
                pass
            # Wait until process exits; fallback to taskkill if needed
            waited = 0.0
            while waited < 12.0:
                if not self._is_process_running("steam.exe"):
                    break
                time.sleep(0.5)
                waited += 0.5
            if self._is_process_running("steam.exe"):
                try:
                    subprocess.run(["taskkill", "/IM", "steam.exe", "/T", "/F"], capture_output=True)
                except Exception:
                    pass
                time.sleep(1.0)
            if self.qmlBridge:
                self.qmlBridge.statusUpdated.emit("Menjalankan Steam…")
            try:
                subprocess.Popen([str(exe)])
            except Exception:
                # Fallback: os.startfile if available
                try:
                    import os
                    os.startfile(str(exe))
                except Exception:
                    pass
            if self.qmlBridge:
                self.qmlBridge.statusUpdated.emit("Steam berhasil direstart.")
        except Exception as e:
            if self.qmlBridge:
                self.qmlBridge.errorOccurred.emit(f"Gagal restart Steam: {e!r}")

    def _is_process_running(self, image_name: str) -> bool:
        try:
            out = subprocess.check_output(["tasklist", "/FI", f"IMAGENAME eq {image_name}"], creationflags=0).decode("utf-8", errors="ignore").lower()
            return image_name.lower() in out
        except Exception:
            return False
    
    @Slot(int)
    def openGameFolder(self, appid):
        """Open game folder"""
        # TODO: Implement open game folder
        pass
    
    @Slot(int)
    def removeGame(self, appid):
        """Remove game - delete .lua and .manifest files"""
        try:
            if not appid:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("AppID tidak terbaca.")
                return
            
            # Resolve Steam directories
            from .core.steam import find_steam_root, _ensure_steam_dirs, _db_list, _db_remove_entries
            steam_root = find_steam_root()
            if not steam_root:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Steam path tidak ditemukan.")
                return
            
            depotcache, stplugin = _ensure_steam_dirs(steam_root)
            
            # Get list of files that were installed for this appid
            installed_files = _db_list(appid)
            
            # If no files in database, try to find files manually
            if not installed_files:
                # Look for .lua files in stplug-in directory
                lua_files = list(stplugin.glob(f"*{appid}*.lua"))
                # Look for .manifest files in depotcache directory
                manifest_files = list(depotcache.glob(f"*{appid}*.manifest"))
                
                # Convert to string paths
                installed_files = [str(f) for f in lua_files + manifest_files]
                
                if not installed_files:
                    if self.qmlBridge:
                        self.qmlBridge.statusUpdated.emit("Tidak ada file .lua atau .manifest yang ditemukan untuk game ini.")
                    return
                else:
                    if self.qmlBridge:
                        self.qmlBridge.statusUpdated.emit(f"Ditemukan {len(installed_files)} file untuk dihapus (tidak ada di database).")
            
            # Delete files
            removed_files = []
            for file_path in installed_files:
                try:
                    path = _Path(file_path)
                    if path.exists():
                        path.unlink()
                        removed_files.append(file_path)
                        print(f"Removed file: {file_path}")
                except Exception as e:
                    print(f"Failed to remove {file_path}: {e}")
            
            # Update database
            if removed_files:
                _db_remove_entries(appid, removed_files)
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit(f"Berhasil hapus {len(removed_files)} file untuk AppID {appid}")
            else:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Tidak ada file yang bisa dihapus.")
                    
        except Exception as e:
            print(f"Error removing game {appid}: {e}")
            if self.qmlBridge:
                self.qmlBridge.statusUpdated.emit(f"Error: {str(e)}")
    
    @Slot(int)
    def updateGame(self, appid):
        """Update game - patch Lua files for the specified appid"""
        self._update_game_for_current_app(appid)
    
    def _update_game_for_current_app(self, appid):
        """Update/patch game by commenting out setManifestid() calls in Lua files"""
        try:
            if not appid:
                if self.qmlBridge:
                    self.qmlBridge.errorOccurred.emit("AppID tidak terbaca.")
                return
            
            # Resolve Steam stplug-in directory
            from .core.steam import find_steam_root, _ensure_steam_dirs
            steam_root = find_steam_root()
            if not steam_root:
                if self.qmlBridge:
                    self.qmlBridge.errorOccurred.emit("Steam path tidak ditemukan.")
                return
            
            _, stp = _ensure_steam_dirs(steam_root)
            if not stp:
                if self.qmlBridge:
                    self.qmlBridge.errorOccurred.emit("Steam path tidak ditemukan.")
                return
            
            # Import Lua patch functions
            from .core.lua_patch import scan_unpatched_lua, _patch_lua_for_app
            
            # Scan for unpatched Lua files
            lua_count, unpatched, detail = scan_unpatched_lua(stp, appid)
            
            if lua_count == 0:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Belum di-Add to Steam • tidak ada .lua.")
                return
            
            if unpatched == 0:
                if self.qmlBridge:
                    self.qmlBridge.statusUpdated.emit("Game is Up to Date ✅")
                return
            
            # Get files to patch
            moved = [str(fp) for fp, _ in detail]
            
            # Patch Lua files
            patched = _patch_lua_for_app(stp, appid, moved)
            
            if self.qmlBridge:
                self.qmlBridge.statusUpdated.emit(f"Patched {patched} file .lua • AppID {appid}")
                # Emit patch status signal
                self.qmlBridge.patchStatusUpdated.emit("Up to Date", "ok")
            
            # Update pill status to "Up to date"
            try:
                self._set_pill("Up to date", "ok")
            except Exception:
                pass
            
        except Exception as e:
            if self.qmlBridge:
                self.qmlBridge.errorOccurred.emit(f"Gagal update: {e}")
    
    def _set_pill(self, text: str = None, variant: str = "ok"):
        """Set & fade-in pill badge. variant: 'ok' or 'warn'. If text is None -> hide."""
        try:
            # Emit signal to QML for pill status update
            if self.qmlBridge:
                if not text:
                    # Hide pill
                    self.qmlBridge.statusUpdated.emit("")
                else:
                    # Show pill with status
                    status_text = f"Status: {text}"
                    if variant == "warn":
                        status_text = f"⚠️ {text}"
                    elif variant == "ok":
                        status_text = f"✅ {text}"
                    self.qmlBridge.statusUpdated.emit(status_text)
        except Exception:
            pass


# SettingsManager and FileManager temporarily disabled


def registerQMLTypes():
    """Register QML types with Qt"""
    print("Registering QML types...")
    qmlRegisterType(QMLBridge, "MantaTools", 1, 0, "QMLBridge")
    qmlRegisterType(SteamAPI, "MantaTools", 1, 0, "SteamAPI")
    # SettingsManager and FileManager temporarily disabled
    print("QML types registered successfully")
