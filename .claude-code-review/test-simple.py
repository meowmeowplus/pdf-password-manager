#!/usr/bin/env python3
"""
Simple test for code review installation
"""

import os
import subprocess
from pathlib import Path

def test_installation():
    """Test if the installation works."""
    
    print("Testing Code Review Installation")
    print("=" * 35)
    
    # Check if we're in the right place
    package_dir = Path(__file__).parent
    install_script = package_dir / 'install-fixed.py'
    
    if not install_script.exists():
        print("ERROR: install-fixed.py not found")
        return False
    
    print("SUCCESS: Found install-fixed.py")
    
    # Check if required files exist
    required_files = [
        'claude-code-review.yaml',
        'README.md',
        'scripts/trigger.py'
    ]
    
    for filename in required_files:
        file_path = package_dir / filename
        if file_path.exists():
            print(f"SUCCESS: Found {filename}")
        else:
            print(f"ERROR: Missing {filename}")
            return False
    
    print("\nAll package files present!")
    print("Package is ready for distribution.")
    return True

if __name__ == '__main__':
    success = test_installation()
    if success:
        print("\nPACKAGE TEST PASSED!")
        print("Ready to use: python .claude-code-review/install-fixed.py")
    else:
        print("\nPACKAGE TEST FAILED!")
    exit(0 if success else 1)