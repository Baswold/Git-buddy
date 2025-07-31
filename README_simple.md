# Git Buddy 🚀

**The easiest way to push files to GitHub from terminal!**

## ⚡ One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/Baswold/Git-buddy/main/install.sh | bash
```

That's it! No pip, no dependencies, no hassle.

## 🎯 Usage

```bash
cd /path/to/your/project
gitbuddy
```

## ✨ Features

- **🔍 Smart Detection** - Only pushes changed files by default
- **🎨 Beautiful Interface** - Clean terminal UI with colors
- **⚡ Super Fast** - No external dependencies
- **🛡️ Safe** - Handles conflicts and authentication automatically
- **📱 Single File** - Just one Python script

## 📋 What It Does

1. **Detects changes** - Shows new, modified, deleted files
2. **Smart selection** - Push only what changed (or everything)
3. **Handles Git** - Init, add, commit, push automatically
4. **Fixes conflicts** - Merges or force-pushes when needed
5. **Guides you** - Clear error messages and solutions

## 🔧 Manual Install

If you prefer manual installation:

```bash
# Download
curl -O https://raw.githubusercontent.com/Baswold/Git-buddy/main/gitbuddy_standalone.py

# Make executable
chmod +x gitbuddy_standalone.py

# Move to PATH
sudo mv gitbuddy_standalone.py /usr/local/bin/gitbuddy
```

## 🎮 Example Usage

```bash
$ gitbuddy

🚀 Git Buddy - Terminal Git Helper
==================================

Enter GitHub repository URL: https://github.com/username/myproject

Git Status:
New files (2):
  + README.md
  + main.py

Modified files (1):
  M config.json

Push (c)hanged files only, (a)ll files, or (q)uit (c): 

Enter commit message (Update files via Git Buddy): Add new features

Summary:
Repository: https://github.com/username/myproject.git
Push mode: Changed files only
Commit message: Add new features

Proceed with git operations? (y): 

✓ Git repository initialized
✓ Changes committed successfully  
✓ Remote origin configured
✓ Successfully pushed to GitHub!

🎉 Success! Your files have been pushed to GitHub!
```

## 🔒 Requirements

- Python 3.6+ (usually pre-installed)
- Git (install with `brew install git` or `apt install git`)

## 🆘 Need Help?

The tool provides helpful error messages and solutions for:
- Authentication issues
- Repository conflicts  
- Missing configurations
- Network problems

**That's it! Enjoy pushing to GitHub with ease! 🎉**