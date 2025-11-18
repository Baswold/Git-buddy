# Git Buddy 🚀

A powerful terminal-based Git helper tool that makes pushing files to GitHub repositories easy, safe, and intuitive.

## ✨ Version 2.0 - Major UX Improvements!

Git Buddy v2.0 brings a comprehensive set of new features focused on improving your daily git workflow while maintaining the simplicity you love.

## 🎯 Key Features

### Core Functionality
- 🖥️ **Beautiful Terminal UI** - Rich, interactive command-line interface
- 📁 **Smart File Selection** - Intelligent change detection and file filtering
- 🔗 **Flexible URL Support** - All GitHub URL formats supported
- ⚡ **Network Resilience** - Automatic retry with exponential backoff
- 🔐 **Enhanced Security** - Sensitive file detection and warnings
- 📊 **Performance Tracking** - Detailed statistics and timing

### Smart Features (NEW in v2.0)
- 🧠 **Smart Commit Messages** - Auto-generated based on your changes
- ⚠️ **File Safety Warnings** - Detects credentials, large files, sensitive data
- 📦 **Configuration Management** - Persistent settings and recent repos
- 🌿 **Branch Management** - Quick switching, creation with smart suggestions
- 📝 **.gitignore Assistant** - Automatic pattern detection and suggestions
- 📚 **Commit History Viewer** - Visual git log with graph
- 💾 **Stash Management** - Interactive stash operations
- ⚡ **Quick Commands** - Fast workflows for power users
- 🧹 **Repository Cleanup** - Maintenance utilities built-in

## Installation

### Option 1: Global Installation (Recommended)
Install Git Buddy globally so you can run it from anywhere with just `gitbuddy`:

```bash
# Navigate to the git_buddy directory
cd /path/to/git_buddy

# Install globally
pip install -e .
```

Now you can run `gitbuddy` from any directory!

### Option 2: Local Installation
1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Simply run from any project directory:
```bash
gitbuddy
```

### Interactive Commands

Git Buddy now supports powerful commands for enhanced workflows:

#### Main Commands
- **help** or **?** - Show comprehensive help
- **config** - View and edit configuration settings
- **stats** - Display repository statistics
- **history** - View commit history with graph
- **stash** - Manage git stashes interactively
- **diff** - Show detailed diff with statistics
- **quick** - Fast commit & push workflow
- **cleanup** - Repository maintenance utilities
- **quit**, **q**, or **exit** - Exit the application

#### Quick Workflows

**Standard Push:**
1. Run `gitbuddy`
2. Enter repository URL (or select from recent)
3. Review changes and select files
4. Use suggested commit message or write your own
5. Confirm and push!

**Quick Commit & Push:**
1. Run `gitbuddy`
2. Type `quick`
3. Confirm commit message
4. Done!

**View Changes:**
1. Run `gitbuddy`
2. Type `diff`
3. Review all changes with statistics

## Supported Repository URL Formats

- `https://github.com/username/repository`
- `https://github.com/username/repository.git`
- `git@github.com:username/repository.git`
- `username/repository`

## GitHub Authentication

For private repositories or first-time pushes, you'll need to authenticate:

