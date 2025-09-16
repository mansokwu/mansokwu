import os
import json
import uuid
import platform
import hashlib
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QCheckBox, QMessageBox, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, Signal
from PySide6.QtGui import QPixmap, QFont, QPainter, QLinearGradient, QBrush, QColor

from ..ui.theme import DARK_BG, TEXT_PRI, TEXT_SEC, BORDER, ACCENT, ACCENT_H
from ..ui.snack import Snack
from ..core.paths import resource_path


class AuthGate(QDialog):
    """
    Modern Auth gate 100% via FastAPI.
    - Tidak baca/cek allowed_codes.txt
    - Tidak ada fallback regex lokal
    - Tidak auto-skip: user selalu harus klik Login
    - UI modern dengan animasi dan responsif
    Kontrak default:
      POST {API_BASE_URL}/auth/verify
      body: {"code": "<string>", "device": "<fingerprint>"}
      200 OK -> {"valid": true, "user": {...}}  => login lolos
      selain itu / {"valid": false}             => tolak
    """
    API_BASE_URL = os.getenv("MANTA_API_BASE_URL", "https://mantagames.my.id").rstrip("/")
    VERIFY_PATH  = os.getenv("MANTA_VERIFY_PATH", "/auth/verify")
    TIMEOUT_S    = int(os.getenv("MANTA_HTTP_TIMEOUT", "12"))
    DEBUG        = os.getenv("MANTA_DEBUG", "0") == "1"
    
    # Signals untuk feedback
    loginStarted = Signal()
    loginFinished = Signal(bool, str)  # success, message
    
    def verify_token(code, device):
        url = f"{AuthGate.API_BASE_URL}{AuthGate.VERIFY_PATH}"
        print("[MANTA] verifying to:", url)  # sementara, biar keliatan di console
        import requests
        r = requests.post(url, json={"code": code, "device": device}, timeout=12)
        return r.status_code, r.text

    def __init__(self, parent=None, app_name="Manta Games", logo_path: str | None = None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(f"{app_name} • Login")
        self.setObjectName("AuthGate")
        self.setFixedSize(480, 600)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # State variables
        self.is_loading = False
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_loading_animation)
        self.loading_dots = 0

        # === Modern Styles ===
        self.setStyleSheet(f"""
            QDialog#AuthGate {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0b1220, stop:1 #1a2332);
                border-radius: 20px;
            }}
            
            QFrame#MainFrame {{
                background: rgba(11, 18, 32, 0.95);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 20px;
            }}
            
            QLabel#Title {{
                color: {TEXT_PRI};
                font-weight: 700;
                font-size: 28px;
                background: transparent;
            }}
            
            QLabel#Sub {{
                color: {TEXT_SEC};
                font-size: 14px;
                background: transparent;
            }}
            
            QLineEdit#TokenInput {{
                background: rgba(18, 23, 34, 0.8);
                color: {TEXT_PRI};
                border: 2px solid {BORDER};
                border-radius: 12px;
                padding: 16px 20px;
                font-size: 16px;
                font-weight: 500;
            }}
            
            QLineEdit#TokenInput:focus {{
                border: 2px solid {ACCENT};
                background: rgba(18, 23, 34, 0.9);
            }}
            
            QPushButton#LoginBtn {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT}, stop:1 #00b8e6);
                color: #0b1220;
                font-weight: 700;
                font-size: 16px;
                border: none;
                border-radius: 12px;
                padding: 16px 24px;
                min-height: 20px;
            }}
            
            QPushButton#LoginBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACCENT_H}, stop:1 #00a3cc);
            }}
            
            QPushButton#LoginBtn:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0099cc, stop:1 #0088bb);
            }}
            
            QPushButton#LoginBtn:disabled {{
                background: #2a2a2a;
                color: #666;
            }}
            
            QLabel#Links {{
                color: {TEXT_SEC};
                font-size: 13px;
                background: transparent;
            }}
            
            QLabel#Links a {{
                color: {ACCENT};
                text-decoration: none;
            }}
            
            QLabel#Links a:hover {{
                color: {ACCENT_H};
                text-decoration: underline;
            }}
            
            QLabel#LoadingText {{
                color: {TEXT_SEC};
                font-size: 14px;
                background: transparent;
            }}
        """)

        # Main container frame
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("MainFrame")
        self.main_frame.setGeometry(0, 0, 480, 600)
        
        # Main layout
        v = QVBoxLayout(self.main_frame)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(24)

        # Logo section
        self.logo = QLabel(self.main_frame)
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setFixedHeight(120)
        
        pm = QPixmap()
        if logo_path: 
            pm.load(logo_path)
        else:
            for cand in ("auth_logo.svg","auth_logo.png","auth_logo@2x.png","logo.png","assets/auth_logo.svg","assets/auth_logo.png","assets/logo.png"):
                rp = resource_path(cand)
                p = Path(rp)
                if p.exists(): 
                    pm.load(str(p))
                    break
                    
        if not pm.isNull():
            # Scale logo to fit nicely
            scaled_pm = pm.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo.setPixmap(scaled_pm)
        else:
            # Fallback: create a simple logo placeholder
            self.logo.setText("🎮")
            self.logo.setStyleSheet("font-size: 48px; color: #00d4ff;")
            
        v.addWidget(self.logo, 0, Qt.AlignHCenter)

        # Title section
        title = QLabel("Welcome to Manta Games", self.main_frame)
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignHCenter)
        v.addWidget(title, 0, Qt.AlignHCenter)
        
        sub = QLabel("Enter your authentication token to continue", self.main_frame)
        sub.setObjectName("Sub")
        sub.setAlignment(Qt.AlignHCenter)
        v.addWidget(sub, 0, Qt.AlignHCenter)

        # Spacer
        v.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Input section
        self.ed = QLineEdit(self.main_frame)
        self.ed.setObjectName("TokenInput")
        self.ed.setPlaceholderText("Enter your token...")
        self.ed.returnPressed.connect(self.try_login)
        v.addWidget(self.ed)

        # Loading text (hidden by default)
        self.loading_text = QLabel("", self.main_frame)
        self.loading_text.setObjectName("LoadingText")
        self.loading_text.setAlignment(Qt.AlignHCenter)
        self.loading_text.hide()
        v.addWidget(self.loading_text)

        # Login button
        self.btn = QPushButton("Login", self.main_frame)
        self.btn.setObjectName("LoginBtn")
        self.btn.clicked.connect(self.try_login)
        v.addWidget(self.btn)

        # Spacer
        v.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Links section
        links = QLabel('Need help? Join our <a href="https://discord.com/invite/yBYsHXtZrR">Discord</a>', self.main_frame)
        links.setObjectName("Links")
        links.setTextFormat(Qt.RichText)
        links.setOpenExternalLinks(True)
        links.setAlignment(Qt.AlignHCenter)
        v.addWidget(links)
        
        # Center the dialog
        self._center_dialog()
        
        # Connect signals
        self.loginStarted.connect(self._on_login_started)
        self.loginFinished.connect(self._on_login_finished)

    def _center_dialog(self):
        """Center the dialog on screen"""
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
        else:
            # Center on screen
            from PySide6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen().geometry()
                x = (screen.width() - self.width()) // 2
                y = (screen.height() - self.height()) // 2
                self.move(x, y)

    def _update_loading_animation(self):
        """Update loading animation dots"""
        if self.is_loading:
            self.loading_dots = (self.loading_dots + 1) % 4
            dots = "." * self.loading_dots
            self.loading_text.setText(f"Authenticating{dots}")
        else:
            self.animation_timer.stop()

    def _on_login_started(self):
        """Handle login started signal"""
        self.is_loading = True
        self.btn.setEnabled(False)
        self.btn.setText("Authenticating...")
        self.loading_text.show()
        self.loading_text.setText("Authenticating")
        self.animation_timer.start(500)  # Update every 500ms

    def _on_login_finished(self, success: bool, message: str):
        """Handle login finished signal"""
        self.is_loading = False
        self.btn.setEnabled(True)
        self.btn.setText("Login")
        self.loading_text.hide()
        self.animation_timer.stop()
        
        if success:
            self.accept()
        else:
            # Show error message
            Snack.show_snack(self, message, "error", 3000)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    # --- Local token storage dimatikan total ---
    def _token_path(self) -> Path: return Path.home() / ".manta_auth.json"
    def _has_valid_token(self) -> bool: return False
    def _save_token(self, code: str): return
    @staticmethod
    def forget_token():
        try:
            p = Path.home() / ".manta_auth.json"
            if p.exists(): p.unlink()
            return True
        except Exception:
            return False

    # --- Util: device fingerprint sederhana (optional) ---
    def _fingerprint(self) -> str:
        seed = f"{platform.system()}|{platform.node()}|{platform.machine()}|{uuid.getnode()}"
        return hashlib.sha256(seed.encode()).hexdigest()[:32]

    # --- HTTP helper ---
    def _api_post_json(self, path: str, payload: dict) -> tuple[int, dict]:
        url = urljoin(self.API_BASE_URL + "/", path.lstrip("/"))
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "MantaTools/1.0"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=self.TIMEOUT_S) as resp:
                status = getattr(resp, "status", 200)
                raw = resp.read().decode("utf-8", errors="ignore") or "{}"
        except urllib.error.HTTPError as e:
            status = e.code
            raw = e.read().decode("utf-8", errors="ignore") or "{}"
        except Exception as e:
            if self.DEBUG:
                print("[AuthGate] network error:", e)
            return 0, {"detail": f"Gagal konek ke server auth ({e.__class__.__name__})"}
        try:
            body = json.loads(raw)
        except Exception:
            body = {}
        if self.DEBUG:
            print("[AuthGate] POST", url, "->", status, body)
        return status, body

    # --- ACTION: login ---
    def try_login(self):
        if self.is_loading:
            return  # Prevent multiple simultaneous logins
            
        code = (self.ed.text() or "").strip()
        if not code:
            Snack.show_snack(self, "Token wajib diisi.", "error", 2200)
            return

        # Emit login started signal
        self.loginStarted.emit()
        
        # Run login in a separate thread to avoid blocking UI
        import threading
        def _login_worker():
            try:
                payload = {"code": code, "device": self._fingerprint()}
                status, body = self._api_post_json(self.VERIFY_PATH, payload)

                if status == 200 and isinstance(body, dict) and body.get("valid") is True:
                    self.loginFinished.emit(True, "Login berhasil! ✅")
                else:
                    msg = (body.get("detail") if isinstance(body, dict) else None) \
                          or ("Server auth tidak bisa dihubungi." if status == 0 else "Token tidak valid.")
                    self.loginFinished.emit(False, msg)
            except Exception as e:
                self.loginFinished.emit(False, f"Error: {str(e)}")
        
        threading.Thread(target=_login_worker, daemon=True).start()

    def exec_and_passed(self) -> bool:
        return self.exec() == QDialog.Accepted
