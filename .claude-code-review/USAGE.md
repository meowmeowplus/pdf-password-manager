# 🔍 Quick Start Guide

## 🚀 3-Step Setup (30 seconds)

### 1. Copy Package
Copy the entire `.claude-code-review/` folder to your repository root:
```bash
cp -r .claude-code-review /path/to/your/project/
```

### 2. Run Installation  
```bash
cd /path/to/your/project/
python .claude-code-review/install-fixed.py
```

### 3. Use the System
In Claude Code, say:
```
deep review code
```

**Done!** Claude will automatically analyze your code for security issues.

## 🎯 What You Get

✅ **Security Analysis**: SQL injection, XSS, auth bypasses  
✅ **Edge Case Detection**: Null values, boundary conditions, race conditions  
✅ **Concrete Fixes**: Not just problems - actual code solutions  
✅ **Priority Rankings**: Critical/High/Medium/Low severity levels  
✅ **Multi-Language**: Works with Python, JavaScript, Java, Go, Rust, C#  

## 📋 Example Result

```
🔍 DEEP CODE REVIEW RESULTS
==========================

📊 Analysis Summary:
- Files Reviewed: 15 Python files  
- Issues Found: 1 Critical, 3 High, 5 Medium, 8 Low

🚨 CRITICAL Issues (Fix Immediately):
- [CRITICAL] SQL Injection in login() | auth.py:45
  Fix: Replace f"SELECT * FROM users WHERE id={user_id}" 
       with cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))

🔴 HIGH Priority Issues (Fix Before Release):  
- [HIGH] Missing input validation | api.py:123
  Fix: Add validation before processing user input

🎯 Top 3 Priority Actions:
1. Fix SQL injection vulnerability (Critical)
2. Add input validation to API endpoints (High)  
3. Handle null pointer exceptions (Medium)
```

## 🎮 Trigger Commands

| Say This | Gets This |
|----------|-----------|  
| `deep review code` | **Full security audit** |
| `security audit` | Security vulnerabilities only |
| `check for vulnerabilities` | Critical issues focus |
| `review this codebase` | Comprehensive analysis |

## 🛠️ Customization

### Change Review Standards
Edit `claude-code-review.yaml`:
```yaml
### Security Analysis (Critical Priority)  
- **Custom Rule**: Check for specific patterns in your codebase
- **Compliance**: Add HIPAA/PCI-DSS requirements
```

### Adjust Project Focus  
Edit `CLAUDE.md`:
```markdown
### Project Context
- **API Security**: Focus on REST endpoint validation
- **Database**: Check for MongoDB injection patterns  
- **Frontend**: Review React components for XSS
```

## 🌍 Multi-Repository Usage

### Option A: Copy to Each Repo
```bash
cp -r .claude-code-review /path/to/repo1/  
cp -r .claude-code-review /path/to/repo2/  
cp -r .claude-code-review /path/to/repo3/
```

### Option B: Global Installation
```bash
# Set up once
mkdir ~/code-review-system
cp -r .claude-code-review/* ~/code-review-system/

# Use anywhere  
cd /any/repository
python ~/code-review-system/install-fixed.py
```

### Option C: Git Submodule
```bash
# Add as submodule  
git submodule add <repo-url> .claude-code-review
git submodule update --init
```

## 🔧 Troubleshooting

**"Installation failed"**
```bash
python .claude-code-review/install-fixed.py
```

**"Hooks not working"**
```bash
# Check Claude Code settings
cat ~/.anthropic/claude-code/settings.json
```

**"No issues found"**
- Try saying "security audit" instead
- Check if you have source code files (.py, .js, .java, etc.)

**"Permission errors"**
```bash  
chmod +x .claude-code-review/scripts/*.py
```

## 💡 Pro Tips

1. **Start Small**: Test on a small codebase first
2. **Fix Incrementally**: Address Critical and High issues first  
3. **Regular Reviews**: Run weekly or before releases
4. **Team Sharing**: Share results with security team
5. **Custom Rules**: Add your own security patterns to YAML

## 📞 Support

- **Issues**: Check the troubleshooting section above
- **Custom Rules**: Edit `claude-code-review.yaml`  
- **Project Settings**: Edit `CLAUDE.md`
- **Updates**: Re-run `install-fixed.py`

---

**🎉 Ready? Just say: "deep review code"**