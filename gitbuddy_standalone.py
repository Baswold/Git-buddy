#!/usr/bin/env python3
"""
Git Buddy - Standalone Version
A single-file terminal Git helper tool for easy GitHub operations
No external dependencies required!
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from urllib.parse import urlparse
import time
import json
from datetime import datetime

# Simple terminal colors without rich dependency
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def colored(text: str, color: str) -> str:
    """Add color to text"""
    return f"{color}{text}{Colors.END}"

def print_header():
    """Print application header"""
    print("=" * 80)
    print(colored("🚀 Git Buddy - Terminal Git Helper v2.0", Colors.BOLD + Colors.BLUE))
    print(colored("Push your files to GitHub with ease | Type 'help' for commands", Colors.CYAN))
    print("=" * 80)

def print_help():
    """Print help information"""
    print("\n" + "=" * 80)
    print(colored("Git Buddy Help", Colors.BOLD + Colors.CYAN))
    print("=" * 80)
    print(colored("\nFeatures:", Colors.BOLD))
    print("• Smart commit message suggestions based on file changes")
    print("• Automatic detection of sensitive files (.env, credentials, etc.)")
    print("• Large file warnings (>10MB by default)")
    print("• Recent repository quick selection")
    print("• Retry logic for network failures")
    print("• Detailed operation statistics")
    print(colored("\nTips:", Colors.BOLD))
    print("• Use numbers to quickly select recent repositories")
    print("• Smart commit messages are generated based on your changes")
    print("• The tool warns you about potentially sensitive files")
    print("• Network failures are automatically retried with exponential backoff")
    print("• Configuration is saved in ~/.gitbuddy_config.json")
    print(colored("\nURL Formats Supported:", Colors.BOLD))
    print("• https://github.com/username/repo")
    print("• git@github.com:username/repo.git")
    print("• username/repo")
    print(colored("\nKeyboard Shortcuts:", Colors.BOLD))
    print("• Type 'quit' or 'q' to exit")
    print("• Type 'help' or '?' for this help message")
    print("• Ctrl+C to cancel at any time")
    print("=" * 80 + "\n")

def load_config() -> Dict:
    """Load configuration from file"""
    config_file = Path.home() / '.gitbuddy_config.json'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "recent_repos": [],
        "default_branch": "main",
        "auto_push_changed": True,
        "show_stats": True,
        "file_size_warning_mb": 10
    }

def save_config(config: Dict):
    """Save configuration to file"""
    try:
        config_file = Path.home() / '.gitbuddy_config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass

def add_recent_repo(config: Dict, repo_url: str):
    """Add repository to recent list"""
    if repo_url not in config["recent_repos"]:
        config["recent_repos"].insert(0, repo_url)
        config["recent_repos"] = config["recent_repos"][:5]
        save_config(config)

def print_status(status: str, message: str):
    """Print status message with color"""
    if status == "success":
        print(f"{colored('✓', Colors.GREEN)} {message}")
    elif status == "error":
        print(f"{colored('✗', Colors.RED)} {message}")
    elif status == "warning":
        print(f"{colored('⚠', Colors.YELLOW)} {message}")
    elif status == "info":
        print(f"{colored('ℹ', Colors.BLUE)} {message}")

def get_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default"""
    if default:
        full_prompt = f"{prompt} ({default}): "
    else:
        full_prompt = f"{prompt}: "
    
    try:
        response = input(full_prompt).strip()
        return response if response else (default or "")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

def confirm(prompt: str) -> bool:
    """Ask for yes/no confirmation"""
    while True:
        response = get_input(f"{prompt} (y/n)", "y").lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print(colored("Please enter 'y' or 'n'", Colors.RED))

