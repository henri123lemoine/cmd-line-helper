#!/bin/bash

# Exit on error
set -e

BINARY_NAME="cmd-helper"
INSTALL_DIR="/usr/local/bin"
REPO_URL="https://github.com/henri123lemoine/cmd-line-helper"
REPO_BRANCH="main"

print_usage() {
    echo "Command Line Helper Installation Script"
    echo
    echo "Usage: $0 [--local]"
    echo "Options:"
    echo "  --local    Build and install from source (default: install pre-built binary)"
    echo
}

ensure_uv_installed() {
    if ! command -v uv &> /dev/null; then
        echo "uv not found. Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Add uv to PATH for the current session
        export PATH="$HOME/.cargo/bin:$PATH"
        
        # Check if installation was successful
        if ! command -v uv &> /dev/null; then
            echo "Failed to install uv. Please install it manually from https://astral.sh/uv"
            exit 1
        fi
        echo "uv installed successfully!"
    else
        echo "uv is already installed"
    fi
}

install_from_release() {
    echo "Installing pre-built binary..."
    curl -L "${REPO_URL}/releases/download/${REPO_BRANCH}/${BINARY_NAME}" -o "${BINARY_NAME}"
    chmod +x "${BINARY_NAME}"
    sudo mv "${BINARY_NAME}" "${INSTALL_DIR}/${BINARY_NAME}"
    echo "${BINARY_NAME} installed successfully!"
    echo "Run '${BINARY_NAME}' to start."
}

build_from_source() {
    # Ensure uv is installed before proceeding
    ensure_uv_installed

    # Check if we're in the project directory by looking for src/shell.py
    if [ ! -f "src/shell.py" ]; then
        echo "Installing from source..."
        # Clone the repository if we're not in it
        temp_dir=$(mktemp -d)
        git clone "${REPO_URL}.git" "$temp_dir"
        cd "$temp_dir"
    fi

    # Create and activate virtual environment using uv
    echo "Creating virtual environment..."
    uv venv
    source .venv/bin/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    uv sync
    
    # Create PyInstaller spec file if it doesn't exist
    if [ ! -f ${BINARY_NAME}.spec ]; then
        echo "Creating PyInstaller spec file..."
        uvx pyi-makespec --name=${BINARY_NAME} src/shell.py
    fi
    
    # Build the binary
    echo "Building binary..."
    uvx pyinstaller --clean ${BINARY_NAME}.spec
    
    # Install the binary
    echo "Installing ${BINARY_NAME} to ${INSTALL_DIR}..."
    chmod +x "dist/${BINARY_NAME}"
    sudo mv "dist/${BINARY_NAME}" "${INSTALL_DIR}/${BINARY_NAME}"
    
    # Clean up if we created a temp directory
    if [ -n "$temp_dir" ]; then
        cd - > /dev/null
        rm -rf "$temp_dir"
    fi
    
    echo "${BINARY_NAME} installed successfully from source!"
    echo "Run '${BINARY_NAME}' to start."
}

main() {
    # Parse command line arguments
    if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        print_usage
        exit 0
    fi
    
    if [ "$1" == "--local" ]; then
        build_from_source
    else
        install_from_release
    fi
}

main "$@"