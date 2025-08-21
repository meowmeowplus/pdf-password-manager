#!/usr/bin/env python3
"""
Claude Code Review System - Universal Installer

Portable code review system that works in any repository.
Just copy .claude-code-review/ folder and run: python .claude-code-review/install-fixed.py
"""

import os
import json
import shutil
from pathlib import Path
import sys

class CodeReviewInstaller:
    def __init__(self):
        self.package_dir = Path(__file__).parent
        self.repo_root = self.find_repo_root()
        self.claude_settings_dirs = [
            Path.home() / '.anthropic' / 'claude-code',
            Path.home() / '.config' / 'claude-code',
            Path.home() / 'AppData' / 'Local' / 'anthropic' / 'claude-code',  # Windows
        ]
    
    def find_repo_root(self):
        """Find repository root (contains .git folder)."""
        current = Path.cwd()
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        return Path.cwd()  # Fallback to current directory
    
    def install(self):
        """Main installation process."""
        print("Claude Code Review System - Universal Installer")
        print("=" * 55)
        print(f"Installing in: {self.repo_root}")
        
        success_count = 0
        
        # Step 1: Copy configuration files
        if self.copy_config_files():
            print("[SUCCESS] Configuration files installed")
            success_count += 1
        else:
            print("[FAILED] Failed to install configuration files")
        
        # Step 2: Setup Claude Code hooks
        if self.setup_claude_hooks():
            print("[SUCCESS] Claude Code hooks configured") 
            success_count += 1
        else:
            print("[WARNING] Claude Code hooks setup failed (may need manual setup)")
        
        # Step 3: Update .gitignore
        if self.update_gitignore():
            print("[SUCCESS] .gitignore updated")
            success_count += 1
        else:
            print("[WARNING] .gitignore update failed")
        
        # Step 4: Create project-specific CLAUDE.md
        if self.create_claude_memory():
            print("[SUCCESS] CLAUDE.md memory file created")
            success_count += 1
        else:
            print("[FAILED] Failed to create CLAUDE.md")
        
        # Summary
        print(f"\nInstallation Summary: {success_count}/4 steps completed")
        
        if success_count >= 3:
            print("\n[SUCCESS] Code review system is ready!")
            print("\nUsage:")
            print("   Just say: 'deep review code'")
            print("   Claude will automatically:")
            print("   - Load your review standards")
            print("   - Scan all code files")
            print("   - Find security issues & edge cases")
            print("   - Provide concrete fixes")
            
            # Show trigger examples
            print("\nOther trigger phrases:")
            print("   - 'deep review code'")
            print("   - 'security audit'") 
            print("   - 'check for vulnerabilities'")
            print("   - 'review this codebase'")
        else:
            print("\n[WARNING] Partial installation. Some manual setup may be required.")
        
        return success_count >= 3
    
    def copy_config_files(self):
        """Copy configuration files to repository root."""
        try:
            files_to_copy = [
                'claude-code-review.yaml',
                'code-review-workflow.md'
            ]
            
            for filename in files_to_copy:
                src = self.package_dir / filename
                dst = self.repo_root / filename
                
                if src.exists():
                    shutil.copy2(src, dst)
                    print(f"   Copied {filename}")
                else:
                    print(f"   Missing {filename} in package")
            
            return True
            
        except Exception as e:
            print(f"   Error copying files: {e}")
            return False
    
    def setup_claude_hooks(self):
        """Setup Claude Code hooks and settings."""
        try:
            # Find or create Claude Code settings directory
            settings_dir = None
            for dir_path in self.claude_settings_dirs:
                if dir_path.exists():
                    settings_dir = dir_path
                    break
            
            if not settings_dir:
                # Create first available directory
                settings_dir = self.claude_settings_dirs[0]
                settings_dir.mkdir(parents=True, exist_ok=True)
            
            settings_file = settings_dir / 'settings.json'
            
            # Load existing settings
            settings = {}
            if settings_file.exists():
                try:
                    with open(settings_file, 'r') as f:
                        settings = json.load(f)
                except Exception:
                    pass
            
            # Add code review hooks
            hooks = settings.get('hooks', {})
            
            # Create trigger script path
            trigger_script = str(self.package_dir / 'scripts' / 'trigger.py')
            
            hooks.update({
                'user-prompt-submit-hook': f'python "{trigger_script}"'
            })
            
            settings['hooks'] = hooks
            
            # Add memory configuration
            settings['memory'] = {
                'enabled': True,
                'file': str(self.repo_root / 'CLAUDE.md')
            }
            
            # Save settings
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print(f"   Settings saved to: {settings_file}")
            return True
            
        except Exception as e:
            print(f"   Error setting up hooks: {e}")
            return False
    
    def update_gitignore(self):
        """Add code review system to .gitignore."""
        try:
            gitignore_path = self.repo_root / '.gitignore'
            
            # Items to ignore
            ignore_items = [
                "",  # Empty line for separation
                "# Claude Code Review System",
                "claude-code-review.yaml",
                "code-review-workflow.md", 
                "CLAUDE.md",
                "*.log",
                ".claude-code-review/",
                "",  # Empty line after
            ]
            
            # Read existing .gitignore
            existing_content = []
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    existing_content = f.read().splitlines()
            
            # Check if already added
            if "# Claude Code Review System" in existing_content:
                print("   .gitignore already contains code review entries")
                return True
            
            # Add new items
            with open(gitignore_path, 'a') as f:
                f.write('\n'.join(ignore_items))
            
            print("   Added code review system to .gitignore")
            return True
            
        except Exception as e:
            print(f"   Error updating .gitignore: {e}")
            return False
    
    def create_claude_memory(self):
        """Create CLAUDE.md with project-specific instructions."""
        try:
            claude_md_path = self.repo_root / 'CLAUDE.md'
            
            # Detect project type
            project_type = self.detect_project_type()
            
            content = f'''# Claude Code Configuration - {self.repo_root.name}

## Code Review Trigger System

### Trigger Phrases
When the user says any of these phrases, automatically initiate deep code review:
- **"deep review code"** (primary trigger)
- "security audit"  
- "check for vulnerabilities"
- "review this codebase"
- "find security issues"

### Automatic Review Process
1. **Load Standards**: Read `claude-code-review.yaml` for review criteria
2. **Scan Codebase**: Use Glob tool to find all relevant source files
3. **Deep Analysis**: Apply security-focused review checklist
4. **Provide Fixes**: Give concrete code solutions, not just descriptions

### Project Context
- **Project Type**: {project_type}
- **Repository**: {self.repo_root.name}
- **Focus Areas**: Security vulnerabilities, edge cases, error handling

### Files to Review
{self.get_file_patterns()}

### Security Priorities
1. **Critical**: Authentication/authorization flaws, SQL injection, XSS
2. **High**: Input validation, error handling, resource cleanup  
3. **Medium**: Race conditions, memory leaks, performance issues
4. **Low**: Code style, documentation, maintainability

### Response Format
Always provide:
1. **Security Analysis** with severity levels
2. **Edge Cases** unhandled scenarios  
3. **Concrete Fixes** with code examples
4. **Priority Actions** ranked by importance
5. **Prevention Recommendations** for future

Remember: Security and reliability are non-negotiable. Provide actionable fixes, not just problem descriptions.
'''
            
            with open(claude_md_path, 'w') as f:
                f.write(content)
            
            print(f"   Created CLAUDE.md for {project_type} project")
            return True
            
        except Exception as e:
            print(f"   Error creating CLAUDE.md: {e}")
            return False
    
    def detect_project_type(self):
        """Detect project type based on files present."""
        if (self.repo_root / 'package.json').exists():
            return "Node.js/JavaScript"
        elif (self.repo_root / 'requirements.txt').exists() or (self.repo_root / 'pyproject.toml').exists():
            return "Python"
        elif (self.repo_root / 'pom.xml').exists():
            return "Java/Maven"
        elif (self.repo_root / 'Cargo.toml').exists():
            return "Rust"
        elif (self.repo_root / 'go.mod').exists():
            return "Go"
        elif list(self.repo_root.glob('*.csproj')):
            return "C#/.NET"
        else:
            return "Multi-language"
    
    def get_file_patterns(self):
        """Get file patterns to review based on project type."""
        project_type = self.detect_project_type()
        
        patterns = {
            "Python": "- Python: `**/*.py`\n- Config: `*.yaml`, `*.json`, `requirements.txt`",
            "Node.js/JavaScript": "- JavaScript: `**/*.js`, `**/*.ts`, `**/*.jsx`, `**/*.tsx`\n- Config: `package.json`, `*.json`, `*.yaml`",
            "Java/Maven": "- Java: `**/*.java`\n- Config: `pom.xml`, `*.xml`, `*.properties`",
            "Rust": "- Rust: `**/*.rs`\n- Config: `Cargo.toml`, `*.toml`",
            "Go": "- Go: `**/*.go`\n- Config: `go.mod`, `*.yaml`",
            "C#/.NET": "- C#: `**/*.cs`\n- Config: `*.csproj`, `*.json`, `*.xml`",
        }
        
        return patterns.get(project_type, "- All source files: `**/*.py`, `**/*.js`, `**/*.java`, `**/*.rs`, `**/*.go`")

def main():
    """Main installation function."""
    installer = CodeReviewInstaller()
    success = installer.install()
    
    if success:
        print("\n[SUCCESS] Ready to use! Try saying: 'deep review code'")
    else:
        print("\n[INFO] Manual setup may be required. Check the documentation.")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())