def run_command(command: List[str], cwd: Path = None, retry_count: int = 0) -> Tuple[bool, str]:
    """Execute command and return success status and output with retry logic"""
    if cwd is None:
        cwd = Path.cwd()

    max_retries = 4 if retry_count > 0 else 0
    attempt = 0

    while attempt <= max_retries:
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, result.stdout + result.stderr

            output = result.stdout + result.stderr
            is_network_error = any(err in output.lower() for err in
                ['network', 'connection', 'timeout', 'ssl', 'tls', 'unable to access'])

            if is_network_error and attempt < max_retries:
                backoff_time = 2 ** attempt
                print(colored(f"Network error detected, retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries})", Colors.YELLOW))
                time.sleep(backoff_time)
                attempt += 1
                continue

            return False, output

        except subprocess.TimeoutExpired:
            if attempt < max_retries:
                backoff_time = 2 ** attempt
                print(colored(f"Command timed out, retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries})", Colors.YELLOW))
                time.sleep(backoff_time)
                attempt += 1
                continue
            return False, "Command timed out after 30 seconds"
        except Exception as e:
            return False, str(e)

    return False, "Max retries exceeded"

def suggest_commit_message(modified_files: List[str], new_files: List[str], deleted_files: List[str]) -> str:
    """Generate smart commit message based on changes"""
    total_changes = len(modified_files) + len(new_files) + len(deleted_files)

    if total_changes == 0:
        return "Update files via Git Buddy"

    # Analyze file types
    file_types = {}
    all_files = modified_files + new_files + deleted_files

    for file in all_files:
        ext = Path(file).suffix.lower()
        if ext:
            file_types[ext] = file_types.get(ext, 0) + 1

    # Determine primary action
    if len(new_files) > len(modified_files) + len(deleted_files):
        action = "Add"
    elif len(deleted_files) > len(modified_files) + len(new_files):
        action = "Remove"
    else:
        action = "Update"

    # Create suggestions
    suggestions = []

    if total_changes == 1:
        file = all_files[0]
        if file in new_files:
            return f"Add {file}"
        elif file in modified_files:
            return f"Update {file}"
        else:
            return f"Remove {file}"

    # File type specific
    if file_types:
        dominant_type = max(file_types, key=file_types.get)
        type_names = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.java': 'Java', '.cpp': 'C++', '.html': 'HTML', '.css': 'CSS',
            '.md': 'documentation', '.json': 'configuration', '.sh': 'scripts'
        }
        type_name = type_names.get(dominant_type, f"{dominant_type[1:]} files")
        return f"{action} {type_name}"

    return f"{action} {total_changes} file{'s' if total_changes > 1 else ''}"

def check_sensitive_files(files: List[str]) -> List[Tuple[str, str]]:
    """Detect potentially sensitive files"""
    sensitive_patterns = {
        r'\.env$': 'Environment variables',
        r'credentials?\.json$': 'Credentials file',
        r'secrets?\.ya?ml$': 'Secrets configuration',
        r'\.pem$': 'Private key',
        r'password': 'Password file',
        r'token': 'Token file',
    }

    sensitive_files = []
    for file_path in files:
        for pattern, description in sensitive_patterns.items():
            if re.search(pattern, file_path, re.IGNORECASE):
                sensitive_files.append((file_path, description))
                break

    return sensitive_files

def check_file_sizes(files: List[str], threshold_mb: int = 10) -> List[Tuple[str, float]]:
    """Check for large files"""
    large_files = []
    threshold_bytes = threshold_mb * 1024 * 1024

    for file_path in files:
        try:
            size = Path(file_path).stat().st_size
            if size > threshold_bytes:
                size_mb = size / (1024 * 1024)
                large_files.append((file_path, size_mb))
        except Exception:
            pass

    return large_files

def display_file_warnings(files: List[str], config: Dict) -> bool:
    """Display warnings for files"""
    sensitive_files = check_sensitive_files(files)
    large_files = check_file_sizes(files, config.get("file_size_warning_mb", 10))

    if not (sensitive_files or large_files):
        return True

    print(colored("\n⚠ File Warnings:", Colors.BOLD + Colors.YELLOW))

    if large_files:
        print(colored("\nLarge Files Detected:", Colors.BOLD))
        for file_path, size_mb in large_files:
            print(f"  {colored('•', Colors.YELLOW)} {file_path}: {size_mb:.2f} MB")

    if sensitive_files:
        print(colored("\nPotentially Sensitive Files Detected:", Colors.BOLD + Colors.RED))
        for file_path, description in sensitive_files:
            print(f"  {colored('⚠', Colors.RED)} {file_path}: {description}")

    return confirm("Do you want to proceed anyway?")

