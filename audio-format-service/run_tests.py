#!/usr/bin/env python3
"""Test runner for audio format service"""

import os
import subprocess
import sys

# Run pytest
if __name__ == "__main__":
    # Change to the audio-format-service directory
    service_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(service_dir)
    
    # Set PYTHONPATH to include the src directory
    env = os.environ.copy()
    src_path = os.path.join(service_dir, 'src')
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{src_path}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = src_path
    
    exit_code = subprocess.call([
        sys.executable, "-m", "pytest",
        "tests/test_main.py",
        "-v", "--tb=short"
    ], env=env)
    sys.exit(exit_code)
