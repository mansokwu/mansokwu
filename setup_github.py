#!/usr/bin/env python3
"""
Setup script untuk konfigurasi GitHub repository
"""

import os
import subprocess
import sys

def check_git_repo():
    """Check if this is a git repository"""
    try:
        subprocess.run(["git", "status"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def init_git_repo():
    """Initialize git repository"""
    print("Initializing git repository...")
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
    print("Git repository initialized!")

def setup_github_remote():
    """Setup GitHub remote"""
    repo_url = "https://github.com/mansokwu/mansokwu.git"
    
    print(f"Setting up GitHub remote: {repo_url}")
    
    try:
        # Check if remote already exists
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Remote 'origin' already exists")
            return
    except:
        pass
    
    # Add remote
    subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
    print("GitHub remote added!")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer outputs
*.exe
*.msi
*.deb
*.rpm

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary files
*.tmp
*.temp
installer.iss
install.bat
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("Created .gitignore file")

def setup_github_actions():
    """Setup GitHub Actions workflow"""
    workflow_dir = ".github/workflows"
    os.makedirs(workflow_dir, exist_ok=True)
    
    print("GitHub Actions workflow already created!")

def main():
    """Main setup function"""
    print("Setting up MantaTools for GitHub...")
    print("=" * 40)
    
    # Check if git repo exists
    if not check_git_repo():
        print("Not a git repository. Initializing...")
        init_git_repo()
    else:
        print("Git repository found!")
    
    # Create .gitignore
    create_gitignore()
    
    # Setup GitHub remote
    setup_github_remote()
    
    # Setup GitHub Actions
    setup_github_actions()
    
    print("\nSetup completed!")
    print("\nNext steps:")
    print("1. Push to GitHub: git push -u origin master")
    print("2. Create first release: python release.py 1.0.0")
    print("3. Test auto-update system")
    
    # Ask if user wants to push now
    response = input("\nDo you want to push to GitHub now? (y/n): ")
    if response.lower() == 'y':
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Setup auto-update system"], check=True)
            subprocess.run(["git", "push", "-u", "origin", "master"], check=True)
            print("Pushed to GitHub successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error pushing to GitHub: {e}")
            print("Please push manually: git push -u origin master")

if __name__ == "__main__":
    main()
