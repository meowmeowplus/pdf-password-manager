#!/usr/bin/env python3
"""
🎁 Create Portable Code Review Package
Creates a distributable .claude-code-review.zip package
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_portable_package():
    """Create a portable code review package."""
    
    print("Creating Portable Code Review Package")
    print("=" * 45)
    
    # Package directory
    package_dir = Path(__file__).parent
    
    # Create zip package
    zip_path = package_dir.parent / "claude-code-review-portable.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Add all files from .claude-code-review directory
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                if file.endswith('.py') or file.endswith('.yaml') or file.endswith('.md'):
                    file_path = Path(root) / file
                    # Get relative path from package directory
                    arc_name = file_path.relative_to(package_dir.parent)
                    zipf.write(file_path, arc_name)
                    print(f"   Added {arc_name}")
    
    print(f"\nPackage created: {zip_path}")
    print("\nDistribution Instructions:")
    print("1. Share claude-code-review-portable.zip with your team")
    print("2. Extract to any repository root")
    print("3. Run: python .claude-code-review/install-fixed.py")  
    print("4. Say: 'deep review code'")
    
    return zip_path

if __name__ == '__main__':
    create_portable_package()