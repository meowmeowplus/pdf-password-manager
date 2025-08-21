#!/usr/bin/env python3
"""
🧪 Test Code Review Installation
Verify that the system works correctly
"""

import os
import tempfile
import shutil
from pathlib import Path
import subprocess

def create_test_repo():
    """Create a test repository with sample code."""
    
    # Create temporary directory
    test_dir = Path(tempfile.mkdtemp(prefix="claude-review-test-"))
    
    # Initialize git repo
    os.chdir(test_dir)
    subprocess.run(['git', 'init'], capture_output=True)
    
    # Create sample Python file with security issues
    sample_code = '''#!/usr/bin/env python3
import sqlite3
import sys

def unsafe_login(username, password):
    # SQL Injection vulnerability
    conn = sqlite3.connect('users.db')
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor = conn.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result

def process_file(filename):
    # Path traversal vulnerability  
    with open(filename, 'r') as f:
        return f.read()

def main():
    username = input("Username: ")
    password = input("Password: ")  # Password in plain text
    
    if unsafe_login(username, password):
        print("Login successful")
        filename = input("Enter filename: ")
        content = process_file(filename)  # No validation
        print(content)
    else:
        print("Login failed")

if __name__ == '__main__':
    main()
'''
    
    with open(test_dir / 'app.py', 'w') as f:
        f.write(sample_code)
    
    # Create requirements.txt
    with open(test_dir / 'requirements.txt', 'w') as f:
        f.write("sqlite3\nflask==1.1.1\n")  # Old version with vulnerabilities
    
    print(f"📁 Test repository created: {test_dir}")
    return test_dir

def test_installation(test_dir):
    """Test the installation process."""
    
    print("\n🧪 Testing Installation Process")
    print("=" * 35)
    
    # Copy .claude-code-review to test directory
    package_dir = Path(__file__).parent
    dest_dir = test_dir / '.claude-code-review'
    
    shutil.copytree(package_dir, dest_dir)
    print("✅ Package copied to test repo")
    
    # Change to test directory
    os.chdir(test_dir)
    
    # Run installation
    install_script = dest_dir / 'install.py'
    result = subprocess.run(['python', str(install_script)], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Installation completed successfully")
        print("📋 Installation output:")
        print(result.stdout)
    else:
        print("❌ Installation failed")
        print("📋 Error output:")
        print(result.stderr)
        return False
    
    # Check if files were created
    expected_files = [
        'claude-code-review.yaml',
        'CLAUDE.md', 
        'code-review-workflow.md',
        '.gitignore'
    ]
    
    all_files_exist = True
    for filename in expected_files:
        file_path = test_dir / filename
        if file_path.exists():
            print(f"✅ {filename} created")
        else:
            print(f"❌ {filename} missing")
            all_files_exist = False
    
    return all_files_exist

def test_trigger():
    """Test the trigger system."""
    
    print("\n🎯 Testing Trigger System")
    print("=" * 28)
    
    # Test trigger script
    trigger_script = Path('.claude-code-review/scripts/trigger.py')
    
    if trigger_script.exists():
        result = subprocess.run(['python', str(trigger_script)], 
                               capture_output=True, text=True)
        
        if "DEEP CODE REVIEW MODE ACTIVATED" in result.stdout:
            print("✅ Trigger script works correctly")
            print("📋 Trigger output:")
            print(result.stdout)
            return True
        else:
            print("❌ Trigger script failed")
            print("📋 Output:")
            print(result.stdout)
            return False
    else:
        print("❌ Trigger script not found")
        return False

def main():
    """Main test function."""
    
    print("Claude Code Review System - Integration Test")
    print("=" * 50)
    
    # Create test repository
    test_dir = create_test_repo()
    
    try:
        # Test installation
        install_success = test_installation(test_dir)
        
        # Test trigger
        trigger_success = test_trigger()
        
        # Summary
        print("\n📊 Test Results")
        print("=" * 15)
        print(f"Installation: {'✅ PASS' if install_success else '❌ FAIL'}")
        print(f"Trigger System: {'✅ PASS' if trigger_success else '❌ FAIL'}")
        
        if install_success and trigger_success:
            print("\n🎉 All tests passed! System is ready for distribution.")
            print(f"\n📁 Test repository available at: {test_dir}")
            print("💡 Try saying 'deep review code' in Claude Code!")
        else:
            print("\n⚠️  Some tests failed. Check the output above.")
            
        return install_success and trigger_success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        response = input(f"\n🗑️  Delete test directory {test_dir}? (y/N): ")
        if response.lower().startswith('y'):
            shutil.rmtree(test_dir)
            print("✅ Test directory cleaned up")

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)