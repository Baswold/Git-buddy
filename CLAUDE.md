# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Git Buddy is a terminal-based Git helper tool that simplifies pushing files to GitHub repositories. The project provides two implementations:
- **Full version** (`git_buddy.py`) - Rich terminal UI with advanced features
- **Standalone version** (`gitbuddy_standalone.py`) - No external dependencies, simplified interface

## Architecture

### Core Components

The project follows a class-based architecture in the full version:

**GitBuddy Class** (`git_buddy.py:29-637`)
- Main application controller
- Handles terminal UI using Rich library
- Manages git operations and GitHub interactions
- Provides interactive file selection and change detection

**Key Methods:**
- `validate_github_url()` - URL parsing and validation
- `get_git_status()` - Git status parsing and file categorization  
- `display_file_selection()` - Interactive file selection with smart change detection
- `handle_push_conflicts()` - Automatic conflict resolution with multiple strategies
- `push_to_github()` - GitHub push with comprehensive error handling

### Two Implementation Approaches

1. **Rich UI Version** (`git_buddy.py`)
   - Dependency: Rich library for terminal formatting
   - Advanced features: file diff viewing, progress indicators, tables
   - Interactive prompts with validation

2. **Standalone Version** (`gitbuddy_standalone.py`)
   - Zero external dependencies
   - ANSI color codes for basic formatting
   - Simplified workflow for maximum compatibility

### Git Workflow Implementation

Both versions implement the same core git workflow:
1. Repository initialization (if needed)
2. Smart file detection (changed vs all files)
3. Staging and committing
4. Remote configuration
5. Push with conflict resolution

## Development Commands

### Installation and Setup
```bash
# Install dependencies for full version
pip install -r requirements.txt

# Install as global command
pip install -e .

# Run full version locally
python git_buddy.py

# Run standalone version
python gitbuddy_standalone.py
```

### Testing the Application
```bash
# Test the installed command
gitbuddy

# Test in a new directory
mkdir test_repo && cd test_repo
gitbuddy
```

### Package Management
```bash
# Build distribution
python setup.py sdist bdist_wheel

# Install from source
pip install -e .
```

## Key Features Implementation

### Smart Change Detection (`git_buddy.py:63-93`, `gitbuddy_standalone.py:115-143`)
- Parses `git status --porcelain` output
- Categorizes files as modified, new, or deleted
- Offers selective pushing of only changed files

### URL Validation (`git_buddy.py:42-61`, `gitbuddy_standalone.py:95-113`)
Supports multiple GitHub URL formats:
- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`  
- `git@github.com:owner/repo.git`
- `owner/repo` (shorthand)

### Conflict Resolution (`git_buddy.py:454-508`, `gitbuddy_standalone.py:289-316`)
Progressive conflict resolution strategy:
1. Pull and merge with `--allow-unrelated-histories`
2. Force push with lease (safer)
3. Regular force push (with confirmation)

### Error Handling
Comprehensive error detection and user guidance for:
- Repository not found
- Authentication failures
- Push conflicts
- Missing git configuration

## File Structure

```
git_buddy/
├── git_buddy.py              # Main application (Rich UI)
├── gitbuddy_standalone.py    # Standalone version (no deps)
├── setup.py                  # Package configuration
├── requirements.txt          # Dependencies (only Rich)
├── install.sh               # One-line installer script
├── README.md                # Full documentation
├── README_simple.md         # Simplified documentation
└── git_buddy.egg-info/      # Package metadata
```

## Installation Methods

1. **Global Installation**: `pip install -e .` creates `gitbuddy` command
2. **One-line Install**: `curl -sSL [url] | bash` downloads standalone version
3. **Manual**: Download `gitbuddy_standalone.py` directly

## Error Handling Patterns

The codebase implements consistent error handling:
- Git commands use `subprocess.run()` with timeout (30s)
- Return tuples of `(success: bool, output: str)`
- User-friendly error messages with actionable solutions
- Graceful keyboard interrupt handling

## Dependencies

- **Full Version**: Rich library (>=13.0.0) for terminal UI
- **Standalone**: Pure Python 3.6+ standard library only
- **System**: Git must be installed and configured