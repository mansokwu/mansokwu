#!/usr/bin/env python3
"""
Test script untuk sistem auto-update MantaTools
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from mantatools.core.updater import AutoUpdateChecker, UpdateManager
from mantatools.core.version import get_version, get_repo_url

def test_version_check():
    """Test version checking"""
    print("Testing version check...")
    print(f"Current version: {get_version()}")
    print(f"Repository URL: {get_repo_url()}")
    
    checker = AutoUpdateChecker(get_version(), get_repo_url())
    has_update = checker.check_update_available()
    
    print(f"Update available: {has_update}")
    return has_update

def test_update_manager():
    """Test update manager"""
    print("\nTesting update manager...")
    
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    
    app = QApplication(sys.argv)
    
    manager = UpdateManager(get_version(), get_repo_url())
    
    # Test manual check
    print("Testing manual update check...")
    manager.check_for_updates(show_no_update_message=True)
    
    # Wait a bit for async operations
    timer = QTimer()
    timer.timeout.connect(app.quit)
    timer.start(5000)  # 5 seconds
    
    app.exec()

def main():
    """Main test function"""
    print("MantaTools Update System Test")
    print("=" * 40)
    
    # Test 1: Version check
    has_update = test_version_check()
    
    # Test 2: Update manager (requires Qt)
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        test_update_manager()
    else:
        print("\nSkipping GUI test. Run with --gui to test UI components.")
    
    print("\nTest completed!")
    
    if has_update:
        print("✓ Update system is working - update available!")
    else:
        print("✓ Update system is working - no updates available")

if __name__ == "__main__":
    main()
