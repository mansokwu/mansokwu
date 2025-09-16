#!/usr/bin/env python3
"""
MantaTools - Main Entry Point
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import and run the main function
from mantatools.main import main

if __name__ == "__main__":
    sys.exit(main())
