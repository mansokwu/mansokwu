#!/usr/bin/env python3
"""
Build script untuk membuat installer MantaTools
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Bersihkan direktori build sebelumnya"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name}")

def install_dependencies():
    """Install dependencies yang diperlukan untuk build"""
    print("Installing build dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "pyinstaller-hooks-contrib"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def build_executable():
    """Build executable menggunakan PyInstaller"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--name", "MantaTools",
        "--icon", "src/assets/icons/icon.ico",
        "--add-data", "src/qml;qml",  # Include QML files
        "--add-data", "src/assets;assets",  # Include assets
        "--add-data", "src/assets/resource/hid.dll;.",  # Include hid.dll
        "--hidden-import", "PySide6.QtQml",
        "--hidden-import", "PySide6.QtQuick",
        "--hidden-import", "PySide6.QtQuickControls2",
        "--hidden-import", "requests",
        "--hidden-import", "packaging",
        "run.py"
    ]
    
    subprocess.run(cmd, check=True)
    print("Build completed successfully!")

def create_installer():
    """Buat installer menggunakan Inno Setup (jika tersedia)"""
    print("Creating installer...")
    
    # Check if Inno Setup is available
    inno_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    inno_exe = None
    for path in inno_paths:
        if os.path.exists(path):
            inno_exe = path
            break
    
    if not inno_exe:
        print("Inno Setup not found. Creating simple installer script...")
        create_simple_installer()
        return
    
    # Create Inno Setup script
    create_inno_script()
    
    # Run Inno Setup
    subprocess.run([inno_exe, "installer.iss"], check=True)
    print("Installer created successfully!")

def create_inno_script():
    """Buat script Inno Setup"""
    inno_script = '''[Setup]
AppName=MantaTools
AppVersion=1.0.0
AppPublisher=MantaTools
AppPublisherURL=https://github.com/mansokwu/mansokwu
AppSupportURL=https://github.com/mansokwu/mansokwu
AppUpdatesURL=https://github.com/mansokwu/mansokwu
DefaultDirName={autopf}\\MantaTools
DefaultGroupName=MantaTools
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=MantaTools_Setup_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\\MantaTools.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\\assets\\*"; DestDir: "{app}\\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "src\\qml\\*"; DestDir: "{app}\\qml"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\MantaTools"; Filename: "{app}\\MantaTools.exe"
Name: "{group}\\{cm:UninstallProgram,MantaTools}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\MantaTools"; Filename: "{app}\\MantaTools.exe"; Tasks: desktopicon
Name: "{userappdata}\\Microsoft\\Internet Explorer\\Quick Launch\\MantaTools"; Filename: "{app}\\MantaTools.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\\MantaTools.exe"; Description: "{cm:LaunchProgram,MantaTools}"; Flags: nowait postinstall skipifsilent
'''
    
    with open("installer.iss", "w", encoding="utf-8") as f:
        f.write(inno_script)

def create_simple_installer():
    """Buat installer sederhana menggunakan batch script"""
    batch_script = '''@echo off
echo Installing MantaTools...
echo.

set "INSTALL_DIR=%PROGRAMFILES%\\MantaTools"

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

echo Copying files...
copy "dist\\MantaTools.exe" "%INSTALL_DIR%\\"
xcopy "src\\assets" "%INSTALL_DIR%\\assets\\" /E /I /Y
xcopy "src\\qml" "%INSTALL_DIR%\\qml\\" /E /I /Y

echo Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\\Desktop"
echo [InternetShortcut] > "%DESKTOP%\\MantaTools.url"
echo URL=file:///%INSTALL_DIR%\\MantaTools.exe >> "%DESKTOP%\\MantaTools.url"
echo IconFile=%INSTALL_DIR%\\MantaTools.exe >> "%DESKTOP%\\MantaTools.url"
echo IconIndex=0 >> "%DESKTOP%\\MantaTools.url"

echo.
echo Installation completed!
echo MantaTools has been installed to: %INSTALL_DIR%
echo.
pause
'''
    
    with open("install.bat", "w", encoding="utf-8") as f:
        f.write(batch_script)

def update_version_file(version):
    """Update versi di file version.py"""
    version_file = "src/mantatools/core/version.py"
    
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace version
    content = content.replace('VERSION = "1.0.0"', f'VERSION = "{version}"')
    
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Updated version to {version}")

def main():
    """Main build function"""
    if len(sys.argv) > 1:
        version = sys.argv[1]
        print(f"Building version {version}")
        update_version_file(version)
    else:
        print("Building current version")
    
    print("Starting build process...")
    
    # Clean previous builds
    clean_build_dirs()
    
    # Install dependencies
    install_dependencies()
    
    # Build executable
    build_executable()
    
    # Create installer
    create_installer()
    
    print("\nBuild process completed!")
    print("Files created:")
    print("- dist/MantaTools.exe (executable)")
    print("- dist/MantaTools_Setup_v1.0.0.exe (installer)")
    print("\nTo release:")
    print("1. Upload the installer to GitHub Releases")
    print("2. Tag the release with version number (e.g., v1.0.0)")
    print("3. Users will get update notifications automatically")

if __name__ == "__main__":
    main()
