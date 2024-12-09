#!/bin/bash

# Exit on error
set -e

INSTALL_DIR="/usr/local/bin"
REPO_URL="https://github.com/henri123lemoine/cmd-line-helper"
INSTALL_PATH="$HOME/.local/share/cmd-helper"

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

install_package() {
    echo "Installing cmd-helper..."
    
    # Create installation directory
    mkdir -p "$INSTALL_PATH"
    
    # Clone repository
    git clone "$REPO_URL" "$INSTALL_PATH"
    cd "$INSTALL_PATH"
    
    # Create virtual environment and install dependencies
    uv venv
    source .venv/bin/activate
    uv sync
}

main() {
    # Ensure uv is installed
    ensure_uv_installed

    # Install the package
    install_package

    # Create a shell script in /usr/local/bin
    echo "Creating cmd-helper launcher..."
    cat > /tmp/cmd-helper << EOF
#!/bin/bash
cd "$INSTALL_PATH"
source .venv/bin/activate
python -m src.shell "\$@"
EOF

    # Make it executable and move it to /usr/local/bin
    chmod +x /tmp/cmd-helper
    sudo mv /tmp/cmd-helper "$INSTALL_DIR/cmd-helper"

    echo "cmd-helper installed successfully!"
    echo "Run 'cmd-helper' to start."
}

main "$@"