def validate_github_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate and parse GitHub repository URL"""
    if not url:
        return False, "URL cannot be empty"
        
    patterns = [
        r'^https://github\.com/([^/]+)/([^/]+)/?(?:\.git)?$',
        r'^git@github\.com:([^/]+)/([^/]+)\.git$',
        r'^([^/]+)/([^/]+)$'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url.strip())
        if match:
            owner, repo = match.groups()
            repo = repo.replace('.git', '')
            return True, f"https://github.com/{owner}/{repo}.git"
            
    return False, "Invalid GitHub URL format. Use: https://github.com/owner/repo or owner/repo"

def get_git_status() -> Tuple[List[str], List[str], List[str]]:
    """Get git status and return lists of modified, new, and deleted files"""
    success, output = run_command(['git', 'status', '--porcelain'])
    
    modified_files = []
    new_files = []
    deleted_files = []
    
    if success and output:
        for line in output.strip().split('\n'):
            if len(line) < 3:
                continue
                
            status_code = line[:2]
            file_path = line[3:]
            
            if status_code.strip() in ['M', 'MM', 'AM']:
                modified_files.append(file_path)
            elif status_code.strip() in ['A', '??', 'AM']:
                new_files.append(file_path)
            elif status_code.strip() in ['D', 'AD', 'MD']:
                deleted_files.append(file_path)
            elif status_code[0] in ['M', 'A', '?'] and status_code[1] in ['M', 'A', '?']:
                if status_code[0] == '?' or status_code[1] == '?':
                    new_files.append(file_path)
                else:
                    modified_files.append(file_path)
    
    return modified_files, new_files, deleted_files

def display_git_status():
    """Display current git status with colors"""
    modified_files, new_files, deleted_files = get_git_status()
    
    if not any([modified_files, new_files, deleted_files]):
        print_status("success", "Working directory clean - no changes detected")
        return False
    
    print(colored("\nGit Status:", Colors.BOLD))
    
    if new_files:
        print(colored(f"\nNew files ({len(new_files)}):", Colors.BOLD + Colors.GREEN))
        for file in new_files:
            print(f"  {colored('+', Colors.GREEN)} {file}")
    
    if modified_files:
        print(colored(f"\nModified files ({len(modified_files)}):", Colors.BOLD + Colors.YELLOW))
        for file in modified_files:
            print(f"  {colored('M', Colors.YELLOW)} {file}")
    
    if deleted_files:
        print(colored(f"\nDeleted files ({len(deleted_files)}):", Colors.BOLD + Colors.RED))
        for file in deleted_files:
            print(f"  {colored('-', Colors.RED)} {file}")
    
    return True

def get_current_branch() -> str:
    """Get the current git branch name"""
    success, output = run_command(['git', 'branch', '--show-current'])
    if success and output.strip():
        return output.strip()
    
    success, output = run_command(['git', 'status', '--porcelain', '-b'])
    if success and output:
        first_line = output.split('\n')[0]
        if '##' in first_line:
            branch_info = first_line.replace('## ', '')
            if '...' in branch_info:
                return branch_info.split('...')[0]
            return branch_info
    
    return "main"

def initialize_git_repo() -> bool:
    """Initialize git repository if not already initialized"""
    git_dir = Path.cwd() / '.git'
    if git_dir.exists():
        print_status("success", "Git repository already initialized")
        return True
        
    print_status("info", "Initializing git repository...")
    success, output = run_command(['git', 'init'])
    
    if success:
        print_status("success", "Git repository initialized")
        return True
    else:
        print_status("error", f"Failed to initialize git repository: {output}")
        return False

def add_and_commit_changes(commit_message: str) -> bool:
    """Add all changes and commit them"""
    print_status("info", "Adding and committing changes...")
    
    # Add all changes
    success, output = run_command(['git', 'add', '.'])
    if not success:
        print_status("error", f"Failed to add files: {output}")
        return False
    
    # Check for git user configuration
    success, output = run_command(['git', 'commit', '-m', commit_message])
    
    if success:
        print_status("success", "Changes committed successfully")
        return True
    else:
        if "Please tell me who you are" in output:
            print_status("error", "Git user not configured. Please run:")
            print("  git config --global user.email 'you@example.com'")
            print("  git config --global user.name 'Your Name'")
            return False
        elif "nothing to commit" in output.lower():
            print_status("warning", "No changes to commit")
            return True
        else:
            print_status("error", f"Failed to commit: {output}")
            return False

def add_remote_origin(repo_url: str) -> bool:
    """Add remote origin to the repository"""
    success, output = run_command(['git', 'remote', 'get-url', 'origin'])
    
    if success:
        current_url = output.strip()
        if current_url == repo_url:
            print_status("success", "Remote origin already set correctly")
            return True
        else:
            print_status("info", f"Updating remote origin...")
            success, output = run_command(['git', 'remote', 'set-url', 'origin', repo_url])
    else:
        print_status("info", "Adding remote origin...")
        success, output = run_command(['git', 'remote', 'add', 'origin', repo_url])
    
    if success:
        print_status("success", "Remote origin configured")
        return True
    else:
        print_status("error", f"Failed to configure remote: {output}")
        return False

def push_to_github(branch: str) -> bool:
    """Push changes to GitHub with smart error handling and retry logic"""
    print_status("info", f"Pushing to GitHub ({branch} branch)...")

    # Show progress
    print("⠋ Pushing to GitHub...", end="", flush=True)

    # Use retry logic with exponential backoff
    success, output = run_command(['git', 'push', '-u', 'origin', branch], retry_count=4)
    print("\r" + " " * 30 + "\r", end="")  # Clear progress indicator
    
    if success:
        print_status("success", "Successfully pushed to GitHub!")
        return True
    else:
        # Handle common push errors
        if "remote: Repository not found" in output or "repository does not exist" in output.lower():
            print_status("error", "Repository not found. Make sure:")
            print("  1. The repository exists on GitHub")
            print("  2. You have access to the repository")
            print("  3. Your GitHub credentials are configured")
            return False
        elif "Permission denied" in output or "Authentication failed" in output:
            print_status("error", "Permission denied. Please check your GitHub authentication:")
            print("  1. Generate a personal access token at: https://github.com/settings/tokens")
            print("  2. Use your GitHub username and token as password when prompted")
            return False
        elif "support for password authentication was removed" in output.lower():
            print_status("error", "Password authentication is no longer supported.")
            print("  1. Generate a personal access token: https://github.com/settings/tokens")
            print("  2. Use token as password when Git asks for credentials")
            return False
        elif any(keyword in output.lower() for keyword in ["failed to push", "rejected", "non-fast-forward"]):
            # Try to handle push conflicts
            print_status("warning", "Push rejected. Attempting to resolve...")
            
            # Try pull with merge
            print_status("info", "Trying to pull and merge remote changes...")
            success, pull_output = run_command(['git', 'pull', 'origin', branch, '--allow-unrelated-histories'])
            
            if success:
                print_status("success", "Successfully merged remote changes")
                success, push_output = run_command(['git', 'push', '-u', 'origin', branch])
                if success:
                    print_status("success", "Successfully pushed after merge!")
                    return True
            
            # Ask for force push
            if confirm("Force push (this will overwrite remote repository)?"):
                success, force_output = run_command(['git', 'push', '--force-with-lease', 'origin', branch])
                if success:
                    print_status("success", "Successfully force pushed!")
                    return True
                else:
                    print_status("error", f"Force push failed: {force_output}")
            
            return False
        else:
            print_status("error", f"Push failed: {output}")
            return False

def main():
    """Main application loop with enhanced features"""
    print_header()
    config = load_config()

    try:
        while True:
            start_time = time.time()

            # Show recent repos if available
            if config["recent_repos"]:
                print(colored("\nRecent Repositories:", Colors.BOLD))
                for i, repo in enumerate(config["recent_repos"][:5], 1):
                    print(f"  {i}. {repo}")

            # Get repository URL
            repo_url = get_input("\nEnter GitHub repository URL (number for recent, 'help', or 'quit')")

            if repo_url.lower() in ['quit', 'q', 'exit']:
                print("👋 Goodbye!")
                break

            if repo_url.lower() in ['help', '?']:
                print_help()
                continue

            # Check if user selected a recent repo
            if repo_url.isdigit() and config["recent_repos"]:
                repo_index = int(repo_url) - 1
                if 0 <= repo_index < len(config["recent_repos"]):
                    repo_url = config["recent_repos"][repo_index]
                    print_status("success", f"Selected: {repo_url}")

            # Validate URL
            is_valid, parsed_url = validate_github_url(repo_url)
            if not is_valid:
                print_status("error", parsed_url)
                continue

            print_status("success", f"Repository URL: {parsed_url}")

            # Add to recent repos
            add_recent_repo(config, parsed_url)

            # Check if git repo exists and show status
            git_dir = Path.cwd() / '.git'
            has_git_repo = git_dir.exists()

            if has_git_repo:
                has_changes = display_git_status()
                if not has_changes:
                    print_status("info", "No changes to push")
                    if not confirm("Continue anyway?"):
                        continue

                # Ask what to push
                choice = get_input("Push (c)hanged files only, (a)ll files, or (q)uit", "c").lower()
                if choice.startswith('q'):
                    continue

                # Get changed files for smart commit message
                modified_files, new_files, deleted_files = get_git_status()
            else:
                choice = 'a'
                print_status("info", "New repository - will push all files")
                modified_files, new_files, deleted_files = [], [], []

            # Get all files for warnings
            try:
                all_files = [str(f) for f in Path.cwd().rglob('*') if f.is_file() and '.git' not in str(f)]
            except Exception:
                all_files = []

            # Display file warnings
            if all_files and not display_file_warnings(all_files, config):
                print_status("warning", "Operation cancelled by user")
                continue

            # Generate smart commit message
            suggested_message = suggest_commit_message(modified_files, new_files, deleted_files)

            # Get commit message with smart suggestion
            commit_message = get_input(f"Enter commit message", suggested_message)

            # Confirm before proceeding
            print(f"\n{colored('Summary:', Colors.BOLD)}")
            print(f"Repository: {parsed_url}")
            print(f"Push mode: {'Changed files only' if choice.startswith('c') else 'All files'}")
            print(f"Commit message: {commit_message}")

            if not confirm("\nProceed with git operations?"):
                continue

            # Execute git operations
            if not initialize_git_repo():
                continue

            if not add_and_commit_changes(commit_message):
                continue

            if not add_remote_origin(parsed_url):
                continue

            branch = get_current_branch()
            if push_to_github(branch):
                operation_time = time.time() - start_time
                print(f"\n{colored('🎉 Success! Your files have been pushed to GitHub!', Colors.BOLD + Colors.GREEN)}")

                # Show operation summary
                if config.get("show_stats", True):
                    print("\n" + "=" * 60)
                    print(colored("📊 Operation Summary", Colors.BOLD + Colors.CYAN))
                    print("=" * 60)
                    print(f"Operation time: {operation_time:.2f}s")
                    print(f"Commit message: {commit_message}")
                    print(f"Branch: {branch}")
                    print("=" * 60)

            # Ask if user wants to continue
            if not confirm("\nPush to another repository?"):
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print_status("error", f"Unexpected error: {e}")

if __name__ == "__main__":
    main()