### Option 1: Personal Access Token (Recommended)
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` permissions
3. Use your GitHub username and the token as your password when prompted

### Option 2: SSH Key Authentication
1. Generate an SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add the public key to your GitHub account
3. Use SSH URL format: `git@github.com:username/repository.git`

## 🎨 Enhanced UX Features

### Smart Commit Messages
Git Buddy analyzes your changes and suggests contextual commit messages:
- **Single file**: "Add README.md"
- **Multiple Python files**: "Add Python files"
- **Documentation**: "Update documentation"
- **Tests**: "Add tests"

### File Safety Features

**Sensitive File Detection** warns you before pushing:
- Environment files (.env, .env.local)
- Credentials (credentials.json, secrets.yaml)
- Private keys (.pem, .key, id_rsa)
- Password/token files

**Large File Warnings** (configurable, default 10MB):
- Alerts you to files that may slow down your repository
- Prevents accidental commits of large assets

### Configuration Management

Settings are saved in `~/.gitbuddy_config.json`:
```json
{
  "recent_repos": ["user/repo1", "user/repo2"],
  "file_size_warning_mb": 10,
  "show_stats": true,
  "default_branch": "main"
}
```

Access via `config` command to:
- Adjust file size warning threshold
- Toggle statistics display
- Set default branch name
- Clear recent repositories list

### Network Resilience

Git operations automatically retry on network failures:
- Up to 4 retry attempts
- Exponential backoff (2s, 4s, 8s, 16s)
- Works for push, pull, and fetch operations
- Clear progress feedback

## Advanced Features

### Branch Management
- View all available branches
- Quick branch switching
- Create branches with smart name suggestions
- Suggestions based on file changes

### .gitignore Assistant
Automatically suggests patterns based on detected files:
- Python: `*.pyc`, `__pycache__/`, `*.egg-info/`
- Node.js: `node_modules/`, `npm-debug.log`
- Environment: `.env`, `.env.local`
- IDEs: `.idea/`, `.vscode/`, `.DS_Store`
- One-click addition to `.gitignore`

### Stash Management
Interactive stash operations:
- List all stashes
- Apply/pop/drop stashes
- Create new stashes with messages
- Clear all stashes (with confirmation)

### Repository Cleanup
- Prune remote branches
- Clean untracked files (dry-run and execute)
- Garbage collection
- Repository optimization

### Detailed Diff Viewing
- Diff statistics for all changes
- Color-coded output (additions/deletions)
- Configurable context lines
- Smart pagination for large diffs

## Error Handling

Git Buddy includes comprehensive error handling:

- **Repository not found** - Detailed troubleshooting steps
- **Permission denied** - Authentication guidance with token setup
- **Push conflicts** - Automatic conflict resolution with multiple strategies
- **Invalid URLs** - Examples of supported formats
- **Network failures** - Automatic retry with backoff
- **Missing configuration** - Helpful setup instructions

## 📊 What's New in v2.0

- **Smart commit message generation** - Save time with AI-like suggestions
- **Configuration system** - Remember your preferences
- **Recent repositories** - Quick access to your last 5 repos
- **Sensitive file detection** - Prevent credential leaks
- **Network retry logic** - Handle flaky connections gracefully
- **Branch management** - Switch and create branches easily
- **.gitignore suggestions** - Smart pattern detection
- **Stash management** - Full stash workflow support
- **Repository statistics** - Detailed metrics after operations
- **Quick commands** - Power user workflows
- **Cleanup utilities** - Keep your repo healthy
- **Enhanced diff viewing** - Better visualization of changes
- **Help system** - Comprehensive in-app documentation

See [CHANGELOG.md](CHANGELOG.md) for complete details.

## 🔧 Requirements

- Python 3.6+
- Git installed and configured
- `rich` library for terminal UI (full version)
- No dependencies for standalone version!

## 🆚 Two Versions

### Full Version (`git_buddy.py`)
- Rich terminal UI with colors and tables
- All features enabled
- Requires `rich` library
- Best for regular use

### Standalone Version (`gitbuddy_standalone.py`)
- Zero external dependencies
- Pure Python standard library
- All major features included
- Perfect for servers or restricted environments

## 💡 Pro Tips

1. **Use recent repos** - Type `1-5` instead of full URL
2. **Quick mode** - Type `quick` for fast commit & push
3. **Check before push** - Type `diff` to review changes
4. **Configure once** - Type `config` to set your preferences
5. **View history** - Type `history` before pushing
6. **Manage stashes** - Type `stash` for WIP changes
7. **Clean up** - Type `cleanup` for repository maintenance

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📝 License

MIT License - feel free to use and modify as needed!

## 🌟 Star this project

If you find Git Buddy useful, please give it a star on GitHub!