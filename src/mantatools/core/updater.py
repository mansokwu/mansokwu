"""
Auto-update system for MantaTools
Handles checking for updates and downloading new versions
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from packaging import version

from PySide6.QtCore import QObject, Signal, QThread, QTimer
from PySide6.QtWidgets import QMessageBox, QProgressDialog


class UpdateChecker(QObject):
    """Thread-safe update checker"""
    
    update_available = Signal(dict)  # Emits update info when available
    update_error = Signal(str)  # Emits error messages
    download_progress = Signal(int)  # Emits download progress (0-100)
    download_complete = Signal(str)  # Emits path to downloaded file
    
    def __init__(self, current_version: str, repo_url: str):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url
        self.github_api_url = f"https://api.github.com/repos/{self._extract_repo_info()}/releases/latest"
        
    def _extract_repo_info(self) -> str:
        """Extract owner/repo from GitHub URL"""
        if "github.com" in self.repo_url:
            parts = self.repo_url.replace("https://github.com/", "").replace(".git", "")
            return parts
        return "mansokwu/mansokwu"  # Default fallback
    
    def check_for_updates(self):
        """Check for available updates"""
        try:
            response = requests.get(self.github_api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get("tag_name", "").lstrip("v")
            
            if version.parse(latest_version) > version.parse(self.current_version):
                # Update available
                update_info = {
                    "version": latest_version,
                    "download_url": self._get_download_url(release_data),
                    "release_notes": release_data.get("body", ""),
                    "published_at": release_data.get("published_at", ""),
                    "size": self._get_asset_size(release_data)
                }
                self.update_available.emit(update_info)
            else:
                # No update available
                self.update_available.emit({"version": None})
                
        except Exception as e:
            self.update_error.emit(f"Error checking for updates: {str(e)}")
    
    def _get_download_url(self, release_data: Dict[str, Any]) -> Optional[str]:
        """Get download URL for the installer"""
        assets = release_data.get("assets", [])
        for asset in assets:
            if asset.get("name", "").endswith(".exe"):
                return asset.get("browser_download_url")
        return None
    
    def _get_asset_size(self, release_data: Dict[str, Any]) -> int:
        """Get size of the installer asset"""
        assets = release_data.get("assets", [])
        for asset in assets:
            if asset.get("name", "").endswith(".exe"):
                return asset.get("size", 0)
        return 0
    
    def download_update(self, download_url: str, target_path: str):
        """Download the update file"""
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.download_progress.emit(progress)
            
            self.download_complete.emit(target_path)
            
        except Exception as e:
            self.update_error.emit(f"Error downloading update: {str(e)}")


class UpdateManager(QObject):
    """Main update manager with UI integration"""
    
    def __init__(self, current_version: str, repo_url: str):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url
        self.update_checker = UpdateChecker(current_version, repo_url)
        self.update_checker_thread = QThread()
        
        # Move update checker to separate thread
        self.update_checker.moveToThread(self.update_checker_thread)
        
        # Connect signals
        self.update_checker.update_available.connect(self._on_update_available)
        self.update_checker.update_error.connect(self._on_update_error)
        self.update_checker.download_progress.connect(self._on_download_progress)
        self.update_checker.download_complete.connect(self._on_download_complete)
        
        # Connect thread signals
        self.update_checker_thread.started.connect(self.update_checker.check_for_updates)
        
        # Start thread
        self.update_checker_thread.start()
        
        # Progress dialog
        self.progress_dialog = None
        self.downloaded_file = None
    
    def check_for_updates(self, show_no_update_message: bool = False):
        """Check for updates and show appropriate UI"""
        self.show_no_update_message = show_no_update_message
        self.update_checker_thread.start()
    
    def _on_update_available(self, update_info: Dict[str, Any]):
        """Handle update available signal"""
        if update_info.get("version") is None:
            if hasattr(self, 'show_no_update_message') and self.show_no_update_message:
                QMessageBox.information(
                    None, 
                    "Update Check", 
                    f"Anda sudah menggunakan versi terbaru ({self.current_version})"
                )
            return
        
        # Show update notification
        version = update_info["version"]
        release_notes = update_info.get("release_notes", "Tidak ada catatan rilis")
        size_mb = update_info.get("size", 0) / (1024 * 1024)
        
        msg = QMessageBox()
        msg.setWindowTitle("Update Tersedia")
        msg.setText(f"Versi baru {version} tersedia!")
        msg.setInformativeText(
            f"Versi saat ini: {self.current_version}\n"
            f"Versi terbaru: {version}\n"
            f"Ukuran: {size_mb:.1f} MB\n\n"
            f"Catatan rilis:\n{release_notes[:200]}{'...' if len(release_notes) > 200 else ''}"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        msg.button(QMessageBox.Yes).setText("Download Update")
        msg.button(QMessageBox.No).setText("Nanti Saja")
        
        if msg.exec() == QMessageBox.Yes:
            self._download_update(update_info)
    
    def _download_update(self, update_info: Dict[str, Any]):
        """Download the update"""
        download_url = update_info["download_url"]
        if not download_url:
            QMessageBox.critical(None, "Error", "URL download tidak tersedia")
            return
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog("Mengunduh update...", "Batal", 0, 100)
        self.progress_dialog.setWindowTitle("Download Update")
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()
        
        # Create temp file for download
        temp_dir = tempfile.gettempdir()
        self.downloaded_file = os.path.join(temp_dir, f"MantaTools_Update_{update_info['version']}.exe")
        
        # Start download in thread
        self.update_checker.download_update(download_url, self.downloaded_file)
    
    def _on_download_progress(self, progress: int):
        """Handle download progress"""
        if self.progress_dialog:
            self.progress_dialog.setValue(progress)
    
    def _on_download_complete(self, file_path: str):
        """Handle download complete"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        # Ask user to install
        msg = QMessageBox()
        msg.setWindowTitle("Download Selesai")
        msg.setText("Update berhasil diunduh!")
        msg.setInformativeText("Apakah Anda ingin menjalankan installer sekarang?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        msg.button(QMessageBox.Yes).setText("Install Sekarang")
        msg.button(QMessageBox.No).setText("Install Nanti")
        
        if msg.exec() == QMessageBox.Yes:
            self._install_update(file_path)
        else:
            # Save path for later installation
            self._save_installer_path(file_path)
    
    def _install_update(self, installer_path: str):
        """Run the installer"""
        try:
            # Run installer
            subprocess.Popen([installer_path], shell=True)
            
            # Close current application
            QMessageBox.information(
                None, 
                "Installer Dimulai", 
                "Installer akan dimulai. Aplikasi ini akan ditutup."
            )
            
            # Exit application
            sys.exit(0)
            
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Gagal menjalankan installer: {str(e)}")
    
    def _save_installer_path(self, installer_path: str):
        """Save installer path for later use"""
        config_dir = Path.home() / ".mantatools"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "pending_update.json"
        with open(config_file, 'w') as f:
            json.dump({"installer_path": installer_path}, f)
    
    def _on_update_error(self, error_message: str):
        """Handle update error"""
        if self.progress_dialog:
            self.progress_dialog.close()
        
        QMessageBox.warning(None, "Update Error", f"Terjadi kesalahan: {error_message}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.update_checker_thread.isRunning():
            self.update_checker_thread.quit()
            self.update_checker_thread.wait()


class AutoUpdateChecker:
    """Simple auto-update checker for startup"""
    
    def __init__(self, current_version: str, repo_url: str):
        self.current_version = current_version
        self.repo_url = repo_url
        self.github_api_url = f"https://api.github.com/repos/{self._extract_repo_info()}/releases/latest"
    
    def _extract_repo_info(self) -> str:
        """Extract owner/repo from GitHub URL"""
        if "github.com" in self.repo_url:
            parts = self.repo_url.replace("https://github.com/", "").replace(".git", "")
            return parts
        return "mansokwu/mansokwu"
    
    def check_update_available(self) -> bool:
        """Check if update is available (non-blocking)"""
        try:
            response = requests.get(self.github_api_url, timeout=5)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get("tag_name", "").lstrip("v")
            
            return version.parse(latest_version) > version.parse(self.current_version)
            
        except Exception:
            return False
