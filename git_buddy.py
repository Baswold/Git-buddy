#!/usr/bin/env python3
"""
Git Buddy - Terminal GUI for Git operations
A simple tool to push files to GitHub repositories with terminal interface
"""

import os
import sys
import subprocess
import re
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse
import json

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
except ImportError:
    print("Error: Required packages not installed. Please run: pip install rich")
    sys.exit(1)

console = Console()

class GitBuddy:
    def __init__(self):
        self.console = console
        self.current_dir = Path.cwd()
        
    def display_header(self):
        """Display the application header"""
        header = Panel(
            Text("🚀 Git Buddy - Terminal Git Helper", style="bold blue"),
            subtitle="Push your files to GitHub with ease"
        )
        self.console.print(header)
        
    def validate_github_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """Validate and parse GitHub repository URL"""
        if not url:
            return False, "URL cannot be empty"
            
        # Handle different GitHub URL formats
        patterns = [
            r'^https://github\.com/([^/]+)/([^/]+)/?(?:\.git)?$',
            r'^git@github\.com:([^/]+)/([^/]+)\.git$',
            r'^([^/]+)/([^/]+)$'  # Just owner/repo
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url.strip())
            if match:
                owner, repo = match.groups()
                repo = repo.replace('.git', '')
                return True, f"https://github.com/{owner}/{repo}.git"
                
        return False, "Invalid GitHub URL format. Use: https://github.com/owner/repo or owner/repo"
    
    def get_files_in_directory(self, directory: Path = None) -> List[Path]:
        """Get all files in the current directory (excluding git and hidden files)"""
        if directory is None:
            directory = self.current_dir
            
        files = []
        ignore_patterns = ['.git', '__pycache__', '.pyc', '.DS_Store', '.egg-info', 'node_modules', '.vscode', '.idea']
        
        for item in directory.rglob('*'):
            if item.is_file():
                # Skip hidden files, git files, and common ignore patterns
                relative_path = str(item.relative_to(directory))
                should_skip = (
                    any(part.startswith('.') for part in item.parts) or
                    any(ignore in relative_path for ignore in ignore_patterns)
                )
                if not should_skip:
                    files.append(item)
        return sorted(files)
    
    def display_file_selection(self, files: List[Path]) -> List[Path]:
        """Display files and let user select which ones to push"""
        if not files:
            self.console.print("[red]No files found in the current directory[/red]")
            return []
            
        self.console.print("\n[bold]Files in current directory:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Index", style="dim", width=6)
        table.add_column("File Path", style="cyan")
        table.add_column("Size", style="green", width=10)
        
        for i, file_path in enumerate(files, 1):
            try:
                size = file_path.stat().st_size
                size_str = self.format_file_size(size)
            except:
                size_str = "N/A"
            table.add_row(str(i), str(file_path.relative_to(self.current_dir)), size_str)
            
        self.console.print(table)
        
        choice = Prompt.ask(
            "\n[bold]Select files to push[/bold]",
            choices=["all", "select", "quit"],
            default="all"
        )
        
        if choice == "quit":
            return []
        elif choice == "all":
            return files
        else:
            return self.select_specific_files(files)
    
    def select_specific_files(self, files: List[Path]) -> List[Path]:
        """Let user select specific files by index"""
        selected_files = []
        
        while True:
            selection = Prompt.ask(
                "\nEnter file numbers (comma-separated, e.g., 1,3,5) or 'done' to finish"
            )
            
            if selection.lower() == 'done':
                break
                
            try:
                indices = [int(i.strip()) for i in selection.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(files):
                        file_path = files[idx - 1]
                        if file_path not in selected_files:
                            selected_files.append(file_path)
                            self.console.print(f"[green]✓[/green] Added: {file_path.relative_to(self.current_dir)}")
                    else:
                        self.console.print(f"[red]Invalid index: {idx}[/red]")
            except ValueError:
                self.console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")
                
        return selected_files
    
    def format_file_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def run_git_command(self, command: List[str], cwd: Path = None) -> Tuple[bool, str]:
        """Execute git command and return success status and output"""
        if cwd is None:
            cwd = self.current_dir
            
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
    
    def initialize_git_repo(self) -> bool:
        """Initialize git repository if not already initialized"""
        git_dir = self.current_dir / '.git'
        if git_dir.exists():
            self.console.print("[green]✓[/green] Git repository already initialized")
            return True
            
        self.console.print("[yellow]Initializing git repository...[/yellow]")
        success, output = self.run_git_command(['git', 'init'])
        
        if success:
            self.console.print("[green]✓[/green] Git repository initialized")
            return True
        else:
            self.console.print(f"[red]✗[/red] Failed to initialize git repository: {output}")
            return False
    
    def add_files_to_git(self, files: List[Path]) -> bool:
        """Add selected files to git staging area"""
        self.console.print("[yellow]Adding files to git...[/yellow]")
        
        for file_path in files:
            relative_path = file_path.relative_to(self.current_dir)
            success, output = self.run_git_command(['git', 'add', str(relative_path)])
            
            if success:
                self.console.print(f"[green]✓[/green] Added: {relative_path}")
            else:
                self.console.print(f"[red]✗[/red] Failed to add {relative_path}: {output}")
                return False
                
        return True
    
    def commit_changes(self, commit_message: str) -> bool:
        """Commit changes with the provided message"""
        self.console.print("[yellow]Committing changes...[/yellow]")
        
        # First check if there are any changes to commit
        success, status_output = self.run_git_command(['git', 'status', '--porcelain'])
        if success and not status_output.strip():
            self.console.print("[yellow]No changes to commit[/yellow]")
            return True
            
        # Check for untracked files and add them
        success, status_output = self.run_git_command(['git', 'status', '--porcelain'])
        if success and status_output:
            untracked_files = [line[3:] for line in status_output.split('\n') if line.startswith('??')]
            if untracked_files:
                self.console.print(f"[yellow]Found {len(untracked_files)} untracked files, adding them...[/yellow]")
                for file in untracked_files:
                    self.run_git_command(['git', 'add', file])
        
        success, output = self.run_git_command(['git', 'commit', '-m', commit_message])
        
        if success:
            self.console.print("[green]✓[/green] Changes committed successfully")
            return True
        else:
            if "nothing to commit" in output.lower():
                self.console.print("[yellow]No changes to commit[/yellow]")
                return True
            elif "Please tell me who you are" in output:
                self.console.print("[red]✗[/red] Git user not configured. Please run:")
                self.console.print("  git config --global user.email 'you@example.com'")
                self.console.print("  git config --global user.name 'Your Name'")
                return False
            else:
                self.console.print(f"[red]✗[/red] Failed to commit: {output}")
                return False
    
    def add_remote_origin(self, repo_url: str) -> bool:
        """Add remote origin to the repository"""
        # Check if remote already exists
        success, output = self.run_git_command(['git', 'remote', 'get-url', 'origin'])
        
        if success:
            current_url = output.strip()
            if current_url == repo_url:
                self.console.print("[green]✓[/green] Remote origin already set correctly")
                return True
            else:
                self.console.print(f"[yellow]Updating remote origin from {current_url} to {repo_url}[/yellow]")
                success, output = self.run_git_command(['git', 'remote', 'set-url', 'origin', repo_url])
        else:
            self.console.print("[yellow]Adding remote origin...[/yellow]")
            success, output = self.run_git_command(['git', 'remote', 'add', 'origin', repo_url])
        
        if success:
            self.console.print("[green]✓[/green] Remote origin configured")
            return True
        else:
            self.console.print(f"[red]✗[/red] Failed to configure remote: {output}")
            return False
    
    def get_current_branch(self) -> str:
        """Get the current git branch name"""
        success, output = self.run_git_command(['git', 'branch', '--show-current'])
        if success and output.strip():
            return output.strip()
        
        # Fallback: try to get branch from git status
        success, output = self.run_git_command(['git', 'status', '--porcelain', '-b'])
        if success and output:
            first_line = output.split('\n')[0]
            if '##' in first_line:
                branch_info = first_line.replace('## ', '')
                if '...' in branch_info:
                    return branch_info.split('...')[0]
                return branch_info
        
        return "main"  # Default fallback

    def handle_push_conflicts(self, branch: str = "main") -> bool:
        """Handle push conflicts by trying different strategies"""
        self.console.print("[yellow]Attempting to resolve push conflicts...[/yellow]")
        
        # First, let's see what branch we're actually on
        current_branch = self.get_current_branch()
        if current_branch != branch:
            self.console.print(f"[yellow]Current branch is '{current_branch}', but trying to push to '{branch}'[/yellow]")
            
            # Try to checkout the target branch or create it
            success, output = self.run_git_command(['git', 'checkout', '-B', branch])
            if success:
                self.console.print(f"[green]✓[/green] Switched to branch '{branch}'")
            else:
                self.console.print(f"[yellow]Using current branch '{current_branch}' instead[/yellow]")
                branch = current_branch
        
        # Try to pull and merge
        self.console.print("[yellow]Trying to pull and merge remote changes...[/yellow]")
        success, output = self.run_git_command(['git', 'pull', 'origin', branch, '--allow-unrelated-histories'])
        
        if success:
            self.console.print("[green]✓[/green] Successfully merged remote changes")
            # Now try to push again
            success, output = self.run_git_command(['git', 'push', '-u', 'origin', branch])
            if success:
                self.console.print("[green]✓[/green] Successfully pushed after merge!")
                return True
        else:
            # If pull failed due to no tracking branch, set upstream and try again
            if "no tracking information" in output.lower() or "couldn't find remote ref" in output.lower():
                self.console.print("[yellow]No remote branch found, creating new remote branch...[/yellow]")
                success, output = self.run_git_command(['git', 'push', '-u', 'origin', branch])
                if success:
                    self.console.print("[green]✓[/green] Successfully pushed new branch!")
                    return True
        
        # If pull failed, try force push with lease (safer than regular force push)
        self.console.print("[yellow]Trying force push with lease (safe overwrite)...[/yellow]")
        if Confirm.ask("[bold red]This will overwrite remote repository. Continue?[/bold red]"):
            success, output = self.run_git_command(['git', 'push', '--force-with-lease', 'origin', branch])
            if success:
                self.console.print("[green]✓[/green] Successfully force pushed!")
                return True
            else:
                # Try regular force push as last resort
                self.console.print("[yellow]Force with lease failed, trying regular force push...[/yellow]")
                if Confirm.ask("[bold red]This is more dangerous. Really continue?[/bold red]"):
                    success, output = self.run_git_command(['git', 'push', '--force', 'origin', branch])
                    if success:
                        self.console.print("[green]✓[/green] Successfully force pushed!")
                        return True
        
        self.console.print(f"[red]✗[/red] Could not resolve push conflicts: {output}")
        return False

    def push_to_github(self, branch: str = None) -> bool:
        """Push changes to GitHub"""
        # Auto-detect current branch if not specified
        if branch is None:
            branch = self.get_current_branch()
            
        self.console.print(f"[yellow]Pushing to GitHub ({branch} branch)...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Pushing to GitHub...", total=None)
            
            success, output = self.run_git_command(['git', 'push', '-u', 'origin', branch])
            
        if success:
            self.console.print("[green]✓[/green] Successfully pushed to GitHub!")
            return True
        else:
            # Handle common push errors with more detail
            if "remote: Repository not found" in output or "repository does not exist" in output.lower():
                self.console.print("[red]✗[/red] Repository not found. Make sure:")
                self.console.print("  1. The repository exists on GitHub")
                self.console.print("  2. You have access to the repository")
                self.console.print("  3. Your GitHub credentials are configured")
                self.console.print("  4. The repository URL is correct")
                return False
            elif "Permission denied" in output or "Authentication failed" in output or "access denied" in output.lower():
                self.console.print("[red]✗[/red] Permission denied. Please check your GitHub authentication:")
                self.console.print("  1. Generate a personal access token at: https://github.com/settings/tokens")
                self.console.print("  2. Use your GitHub username and token as password when prompted")
                self.console.print("  3. Or configure SSH keys for passwordless access")
                self.console.print("  4. Make sure you have write access to the repository")
                return False
            elif "support for password authentication was removed" in output.lower():
                self.console.print("[red]✗[/red] Password authentication is no longer supported. You need:")
                self.console.print("  1. A personal access token instead of your password")
                self.console.print("  2. Go to: https://github.com/settings/tokens")
                self.console.print("  3. Generate a token with 'repo' permissions")
                self.console.print("  4. Use token as password when Git asks for credentials")
                return False
            elif "failed to push some refs" in output or "non-fast-forward" in output or "Updates were rejected" in output or "rejected" in output.lower():
                # Try to handle push conflicts
                return self.handle_push_conflicts(branch)
            elif "couldn't find remote ref" in output.lower():
                self.console.print(f"[yellow]Remote branch '{branch}' doesn't exist, creating it...[/yellow]")
                return self.handle_push_conflicts(branch)
            else:
                self.console.print(f"[red]✗[/red] Push failed with error:")
                self.console.print(f"[red]{output}[/red]")
                # Ask if user wants to try conflict resolution anyway
                if Confirm.ask("Try to resolve this as a push conflict?"):
                    return self.handle_push_conflicts(branch)
                return False
    
    def run(self):
        """Main application loop"""
        self.display_header()
        
        try:
            while True:
                # Get repository URL
                repo_url = Prompt.ask("\n[bold]Enter GitHub repository URL (or 'quit' to exit)[/bold]")
                
                if repo_url.lower() == 'quit':
                    self.console.print("👋 Goodbye!")
                    break
                
                # Validate URL
                is_valid, parsed_url = self.validate_github_url(repo_url)
                if not is_valid:
                    self.console.print(f"[red]✗[/red] {parsed_url}")
                    continue
                
                self.console.print(f"[green]✓[/green] Repository URL: {parsed_url}")
                
                # Get files in directory
                files = self.get_files_in_directory()
                if not files:
                    continue
                
                # Let user select files
                selected_files = self.display_file_selection(files)
                if not selected_files:
                    continue
                
                # Get commit message
                commit_message = Prompt.ask(
                    "\n[bold]Enter commit message[/bold]",
                    default="Update files via Git Buddy"
                )
                
                # Confirm before proceeding
                self.console.print(f"\n[bold]Summary:[/bold]")
                self.console.print(f"Repository: {parsed_url}")
                self.console.print(f"Files to push: {len(selected_files)}")
                self.console.print(f"Commit message: {commit_message}")
                
                if not Confirm.ask("\nProceed with git operations?"):
                    continue
                
                # Execute git operations
                if not self.initialize_git_repo():
                    continue
                    
                if not self.add_files_to_git(selected_files):
                    continue
                    
                if not self.commit_changes(commit_message):
                    continue
                    
                if not self.add_remote_origin(parsed_url):
                    continue
                    
                if self.push_to_github():
                    self.console.print("\n[bold green]🎉 Success! Your files have been pushed to GitHub![/bold green]")
                
                # Ask if user wants to continue
                if not Confirm.ask("\nPush to another repository?"):
                    break
                    
        except KeyboardInterrupt:
            self.console.print("\n\n👋 Goodbye!")
        except Exception as e:
            self.console.print(f"\n[red]Unexpected error: {e}[/red]")


def main():
    """Entry point for the gitbuddy command"""
    app = GitBuddy()
    app.run()

if __name__ == "__main__":
    main()