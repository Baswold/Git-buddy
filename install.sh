#!/bin/bash
# Git Buddy - One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/yourusername/git-buddy/main/install.sh | bash

set -e

INSTALL_DIR="/usr/local/bin"
SCRIPT_NAME="gitbuddy"
REPO_URL="https://raw.githubusercontent.com/Baswold/Git-buddy/main/gitbuddy_standalone.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    case $1 in
        "success") echo -e "${GREEN}✓${NC} $2" ;;
        "error") echo -e "${RED}✗${NC} $2" ;;
        "warning") echo -e "${YELLOW}⚠${NC} $2" ;;
        "info") echo -e "${BLUE}ℹ${NC} $2" ;;
    esac
}

print_header() {
    echo "=================================="
    echo -e "${BLUE}🚀 Git Buddy Installer${NC}"
    echo "=================================="
}

check_requirements() {
    print_status "info" "Checking requirements..."
    
    # Check if Python 3 is installed
    if ! command -v python3 &> /dev/null; then
        print_status "error" "Python 3 is required but not installed."
        echo "Please install Python 3 first:"
        echo "  macOS: brew install python3"
        echo "  Ubuntu/Debian: sudo apt install python3"
        echo "  CentOS/RHEL: sudo yum install python3"
        exit 1
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_status "error" "Git is required but not installed."
        echo "Please install Git first:"
        echo "  macOS: brew install git"
        echo "  Ubuntu/Debian: sudo apt install git"
        echo "  CentOS/RHEL: sudo yum install git"
        exit 1
    fi
    
    print_status "success" "Requirements satisfied"
}

install_gitbuddy() {
    print_status "info" "Installing Git Buddy..."
    
    # Create temporary file
    TEMP_FILE=$(mktemp)
    
    # Download the standalone script
    if command -v curl &> /dev/null; then
        if curl -sSL "$REPO_URL" -o "$TEMP_FILE"; then
            print_status "success" "Downloaded Git Buddy"
        else
            print_status "error" "Failed to download Git Buddy"
            print_status "info" "You can manually download from: $REPO_URL"
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        if wget -q "$REPO_URL" -O "$TEMP_FILE"; then
            print_status "success" "Downloaded Git Buddy"
        else
            print_status "error" "Failed to download Git Buddy"
            print_status "info" "You can manually download from: $REPO_URL"
            exit 1
        fi
    else
        print_status "error" "Neither curl nor wget found. Cannot download Git Buddy."
        print_status "info" "Please install curl or wget, or manually download from: $REPO_URL"
        exit 1
    fi
    
    # Make it executable
    chmod +x "$TEMP_FILE"
    
    # Check if we can write to /usr/local/bin
    if [ -w "$INSTALL_DIR" ]; then
        mv "$TEMP_FILE" "$INSTALL_DIR/$SCRIPT_NAME"
        print_status "success" "Installed Git Buddy to $INSTALL_DIR/$SCRIPT_NAME"
    else
        # Try with sudo
        print_status "warning" "Need sudo permissions to install to $INSTALL_DIR"
        if sudo mv "$TEMP_FILE" "$INSTALL_DIR/$SCRIPT_NAME"; then
            print_status "success" "Installed Git Buddy to $INSTALL_DIR/$SCRIPT_NAME"
        else
            print_status "error" "Failed to install to $INSTALL_DIR"
            print_status "info" "You can manually copy the file to a directory in your PATH"
            exit 1
        fi
    fi
}

verify_installation() {
    print_status "info" "Verifying installation..."
    
    if command -v gitbuddy &> /dev/null; then
        print_status "success" "Git Buddy installed successfully!"
        echo ""
        echo -e "${GREEN}🎉 Installation complete!${NC}"
        echo ""
        echo "Usage:"
        echo "  cd /path/to/your/project"
        echo "  gitbuddy"
        echo ""
        echo "Features:"
        echo "  • Smart change detection"
        echo "  • Push only modified files"
        echo "  • Automatic conflict resolution"
        echo "  • No dependencies required!"
    else
        print_status "error" "Installation verification failed"
        print_status "info" "Make sure $INSTALL_DIR is in your PATH"
        exit 1
    fi
}

# Main installation process
main() {
    print_header
    check_requirements
    install_gitbuddy
    verify_installation
}

# Run if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi