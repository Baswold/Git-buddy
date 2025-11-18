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
from typing import List, Optional, Tuple, Dict
from urllib.parse import urlparse
import json
import time
from datetime import datetime

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
        self.config_file = Path.home() / '.gitbuddy_config.json'
        self.config = self.load_config()
        self.operation_start_time = None
        
    def load_config(self) -> Dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
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

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save config: {e}[/yellow]")

    def add_recent_repo(self, repo_url: str):
        """Add repository to recent list"""
        if repo_url not in self.config["recent_repos"]:
            self.config["recent_repos"].insert(0, repo_url)
            self.config["recent_repos"] = self.config["recent_repos"][:5]  # Keep only last 5
            self.save_config()

    def display_header(self):
        """Display the application header"""
        header = Panel(
            Text("🚀 Git Buddy - Terminal Git Helper v2.0", style="bold blue"),
            subtitle="Push your files to GitHub with ease | Type 'help' for commands"
        )
        self.console.print(header)

    def display_help(self):
        """Display help information"""
        help_text = """
[bold cyan]Git Buddy Help[/bold cyan]

[bold]Features:[/bold]
• Smart commit message suggestions based on file changes
• Automatic detection of sensitive files (.env, credentials, etc.)
• Large file warnings (>10MB by default)
• Recent repository quick selection
• Interactive branch management
• .gitignore suggestions
• Retry logic for network failures
• Detailed operation statistics

[bold]Tips:[/bold]
• Use numbers to quickly select recent repositories
• Smart commit messages are generated based on your changes
• The tool warns you about potentially sensitive files before pushing
• Network failures are automatically retried with exponential backoff
• Configuration is saved in ~/.gitbuddy_config.json

[bold]URL Formats Supported:[/bold]
• https://github.com/username/repo
• git@github.com:username/repo.git
• username/repo

[bold]Keyboard Shortcuts:[/bold]
• Type 'quit' or 'q' to exit
• Type 'help' or '?' for this help message
• Ctrl+C to cancel at any time
"""
        self.console.print(Panel(help_text, title="Help", border_style="cyan"))

    def suggest_commit_message(self, modified_files: List[str], new_files: List[str], deleted_files: List[str]) -> str:
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

        # Create suggestions based on patterns
        suggestions = []

        # Pattern 1: Specific file count
        if total_changes == 1:
            file = all_files[0]
            if file in new_files:
                suggestions.append(f"Add {file}")
            elif file in modified_files:
                suggestions.append(f"Update {file}")
            else:
                suggestions.append(f"Remove {file}")

        # Pattern 2: File type specific
        if file_types:
            dominant_type = max(file_types, key=file_types.get)
            type_names = {
                '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                '.java': 'Java', '.cpp': 'C++', '.c': 'C',
                '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS',
                '.md': 'documentation', '.txt': 'text files',
                '.json': 'configuration', '.yaml': 'configuration', '.yml': 'configuration',
                '.sh': 'scripts', '.bat': 'scripts'
            }

            type_name = type_names.get(dominant_type, f"{dominant_type[1:]} files")
            suggestions.append(f"{action} {type_name}")

        # Pattern 3: Generic
        suggestions.append(f"{action} {total_changes} file{'s' if total_changes > 1 else ''}")

        # Pattern 4: Detailed
        parts = []
        if new_files:
            parts.append(f"{len(new_files)} new")
        if modified_files:
            parts.append(f"{len(modified_files)} modified")
        if deleted_files:
            parts.append(f"{len(deleted_files)} deleted")

        if parts:
            suggestions.append(f"Update files: {', '.join(parts)}")

        # Pattern 5: Check for common patterns
        if any('test' in f.lower() for f in all_files):
            suggestions.append(f"{action} tests")
        if any('readme' in f.lower() for f in all_files):
            suggestions.append(f"{action} documentation")
        if any('.gitignore' in f for f in all_files):
            suggestions.append("Update .gitignore")

        return suggestions[0] if suggestions else "Update files via Git Buddy"

    def check_file_sizes(self, files: List[Path]) -> Tuple[List[Path], List[Tuple[Path, float]]]:
        """Check for large files and return warnings"""
        large_files = []
        warning_threshold = self.config.get("file_size_warning_mb", 10) * 1024 * 1024  # Convert to bytes

        for file_path in files:
            try:
                size = file_path.stat().st_size
                if size > warning_threshold:
                    size_mb = size / (1024 * 1024)
                    large_files.append((file_path, size_mb))
            except Exception:
                pass

        return [f for f, _ in large_files], large_files

    def check_sensitive_files(self, files: List[Path]) -> List[Tuple[Path, str]]:
        """Detect potentially sensitive files"""
        sensitive_patterns = {
            r'\.env$': 'Environment variables file',
            r'\.env\..*': 'Environment configuration',
            r'credentials?\.json$': 'Credentials file',
            r'secrets?\.ya?ml$': 'Secrets configuration',
            r'\.aws/': 'AWS credentials',
            r'\.ssh/': 'SSH keys',
            r'id_rsa': 'SSH private key',
            r'\.pem$': 'Private key file',
            r'password': 'Password file',
            r'token': 'Token file',
            r'\.key$': 'Key file',
            r'config\.inc\.php$': 'PHP config with potential credentials',
            r'wp-config\.php$': 'WordPress config with credentials'
        }

        sensitive_files = []
        for file_path in files:
            file_str = str(file_path)
            for pattern, description in sensitive_patterns.items():
                if re.search(pattern, file_str, re.IGNORECASE):
                    sensitive_files.append((file_path, description))
                    break

        return sensitive_files

    def display_file_warnings(self, files: List[Path]) -> bool:
        """Display warnings for files and ask for confirmation"""
        large_files_paths, large_files_info = self.check_file_sizes(files)
        sensitive_files = self.check_sensitive_files(files)

        has_warnings = bool(large_files_info or sensitive_files)

        if not has_warnings:
            return True

        self.console.print("\n[bold yellow]⚠ File Warnings:[/bold yellow]")

        if large_files_info:
            self.console.print("\n[bold]Large Files Detected:[/bold]")
            for file_path, size_mb in large_files_info:
                relative_path = file_path.relative_to(self.current_dir)
                self.console.print(f"  [yellow]•[/yellow] {relative_path}: {size_mb:.2f} MB")
            self.console.print("[dim]Large files can slow down repository operations[/dim]")

        if sensitive_files:
            self.console.print("\n[bold red]Potentially Sensitive Files Detected:[/bold red]")
            for file_path, description in sensitive_files:
                relative_path = file_path.relative_to(self.current_dir)
                self.console.print(f"  [red]⚠[/red] {relative_path}: {description}")
            self.console.print("[dim]These files may contain credentials or sensitive data[/dim]")

        return Confirm.ask("\n[bold]Do you want to proceed anyway?[/bold]", default=False)

    def suggest_gitignore_entries(self, files: List[Path]) -> List[str]:
        """Suggest .gitignore entries based on detected files"""
        suggestions = set()

        # Common patterns to ignore
        patterns_map = {
            '.pyc': ['*.pyc', '__pycache__/', '*.pyo', '*.pyd'],
            '.egg-info': ['*.egg-info/', 'dist/', 'build/'],
            'node_modules': ['node_modules/', 'npm-debug.log*', 'yarn-error.log*'],
            '.env': ['.env', '.env.local', '.env.*.local'],
            '.log': ['*.log', 'logs/'],
            '.DS_Store': ['.DS_Store', '.AppleDouble', '.LSOverride'],
            '.idea': ['.idea/', '*.iml'],
            '.vscode': ['.vscode/'],
            'target': ['target/', '*.class'],  # Java
            'bin': ['bin/', 'obj/'],  # C#/.NET
        }

        for file_path in files:
            file_str = str(file_path)
            for pattern, ignore_entries in patterns_map.items():
                if pattern in file_str.lower():
                    suggestions.update(ignore_entries)

        return sorted(suggestions)

    def manage_gitignore(self, files: List[Path]):
        """Interactive .gitignore management"""
        gitignore_path = self.current_dir / '.gitignore'
        suggestions = self.suggest_gitignore_entries(files)

        if not suggestions:
            return

        self.console.print("\n[bold cyan]💡 .gitignore Suggestions[/bold cyan]")
        self.console.print("Based on your files, consider adding these to .gitignore:")

        for suggestion in suggestions:
            self.console.print(f"  [yellow]•[/yellow] {suggestion}")

        if Confirm.ask("\n[bold]Would you like to add these to .gitignore?[/bold]", default=False):
            existing_entries = set()
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    existing_entries = {line.strip() for line in f if line.strip() and not line.startswith('#')}

            new_entries = [s for s in suggestions if s not in existing_entries]

            if new_entries:
                with open(gitignore_path, 'a') as f:
                    f.write('\n# Added by Git Buddy\n')
                    for entry in new_entries:
                        f.write(f'{entry}\n')

                self.console.print(f"[green]✓[/green] Added {len(new_entries)} entries to .gitignore")
            else:
                self.console.print("[yellow]All suggestions already in .gitignore[/yellow]")

    def get_available_branches(self) -> List[str]:
        """Get list of all branches"""
        success, output = self.run_git_command(['git', 'branch', '-a'])
        if not success or not output.strip():
            return []

        branches = []
        for line in output.strip().split('\n'):
            # Remove leading markers and whitespace
            branch = line.strip().lstrip('*').strip()
            # Skip remote tracking info
            if 'remotes/origin/' in branch:
                branch = branch.replace('remotes/origin/', '')
            # Skip HEAD references
            if '->' not in branch and branch and branch not in branches:
                branches.append(branch)

        return branches

    def suggest_branch_name(self, modified_files: List[str], new_files: List[str]) -> str:
        """Suggest a branch name based on changes"""
        all_files = modified_files + new_files

        # Check for common patterns
        if any('feature' in f.lower() for f in all_files):
            return "feature/new-feature"
        if any('fix' in f.lower() or 'bug' in f.lower() for f in all_files):
            return "bugfix/fix-issue"
        if any('test' in f.lower() for f in all_files):
            return "test/add-tests"
        if any('doc' in f.lower() or 'readme' in f.lower() for f in all_files):
            return "docs/update-documentation"

        return "feature/updates"

    def interactive_branch_management(self):
        """Interactive branch selection and creation"""
        current_branch = self.get_current_branch()
        available_branches = self.get_available_branches()

        self.console.print(f"\n[bold]Current Branch:[/bold] [green]{current_branch}[/green]")

        if available_branches:
            self.console.print("\n[bold]Available Branches:[/bold]")
            for branch in available_branches[:10]:  # Show max 10
                marker = "→" if branch == current_branch else " "
                self.console.print(f"  {marker} {branch}")

        if Confirm.ask("\n[bold]Switch or create a new branch?[/bold]", default=False):
            choice = Prompt.ask(
                "Enter branch name to switch to, or 'new' to create a new branch",
                default=current_branch
            )

            if choice.lower() == 'new':
                modified_files, new_files, _ = self.get_git_status()
                suggested_name = self.suggest_branch_name(modified_files, new_files)
                new_branch = Prompt.ask("Enter new branch name", default=suggested_name)

                success, output = self.run_git_command(['git', 'checkout', '-b', new_branch])
                if success:
                    self.console.print(f"[green]✓[/green] Created and switched to branch '{new_branch}'")
                else:
                    self.console.print(f"[red]✗[/red] Failed to create branch: {output}")
            elif choice != current_branch:
                success, output = self.run_git_command(['git', 'checkout', choice])
                if success:
                    self.console.print(f"[green]✓[/green] Switched to branch '{choice}'")
                else:
                    self.console.print(f"[red]✗[/red] Failed to switch branch: {output}")

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
    
    def get_git_status(self) -> Tuple[List[str], List[str], List[str]]:
        """Get git status and return lists of modified, new, and deleted files"""
        success, output = self.run_git_command(['git', 'status', '--porcelain'])
        
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
                    # Handle staged and unstaged changes
                    if file_path not in modified_files and file_path not in new_files:
                        if status_code[0] == '?' or status_code[1] == '?':
                            new_files.append(file_path)
                        else:
                            modified_files.append(file_path)
        
        return modified_files, new_files, deleted_files

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
    
    def get_changed_files_as_paths(self) -> List[Path]:
        """Get only changed/new files as Path objects"""
        modified_files, new_files, deleted_files = self.get_git_status()
        all_changed = modified_files + new_files
        
        changed_paths = []
        for file_path in all_changed:
            full_path = self.current_dir / file_path
            if full_path.exists():
                changed_paths.append(full_path)
        
        return sorted(changed_paths)
    
    def show_file_diff(self, file_path: str):
        """Show diff for a specific file"""
        self.console.print(f"\n[bold]Diff for {file_path}:[/bold]")
        
        # Check if file is new (untracked)
        success, status_output = self.run_git_command(['git', 'status', '--porcelain', file_path])
        if success and status_output.startswith('??'):
            self.console.print("[green]This is a new file (showing first 20 lines):[/green]")
            try:
                with open(self.current_dir / file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:20]
                    for i, line in enumerate(lines, 1):
                        self.console.print(f"[green]+{i:3d}[/green] {line.rstrip()}")
                    if len(lines) == 20:
                        self.console.print("[dim]... (truncated)[/dim]")
            except Exception as e:
                self.console.print(f"[red]Could not read file: {e}[/red]")
        else:
            # Show actual diff for modified files
            success, diff_output = self.run_git_command(['git', 'diff', 'HEAD', '--', file_path])
            if success and diff_output.strip():
                # Parse and colorize diff output
                lines = diff_output.split('\n')
                for line in lines:
                    if line.startswith('+++') or line.startswith('---'):
                        self.console.print(f"[bold]{line}[/bold]")
                    elif line.startswith('+'):
                        self.console.print(f"[green]{line}[/green]")
                    elif line.startswith('-'):
                        self.console.print(f"[red]{line}[/red]")
                    elif line.startswith('@@'):
                        self.console.print(f"[cyan]{line}[/cyan]")
                    else:
                        self.console.print(line)
            else:
                self.console.print("[yellow]No differences found or file is staged[/yellow]")

    def display_git_status(self):
        """Display current git status with colors"""
        modified_files, new_files, deleted_files = self.get_git_status()
        
        if not any([modified_files, new_files, deleted_files]):
            self.console.print("[green]✓[/green] Working directory clean - no changes detected")
            return
        
        self.console.print("\n[bold]Git Status:[/bold]")
        
        if new_files:
            self.console.print(f"\n[bold green]New files ({len(new_files)}):[/bold green]")
            for file in new_files:
                self.console.print(f"  [green]+[/green] {file}")
        
        if modified_files:
            self.console.print(f"\n[bold yellow]Modified files ({len(modified_files)}):[/bold yellow]")
            for file in modified_files:
                self.console.print(f"  [yellow]M[/yellow] {file}")
        
        if deleted_files:
            self.console.print(f"\n[bold red]Deleted files ({len(deleted_files)}):[/bold red]")
            for file in deleted_files:
                self.console.print(f"  [red]-[/red] {file}")
        
        # Offer to show diffs
        if modified_files or new_files:
            if Confirm.ask("\n[bold]Would you like to see what changed in any files?[/bold]"):
                all_changed = modified_files + new_files
                for i, file in enumerate(all_changed, 1):
                    self.console.print(f"\n[bold]{i}. {file}[/bold]")
                
                while True:
                    choice = Prompt.ask(
                        "Enter file number to view diff (or 'done' to continue)",
                        default="done"
                    )
                    
                    if choice.lower() == 'done':
                        break
                        
                    try:
                        file_index = int(choice) - 1
                        if 0 <= file_index < len(all_changed):
                            self.show_file_diff(all_changed[file_index])
                        else:
                            self.console.print("[red]Invalid file number[/red]")
                    except ValueError:
                        self.console.print("[red]Please enter a number or 'done'[/red]")

    def display_file_selection(self, files: List[Path]) -> List[Path]:
        """Display files and let user select which ones to push"""
        if not files:
            self.console.print("[red]No files found in the current directory[/red]")
            return []
        
        # Check if this is a git repository and show status
        git_dir = self.current_dir / '.git'
        if git_dir.exists():
            self.display_git_status()
            
            # Get changed files
            changed_files = self.get_changed_files_as_paths()
            
            if changed_files:
                self.console.print("\n[bold]File Selection Options:[/bold]")
                choice = Prompt.ask(
                    "What would you like to push?",
                    choices=["changed", "all", "select", "quit"],
                    default="changed"
                )
                
                if choice == "quit":
                    return []
                elif choice == "changed":
                    self.console.print(f"\n[green]Selected {len(changed_files)} changed file(s)[/green]")
                    return changed_files
                elif choice == "all":
                    files = files
                else:  # select
                    return self.select_specific_files(files)
            else:
                self.console.print("\n[yellow]No changes detected, showing all files[/yellow]")
        
        self.console.print("\n[bold]All files in directory:[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Index", style="dim", width=6)
        table.add_column("File Path", style="cyan")
        table.add_column("Size", style="green", width=10)
        table.add_column("Status", style="yellow", width=8)
        
        # Get git status for file marking
        modified_files, new_files, deleted_files = self.get_git_status()
        all_changed = set(modified_files + new_files)
        
        for i, file_path in enumerate(files, 1):
            try:
                size = file_path.stat().st_size
                size_str = self.format_file_size(size)
            except:
                size_str = "N/A"
            
            relative_path = str(file_path.relative_to(self.current_dir))
            status = "NEW" if relative_path in new_files else "MODIFIED" if relative_path in modified_files else "UNCHANGED"
            
            table.add_row(str(i), relative_path, size_str, status)
            
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
    
    def run_git_command(self, command: List[str], cwd: Path = None, retry_count: int = 0) -> Tuple[bool, str]:
        """Execute git command and return success status and output with retry logic"""
        if cwd is None:
            cwd = self.current_dir

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

                # If successful, return immediately
                if result.returncode == 0:
                    return True, result.stdout + result.stderr

                # If it's a network error and we have retries left, retry with backoff
                output = result.stdout + result.stderr
                is_network_error = any(err in output.lower() for err in
                    ['network', 'connection', 'timeout', 'ssl', 'tls', 'unable to access'])

                if is_network_error and attempt < max_retries:
                    backoff_time = 2 ** attempt  # Exponential backoff: 2s, 4s, 8s, 16s
                    self.console.print(f"[yellow]Network error detected, retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries})[/yellow]")
                    time.sleep(backoff_time)
                    attempt += 1
                    continue

                # Not a network error or no retries left
                return False, output

            except subprocess.TimeoutExpired:
                if attempt < max_retries:
                    backoff_time = 2 ** attempt
                    self.console.print(f"[yellow]Command timed out, retrying in {backoff_time}s... (attempt {attempt + 1}/{max_retries})[/yellow]")
                    time.sleep(backoff_time)
                    attempt += 1
                    continue
                return False, "Command timed out after 30 seconds"
            except Exception as e:
                return False, str(e)

        return False, "Max retries exceeded"

    def view_commit_history(self, limit: int = 10):
        """Display recent commit history"""
        success, output = self.run_git_command(['git', 'log', f'-{limit}', '--oneline', '--decorate', '--graph'])

        if success and output.strip():
            self.console.print("\n[bold]Recent Commits:[/bold]")
            for line in output.strip().split('\n'):
                # Colorize the output
                if '*' in line:
                    self.console.print(f"[cyan]{line}[/cyan]")
                else:
                    self.console.print(line)
        else:
            self.console.print("[yellow]No commit history available[/yellow]")

    def get_repository_stats(self) -> Dict:
        """Get repository statistics"""
        stats = {}

        # Get total commits
        success, output = self.run_git_command(['git', 'rev-list', '--count', 'HEAD'])
        stats['total_commits'] = int(output.strip()) if success and output.strip() else 0

        # Get branch count
        success, output = self.run_git_command(['git', 'branch', '-a'])
        stats['branches'] = len(output.strip().split('\n')) if success and output.strip() else 0

        # Get contributors
        success, output = self.run_git_command(['git', 'shortlog', '-sn', '--all'])
        stats['contributors'] = len(output.strip().split('\n')) if success and output.strip() else 0

        return stats

    def display_operation_summary(self, operation_time: float, files_count: int):
        """Display summary of the operation"""
        if not self.config.get("show_stats", True):
            return

        stats = self.get_repository_stats()

        self.console.print("\n" + "=" * 60)
        self.console.print("[bold cyan]📊 Operation Summary[/bold cyan]")
        self.console.print("=" * 60)

        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Files pushed", str(files_count))
        summary_table.add_row("Operation time", f"{operation_time:.2f}s")
        summary_table.add_row("Total commits", str(stats.get('total_commits', 'N/A')))
        summary_table.add_row("Branches", str(stats.get('branches', 'N/A')))
        summary_table.add_row("Contributors", str(stats.get('contributors', 'N/A')))

        self.console.print(summary_table)
        self.console.print("=" * 60)
    
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
        """Push changes to GitHub with retry logic"""
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

            # Use retry logic for push operations (4 retries with exponential backoff)
            success, output = self.run_git_command(['git', 'push', '-u', 'origin', branch], retry_count=4)
            
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
        """Main application loop with enhanced features"""
        self.display_header()

        try:
            while True:
                # Start timing the operation
                self.operation_start_time = time.time()

                # Show recent repos if available
                if self.config["recent_repos"]:
                    self.console.print("\n[bold]Recent Repositories:[/bold]")
                    for i, repo in enumerate(self.config["recent_repos"][:5], 1):
                        self.console.print(f"  {i}. {repo}")

                # Get repository URL
                repo_url = Prompt.ask("\n[bold]Enter GitHub repository URL (number for recent, 'help', or 'quit')[/bold]")

                if repo_url.lower() in ['quit', 'q', 'exit']:
                    self.console.print("👋 Goodbye!")
                    break

                if repo_url.lower() in ['help', '?']:
                    self.display_help()
                    continue

                # Check if user selected a recent repo
                if repo_url.isdigit() and self.config["recent_repos"]:
                    repo_index = int(repo_url) - 1
                    if 0 <= repo_index < len(self.config["recent_repos"]):
                        repo_url = self.config["recent_repos"][repo_index]
                        self.console.print(f"[green]✓[/green] Selected: {repo_url}")

                # Validate URL
                is_valid, parsed_url = self.validate_github_url(repo_url)
                if not is_valid:
                    self.console.print(f"[red]✗[/red] {parsed_url}")
                    continue

                self.console.print(f"[green]✓[/green] Repository URL: {parsed_url}")

                # Add to recent repos
                self.add_recent_repo(parsed_url)

                # Check if user wants to view commit history
                git_dir = self.current_dir / '.git'
                if git_dir.exists():
                    if Confirm.ask("\n[bold]View recent commit history?[/bold]", default=False):
                        self.view_commit_history()

                    # Offer branch management
                    self.interactive_branch_management()

                # Get files in directory
                files = self.get_files_in_directory()
                if not files:
                    continue

                # Suggest .gitignore entries
                if git_dir.exists():
                    self.manage_gitignore(files)

                # Let user select files (this now includes smart change detection)
                selected_files = self.display_file_selection(files)
                if not selected_files:
                    continue

                # Check for file warnings (large files, sensitive files)
                if not self.display_file_warnings(selected_files):
                    self.console.print("[yellow]Operation cancelled by user[/yellow]")
                    continue

                # Get git status for smart commit message
                modified_files, new_files, deleted_files = self.get_git_status()

                # Generate smart commit message suggestion
                suggested_message = self.suggest_commit_message(modified_files, new_files, deleted_files)

                # Get commit message with smart suggestion
                commit_message = Prompt.ask(
                    "\n[bold]Enter commit message[/bold]",
                    default=suggested_message
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

                    # Display operation summary
                    operation_time = time.time() - self.operation_start_time
                    self.display_operation_summary(operation_time, len(selected_files))

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