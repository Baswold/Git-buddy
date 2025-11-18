# Changelog

All notable changes to Git Buddy will be documented in this file.

## [2.0.0] - 2025-01-18

### 🎉 Major UX Improvements + Advanced Power User Features

This release brings significant user experience enhancements while maintaining the familiar terminal UI, plus a comprehensive set of advanced commands for power users.

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
- **Command system** - Type commands instead of URLs for special operations

#### Power User Commands (NEW)
- **config** - Interactive configuration management
  - View and edit all settings in one place
  - Adjust file size warning threshold
  - Toggle statistics display
  - Set default branch name
  - Clear recent repositories list

- **stats** - Repository statistics viewer
  - Total commit count
  - Branch count
  - Contributors count
  - Quick repository health check

- **history** - Enhanced commit history viewer
  - Visual graph representation
  - Color-coded output
  - Configurable number of commits

- **stash** - Complete stash management
  - List all stashes
  - Apply/pop/drop specific stashes
  - Create new stashes with custom messages
  - Clear all stashes (with confirmation)

- **diff** - Detailed diff viewer
  - Full repository diff with statistics
  - Color-coded additions/deletions
  - Smart pagination for large diffs
  - Line-by-line change visualization

- **quick** - Fast commit & push workflow
  - One-command commit and push
  - Smart commit message suggestions
  - Skip file selection for speed
  - Perfect for quick updates

- **cleanup** - Repository maintenance utilities
  - Prune remote branches
  - Clean untracked files (with dry-run option)
  - Garbage collection
  - Aggressive optimization
  - Safety confirmations for destructive operations

#### Enhanced Diff Viewing
- **Contextual line display** - Configurable context (default 3 lines)
- **Addition/deletion statistics** - Shows +/- counts per file
- **Better colorization** - Distinct colors for different change types
- **Truncation handling** - Smart handling of large files
- **File-specific diffs** - View individual file changes with stats

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

- **Lines of code added**: ~1200+
- **New functions**: 25+
- **New features**: 20+
- **New commands**: 8
- **Configuration options**: 4
- **Supported file patterns**: 50+
- **Advanced utilities**: 6

### 🎯 UX Highlights

1. **Faster workflow** - Recent repos save 30+ seconds per operation
2. **Safer pushes** - Sensitive file warnings prevent credential leaks
3. **Smarter messages** - Auto-generated commit messages save time
4. **More resilient** - Network retry logic handles flaky connections
5. **Better informed** - Statistics show repository health at a glance
6. **Power user mode** - Quick command for rapid iterations
7. **Complete control** - Stash, cleanup, and config management built-in
8. **Better visibility** - Enhanced diff viewing with full statistics
9. **One-stop shop** - All git operations in one interface
10. **Professional grade** - Repository maintenance utilities included

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
