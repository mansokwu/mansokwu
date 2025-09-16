#!/usr/bin/env python3
"""
Script untuk release MantaTools
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def get_current_version():
    """Get current version from version.py"""
    version_file = "src/mantatools/core/version.py"
    with open(version_file, "r") as f:
        content = f.read()
    
    for line in content.split("\n"):
        if line.startswith('VERSION = '):
            return line.split('"')[1]
    return "1.0.0"

def update_version(new_version):
    """Update version in version.py"""
    version_file = "src/mantatools/core/version.py"
    
    with open(version_file, "r") as f:
        content = f.read()
    
    # Replace version
    content = content.replace(f'VERSION = "{get_current_version()}"', f'VERSION = "{new_version}"')
    
    with open(version_file, "w") as f:
        f.write(content)
    
    print(f"Updated version to {new_version}")

def build_release():
    """Build the release"""
    print("Building release...")
    subprocess.run([sys.executable, "build_installer.py", get_current_version()], check=True)
    print("Build completed!")

def create_git_tag(version):
    """Create git tag"""
    tag = f"v{version}"
    print(f"Creating git tag: {tag}")
    
    # Add and commit changes
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Release version {version}"], check=True)
    
    # Create tag
    subprocess.run(["git", "tag", "-a", tag, "-m", f"Release version {version}"], check=True)
    
    print(f"Created tag: {tag}")

def push_to_github():
    """Push to GitHub"""
    print("Pushing to GitHub...")
    subprocess.run(["git", "push", "origin", "master"], check=True)
    subprocess.run(["git", "push", "origin", "--tags"], check=True)
    print("Pushed to GitHub!")

def create_github_release(version):
    """Create GitHub release using gh CLI"""
    try:
        # Check if gh CLI is available
        subprocess.run(["gh", "--version"], check=True, capture_output=True)
        
        tag = f"v{version}"
        installer_path = f"dist/MantaTools_Setup_v{version}.exe"
        
        if not os.path.exists(installer_path):
            print(f"Installer not found: {installer_path}")
            return
        
        # Create release
        cmd = [
            "gh", "release", "create", tag,
            installer_path,
            "--title", f"MantaTools v{version}",
            "--notes", f"Release version {version}\n\n- Bug fixes and improvements\n- Auto-update support"
        ]
        
        subprocess.run(cmd, check=True)
        print(f"Created GitHub release: {tag}")
        
    except subprocess.CalledProcessError:
        print("GitHub CLI not available. Please create release manually:")
        print(f"1. Go to https://github.com/mansokwu/mansokwu/releases")
        print(f"2. Create new release with tag: v{version}")
        print(f"3. Upload: {installer_path}")

def main():
    """Main release function"""
    if len(sys.argv) < 2:
        print("Usage: python release.py <version>")
        print("Example: python release.py 1.0.1")
        sys.exit(1)
    
    new_version = sys.argv[1]
    current_version = get_current_version()
    
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    if new_version == current_version:
        print("Version unchanged, skipping version update")
    else:
        update_version(new_version)
    
    # Build release
    build_release()
    
    # Create git tag
    create_git_tag(new_version)
    
    # Push to GitHub
    push_to_github()
    
    # Create GitHub release
    create_github_release(new_version)
    
    print("\nRelease process completed!")
    print(f"Version {new_version} has been released.")
    print("Users will now receive update notifications.")

if __name__ == "__main__":
    main()
