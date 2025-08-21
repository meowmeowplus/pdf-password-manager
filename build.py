#!/usr/bin/env python3
"""
Build script for PDF Password Remover.
Creates standalone executables for both CLI and GUI versions.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Success")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"✗ Command not found: {cmd[0]}")
        return False

def check_requirements():
    """Check if required packages are installed."""
    required_packages = ['PyPDF2', 'PyCryptodome', 'pyinstaller']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('pycryptodome', 'Crypto'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Install with: pip install " + ' '.join(missing))
        return False
    
    return True

def create_icon():
    """Create a simple icon for the executable."""
    icon_path = "icon.ico"
    
    # For now, just note that an icon could be created
    # In a real implementation, you'd create or use an existing .ico file
    print(f"Note: You can add an icon by placing icon.ico in the current directory")
    
    return icon_path if os.path.exists(icon_path) else None

def build_cli():
    """Build the CLI version."""
    print("\n" + "="*50)
    print("Building CLI Version")
    print("="*50)
    
    icon = create_icon()
    cmd = [
        'pyinstaller',
        '--onefile',
        '--console',
        '--name=PDF_Password_Remover_CLI',
        '--clean',
        '--noconfirm'
    ]
    
    if icon:
        cmd.extend(['--icon', icon])
    
    # Add hidden imports for better compatibility
    cmd.extend([
        '--hidden-import=PyPDF2',
        '--hidden-import=Crypto',
        '--hidden-import=Crypto.Cipher',
        '--hidden-import=Crypto.Cipher.AES'
    ])
    
    cmd.append('remove_pdf_password.py')
    
    return run_command(cmd, "Building CLI executable")

def build_gui():
    """Build the GUI version."""
    print("\n" + "="*50)
    print("Building GUI Version")
    print("="*50)
    
    icon = create_icon()
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',  # No console window
        '--name=PDF_Password_Remover_GUI',
        '--clean',
        '--noconfirm'
    ]
    
    if icon:
        cmd.extend(['--icon', icon])
    
    # Add hidden imports
    cmd.extend([
        '--hidden-import=PyPDF2',
        '--hidden-import=Crypto',
        '--hidden-import=Crypto.Cipher',
        '--hidden-import=Crypto.Cipher.AES',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk'
    ])
    
    cmd.append('pdf_password_remover_gui_enhanced.py')
    
    return run_command(cmd, "Building GUI executable")

def build_original_gui():
    """Build the original simple GUI version."""
    print("\n" + "="*50)
    print("Building Original GUI Version")
    print("="*50)
    
    icon = create_icon()
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=PDF_Password_Remover_GUI_Simple',
        '--clean',
        '--noconfirm'
    ]
    
    if icon:
        cmd.extend(['--icon', icon])
    
    cmd.extend([
        '--hidden-import=PyPDF2',
        '--hidden-import=Crypto',
        '--hidden-import=Crypto.Cipher',
        '--hidden-import=Crypto.Cipher.AES',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk'
    ])
    
    cmd.append('pdf_password_remover_gui.py')
    
    return run_command(cmd, "Building original GUI executable")

def clean_build_files():
    """Clean up build artifacts."""
    print("\nCleaning up build files...")
    
    # Remove build directories
    for dir_name in ['build', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")
    
    # Remove .spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"Removed {spec_file}")

def copy_executables():
    """Copy executables to a release directory."""
    release_dir = Path('release')
    release_dir.mkdir(exist_ok=True)
    
    dist_dir = Path('dist')
    if dist_dir.exists():
        for exe_file in dist_dir.glob('*.exe'):
            dest = release_dir / exe_file.name
            shutil.copy2(exe_file, dest)
            print(f"Copied {exe_file.name} to release/")
    
    # Copy documentation
    for doc_file in ['README.md', 'requirements.txt']:
        if os.path.exists(doc_file):
            shutil.copy2(doc_file, release_dir / doc_file)
            print(f"Copied {doc_file} to release/")

def main():
    """Main build function."""
    print("PDF Password Remover - Build Script")
    print("="*40)
    
    # Check if we're in the right directory
    required_files = ['remove_pdf_password.py', 'pdf_password_remover_gui.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Error: {file} not found. Please run this script from the project directory.")
            sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    success_count = 0
    total_builds = 3
    
    # Build all versions
    if build_cli():
        success_count += 1
    
    if build_gui():
        success_count += 1
    
    if build_original_gui():
        success_count += 1
    
    # Summary
    print("\n" + "="*50)
    print("Build Summary")
    print("="*50)
    print(f"Successful builds: {success_count}/{total_builds}")
    
    if success_count > 0:
        copy_executables()
        print(f"\nExecutables are available in the 'dist/' directory")
        print(f"Release files copied to 'release/' directory")
        
        # List created executables
        dist_dir = Path('dist')
        if dist_dir.exists():
            executables = list(dist_dir.glob('*.exe'))
            if executables:
                print(f"\nCreated executables:")
                for exe in executables:
                    size = exe.stat().st_size / (1024 * 1024)  # Size in MB
                    print(f"  - {exe.name} ({size:.1f} MB)")
    
    # Clean up
    if input("\nClean up build files? (y/N): ").lower().startswith('y'):
        clean_build_files()
    
    print(f"\nBuild complete!")

if __name__ == '__main__':
    main()