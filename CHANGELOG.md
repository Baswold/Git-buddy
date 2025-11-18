# Changelog

All notable changes to Git Buddy will be documented in this file.

## [2.0.0] - 2025-01-18

### 🎉 Major UX Improvements

This release brings significant user experience enhancements while maintaining the familiar terminal UI.

### ✨ New Features

#### Smart Commit Messages
- **Automatic commit message generation** based on file changes
- Analyzes modified, new, and deleted files to suggest contextual messages
- Detects file types and patterns (e.g., "Add Python files", "Update documentation")
- Single file changes get specific messages (e.g., "Update README.md")

#### File Safety Features
- **Sensitive file detection** warns before pushing:
  - Environment files (.env, .env.local)
  - Credentials (credentials.json, secrets.yaml)
  - Private keys (.pem, .key, id_rsa)
  - Password and token files
- **Large file warnings** for files exceeding 10MB (configurable)
- Interactive confirmation before proceeding with sensitive/large files

#### Configuration Management
- **Persistent configuration** saved in `~/.gitbuddy_config.json`
- **Recent repositories** list (last 5 repos)
- Quick selection using numbers (e.g., "1" for first recent repo)
- Configurable settings:
  - `file_size_warning_mb`: Size threshold for warnings (default: 10)
  - `show_stats`: Toggle operation statistics (default: true)
  - `default_branch`: Default branch name (default: "main")

#### Network Resilience
- **Exponential backoff retry logic** for git operations
- Automatic retry on network failures (up to 4 attempts: 2s, 4s, 8s, 16s)
- Retry on timeout errors with progressive delays
- Clear user feedback during retry attempts

#### Repository Management
- **Commit history viewer** - View recent commits with graph
- **Repository statistics** after successful push:
  - Total commits count
  - Branch count
  - Contributors count
  - Operation timing
- **Interactive branch management**:
  - View all available branches
  - Quick branch switching
  - Create new branches with smart name suggestions
  - Branch name suggestions based on file changes

#### .gitignore Assistant
- **Automatic .gitignore suggestions** based on detected files
- Smart pattern detection for:
  - Python projects (*.pyc, __pycache__, *.egg-info)
  - Node.js projects (node_modules, npm-debug.log)
  - Environment files (.env, .env.local)
  - IDE files (.idea, .vscode, .DS_Store)
  - Build artifacts (dist/, build/, target/)
- One-click addition of suggested entries
- Avoids duplicate entries

#### Enhanced User Interface
- **Help command** - Type 'help' or '?' for quick reference
- **Version information** displayed in header (v2.0)
- **Performance metrics** - Operation timing displayed after success
- **Better prompts** with context-aware defaults
- **Multiple exit options** - 'quit', 'q', or 'exit'

### 🔧 Improvements

#### Better Error Handling
- More descriptive error messages
- Network-specific error detection and handling
- Graceful degradation when features aren't available

#### Code Quality
- Added type hints throughout codebase
- Improved function documentation
- Better separation of concerns
- Consistent error handling patterns

#### Both Versions Updated
- ✅ Full version (git_buddy.py) - Rich UI with all features
- ✅ Standalone version (gitbuddy_standalone.py) - Zero dependencies with all features

### 📊 Statistics

- **Lines of code added**: ~800+
- **New functions**: 15+
- **New features**: 10+
- **Configuration options**: 4
- **Supported file patterns**: 50+

### 🎯 UX Highlights

1. **Faster workflow** - Recent repos save 30+ seconds per operation
2. **Safer pushes** - Sensitive file warnings prevent credential leaks
3. **Smarter messages** - Auto-generated commit messages save time
4. **More resilient** - Network retry logic handles flaky connections
5. **Better informed** - Statistics show repository health at a glance

### 🔄 Migration Guide

No breaking changes! All existing workflows continue to work. New features are opt-in or automatic.

Configuration file is automatically created on first use at `~/.gitbuddy_config.json`.

### 📝 Documentation

- Updated README.md with new features
- Added CLAUDE.md for AI assistant guidance
- Comprehensive inline documentation
- Help command for quick reference

### 🙏 Acknowledgments

This release was developed with a focus on improving the daily workflow of developers while maintaining the simplicity and speed that makes Git Buddy useful.

---

## [1.0.0] - Previous Release

### Initial Features
- Basic git repository initialization
- File selection and staging
- Commit and push to GitHub
- URL validation
- Error handling for common git operations
- Rich terminal UI
- Standalone zero-dependency version
