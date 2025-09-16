from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PySide6.QtGui import QPainter, QColor
import time

class Snack:
    """Simple snackbar notification system"""
    
    @staticmethod
    def show_snack(parent: QWidget, message: str, snack_type: str = "info", duration: int = 3000):
        """
        Show a snackbar notification
        Args:
            parent: Parent widget
            message: Message to display
            snack_type: Type of snack ("success", "error", "info", "warning")
            duration: Duration in milliseconds
        """
        snack = SnackBar(parent, message, snack_type, duration)
        snack.show()

class SnackBar(QWidget):
    def __init__(self, parent: QWidget, message: str, snack_type: str, duration: int):
        super().__init__(parent)
        self.parent = parent
        self.message = message
        self.snack_type = snack_type
        self.duration = duration
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set colors based on type
        if snack_type == "success":
            bg_color = "#4caf50"
        elif snack_type == "error":
            bg_color = "#f44336"
        elif snack_type == "warning":
            bg_color = "#ff9800"
        else:  # info
            bg_color = "#2196f3"
            
        self.setStyleSheet(f"""
            QWidget {{
                background: {bg_color};
                border-radius: 8px;
                color: white;
                font-weight: 500;
                padding: 12px 16px;
            }}
        """)
        
        # Create layout and label
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)
        
        # Position the snackbar
        self.position_snackbar()
        
        # Auto-hide timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide)
        self.timer.start(duration)
        
    def position_snackbar(self):
        """Position the snackbar at the bottom of the parent widget"""
        if self.parent:
            parent_rect = self.parent.geometry()
            self.resize(300, 50)
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + parent_rect.height() - self.height() - 20
            self.move(x, y)
