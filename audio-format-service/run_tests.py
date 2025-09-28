#!/usr/bin/env python3
"""Test runner for audio format service"""

import os
import subprocess
import sys

# Run pytest
if __name__ == "__main__":
    # Change to the audio-format-service directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    exit_code = subprocess.call([
        sys.executable, "-m", "pytest",
        "tests/test_main.py",
        "-v", "--tb=short"
    ])
    sys.exit(exit_code)
