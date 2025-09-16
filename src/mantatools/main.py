"""
Main application entry point for MantaTools - QML Version
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, QUrl
from PySide6.QtQml import qmlRegisterType, QQmlApplicationEngine

from .core.paths import resource_path, ensure_hid_dll_first_run
from .core.version import get_version, get_repo_url
from .core.updater import UpdateManager, AutoUpdateChecker
from .bridge import registerQMLTypes, QMLBridge


def main():
    """Main application entry point - QML Version"""
    # Set environment variables for better GPU performance and Material style
    os.environ["QT_QUICK_BACKEND"] = "software"  # Use software rendering
    os.environ["QT_OPENGL"] = "angle"  # Use ANGLE for better compatibility
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"  # Use Material style for custom ScrollBar support
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MantaTools")
    app.setApplicationVersion(get_version())
    app.setOrganizationName("MantaTools")
    
    # Set application icon
    icon_path = resource_path("src/assets/icons/icon.ico")
    print(f"Looking for icon at: {icon_path}")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print("Application icon set successfully")
    else:
        print(f"Icon file not found at: {icon_path}")
        # Try alternative path
        alt_icon_path = resource_path("assets/icons/icon.ico")
        print(f"Trying alternative path: {alt_icon_path}")
        if os.path.exists(alt_icon_path):
            app.setWindowIcon(QIcon(alt_icon_path))
            print("Application icon set from alternative path")
        else:
            print("Icon file not found in any location")
    
    # Ensure hid.dll is in place (first run setup)
    ensure_hid_dll_first_run()

    # --- Register QML Types ---
    registerQMLTypes()
    
    # --- Create QML Engine ---
    engine = QQmlApplicationEngine()
    
    # Create and register QML bridge
    qml_bridge = QMLBridge()
    print(f"Created QMLBridge: {qml_bridge}")
    engine.rootContext().setContextProperty("qmlBridge", qml_bridge)
    print(f"Set context property qmlBridge: {qml_bridge}")
    
    # Initialize update manager
    update_manager = UpdateManager(get_version(), get_repo_url())
    engine.rootContext().setContextProperty("updateManager", update_manager)
    
    # Check for updates on startup (non-blocking)
    auto_checker = AutoUpdateChecker(get_version(), get_repo_url())
    if auto_checker.check_update_available():
        # Show update notification after a short delay
        from PySide6.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(lambda: update_manager.check_for_updates())
        timer.setSingleShot(True)
        timer.start(2000)  # Check after 2 seconds
    
    # Load main QML file
    qml_file = resource_path("src/qml/main.qml")
    if not os.path.exists(qml_file):
        # Fallback to relative path
        qml_file = os.path.join(os.path.dirname(__file__), "..", "qml", "main.qml")
    
    print(f"Loading QML file: {qml_file}")
    engine.load(QUrl.fromLocalFile(qml_file))
    
    # Check if QML loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML file")
        sys.exit(-1)
    
    print("QML loaded successfully")
    print(f"Root objects: {engine.rootObjects()}")
    
    # Try to access qmlBridge from root object
    root_object = engine.rootObjects()[0]
    print(f"Root object: {root_object}")
    
    # Try to set qmlBridge property on root object
    try:
        root_object.setProperty("qmlBridge", qml_bridge)
        print("Set qmlBridge property on root object")
    except Exception as e:
        print(f"Error setting qmlBridge property on root object: {e}")
    
    if not engine.rootObjects():
        sys.exit(-1)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
