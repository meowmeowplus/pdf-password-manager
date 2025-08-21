# 🔍 Deep Code Review Workflow

## 🎯 Activation Triggers

When you say any of these phrases, Claude automatically activates deep review mode:

- **"deep review code"** ← Primary trigger
- "security audit"
- "check for vulnerabilities" 
- "review this codebase"
- "find security issues"

## 🔄 Automated Review Process

### Phase 1: Load Configuration (5 seconds)
1. Read `claude-code-review.yaml` for security standards
2. Load `CLAUDE.md` for project-specific context
3. Activate security-focused analysis mode

### Phase 2: Codebase Discovery (10 seconds)
1. Use `Glob` tool to find all source files by language:
   - Python: `**/*.py` 
   - JavaScript: `**/*.js`, `**/*.ts`, `**/*.jsx`, `**/*.tsx`
   - Java: `**/*.java`
   - C#: `**/*.cs`
   - Go: `**/*.go`
   - Rust: `**/*.rs`
2. Prioritize files with security implications (auth, database, API)
3. Scan configuration files: `*.yaml`, `*.json`, `requirements.txt`, etc.

### Phase 3: Security Analysis (30-60 seconds)
1. **Critical Security Issues**: 
   - SQL injection vulnerabilities
   - XSS attack vectors
   - Authentication bypasses
   - Hardcoded credentials
   - File upload vulnerabilities

2. **High Priority Issues**:
   - Missing input validation
   - Error information disclosure
   - Insecure crypto usage
   - Authorization gaps
   - Resource leaks

3. **Medium Priority Issues**:
   - Weak error handling
   - Race conditions
   - Memory management issues
   - Dependency vulnerabilities

### Phase 4: Edge Case Detection (20 seconds)
- **Null/Empty Handling**: Check for null pointer exceptions
- **Boundary Conditions**: Array bounds, numeric limits
- **Network Failures**: Timeout handling, connection errors
- **Resource Exhaustion**: Memory limits, disk space
- **Concurrent Access**: Race conditions, deadlocks

### Phase 5: Code Quality Analysis (15 seconds)
- **Function Complexity**: Overly long or complex functions
- **Code Duplication**: DRY violations
- **Naming Conventions**: Unclear variable/function names
- **Error Handling**: Missing try-catch blocks
- **Resource Management**: Unclosed files/connections

## 📊 Severity Classification

### 🚨 CRITICAL (Drop everything and fix)
- **Authentication bypass**: Users can access without login
- **SQL injection**: Database can be compromised
- **Remote code execution**: Attacker can run arbitrary code
- **Hardcoded secrets**: API keys/passwords in source code

### 🔴 HIGH (Fix before release)
- **XSS vulnerabilities**: User data not sanitized in output
- **Missing authorization**: Users can access unauthorized data
- **Information disclosure**: Sensitive data in error messages
- **File upload issues**: Unrestricted file types/execution

### 🟡 MEDIUM (Fix in next sprint)
- **Input validation gaps**: Non-critical fields unvalidated
- **Error handling gaps**: Operations that could fail ungracefully
- **Resource leaks**: Memory/file handle leaks
- **Race conditions**: Concurrent access issues

### 🟢 LOW (Address in backlog)
- **Code quality**: Complex functions, poor naming
- **Performance**: Inefficient algorithms or queries
- **Documentation**: Missing or unclear comments
- **Style**: Formatting and convention issues

## 🔧 Fix Format

For each issue found, provide:

```
🚨 [SEVERITY] Issue Title
Location: filename.ext:line_number
Impact: What could go wrong
Attack Vector: How an attacker could exploit this

❌ Problematic Code:
[Show the vulnerable code]

✅ Secure Fix:
[Provide corrected code with explanation]

🛡️ Prevention:
[How to avoid this in future]
```

## 🎯 Output Template

```
🔍 DEEP CODE REVIEW RESULTS
==========================

📊 **Analysis Summary**:
- Files Reviewed: X source files
- Languages: Python, JavaScript, etc.
- Time: ~X minutes
- Issues Found: X Critical, X High, X Medium, X Low

🚨 **CRITICAL Issues** (Fix Immediately):
[List with code fixes]

🔴 **HIGH Priority Issues** (Fix Before Release):
[List with code fixes]

🟡 **MEDIUM Priority Issues** (Next Sprint):
[List with recommendations]

⚠️ **Edge Cases Unhandled**:
[Scenarios that could cause failures]

🔧 **Code Quality Improvements**:
[Maintainability and readability improvements]

✅ **Security Strengths Found**:
[Good practices already implemented]

🎯 **Top 3 Priority Actions**:
1. [Most critical fix with exact code]
2. [Second most critical fix with exact code]  
3. [Third most critical fix with exact code]

📋 **Prevention Checklist**:
□ Add input validation to all user inputs
□ Implement proper error handling  
□ Add unit tests for edge cases
□ Review third-party dependencies
□ Add security headers to web responses
```

## 🚀 Advanced Usage

### Targeted Reviews
- **"security audit for authentication"** → Focus only on auth code
- **"review API endpoints for vulnerabilities"** → Focus on API security
- **"check database queries for injection"** → Focus on SQL security
- **"review file upload handling"** → Focus on upload security

### Language-Specific Reviews  
- **"review Python code for security"** → Python-focused analysis
- **"audit JavaScript for XSS"** → JS/frontend security focus
- **"check Java code for vulnerabilities"** → Java-specific patterns

### CI/CD Integration
- **"pre-commit security check"** → Quick security scan
- **"release readiness review"** → Comprehensive pre-release audit

## 🛠️ Customization

### Project-Specific Standards
Edit `claude-code-review.yaml` to add:
- Custom security requirements
- Industry compliance standards (HIPAA, PCI-DSS, SOX)
- Technology-specific checks
- Team coding standards

### Response Tuning
Modify `CLAUDE.md` to adjust:
- Review depth and focus areas
- Output format preferences  
- Project context and constraints
- Team expertise level

## ⚡ Performance Tips

1. **Start Specific**: Use targeted triggers for faster results
2. **Staged Reviews**: Review by component/module for large codebases
3. **Incremental**: Review new/changed files first
4. **Priority Focus**: Address CRITICAL and HIGH issues first
5. **Automate**: Integrate with CI/CD for continuous security

Remember: The goal is to find **actionable security issues** with **concrete fixes**, not just code style problems!