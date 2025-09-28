#!/usr/bin/env python3
"""Test runner for audio format service"""

import os
import subprocess
import sys

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, '/app/shared/src')

# Run pytest
if __name__ == "__main__":
    exit_code = subprocess.call([
        sys.executable, "-m", "pytest",
        "/app/tests/test_main.py",
        "-v", "--tb=short"
    ])
    sys.exit(exit_code)
