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
from typing import List, Optional, Tuple
from urllib.parse import urlparse
import time

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
    print(colored("🚀 Git Buddy - Terminal Git Helper", Colors.BOLD + Colors.BLUE))
    print(colored("Push your files to GitHub with ease", Colors.CYAN))
    print("=" * 80)

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

def run_command(command: List[str], cwd: Path = None) -> Tuple[bool, str]:
    """Execute command and return success status and output"""
    if cwd is None:
        cwd = Path.cwd()
        
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 30 seconds"
    except Exception as e:
        return False, str(e)

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
    """Push changes to GitHub with smart error handling"""
    print_status("info", f"Pushing to GitHub ({branch} branch)...")
    
    # Show progress
    print("⠋ Pushing to GitHub...", end="", flush=True)
    
    success, output = run_command(['git', 'push', '-u', 'origin', branch])
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
    """Main application loop"""
    print_header()
    
    try:
        while True:
            # Get repository URL
            repo_url = get_input("\nEnter GitHub repository URL (or 'quit' to exit)")
            
            if repo_url.lower() == 'quit':
                print("👋 Goodbye!")
                break
            
            # Validate URL
            is_valid, parsed_url = validate_github_url(repo_url)
            if not is_valid:
                print_status("error", parsed_url)
                continue
            
            print_status("success", f"Repository URL: {parsed_url}")
            
            # Check if git repo exists and show status
            git_dir = Path.cwd() / '.git'
            if git_dir.exists():
                has_changes = display_git_status()
                if not has_changes:
                    print_status("info", "No changes to push")
                    continue
                
                # Ask what to push
                choice = get_input("Push (c)hanged files only, (a)ll files, or (q)uit", "c").lower()
                if choice.startswith('q'):
                    continue
            else:
                choice = 'a'  # Push all for new repos
                print_status("info", "New repository - will push all files")
            
            # Get commit message
            commit_message = get_input("Enter commit message", "Update files via Git Buddy")
            
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
                print(f"\n{colored('🎉 Success! Your files have been pushed to GitHub!', Colors.BOLD + Colors.GREEN)}")
            
            # Ask if user wants to continue
            if not confirm("\nPush to another repository?"):
                break
                
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print_status("error", f"Unexpected error: {e}")

if __name__ == "__main__":
    main()