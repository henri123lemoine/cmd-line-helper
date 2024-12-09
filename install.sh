#!/bin/bash

# Exit on error and print commands as they execute
set -ex

INSTALL_DIR="/usr/local/bin"
REPO_URL="https://github.com/henri123lemoine/cmd-line-helper"
INSTALL_PATH="$HOME/.local/share/cmd-helper"

ensure_uv_installed() {
    if ! command -v uv &> /dev/null; then
        echo "uv not found. Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
        
        if ! command -v uv &> /dev/null; then
            echo "Failed to install uv"
            exit 1
        fi
        echo "uv installed successfully!"
    else
        echo "uv is already installed"
    fi
}

install_package() {
    echo "Installing cmd-helper..."
    
    # Remove existing installation if it exists
    rm -rf "$INSTALL_PATH"
    
    # Create fresh installation directory
    mkdir -p "$INSTALL_PATH"
    
    echo "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_PATH"
    cd "$INSTALL_PATH"
    
    echo "Setting up virtual environment..."
    uv venv
    source .venv/bin/activate
    
    echo "Installing dependencies..."
    uv sync
}

create_launcher() {
    echo "Creating cmd-helper launcher..."
    cat > /tmp/cmd-helper << EOF
#!/bin/bash
cd "$INSTALL_PATH"
source .venv/bin/activate
python -m src.shell "\$@"
EOF

    chmod +x /tmp/cmd-helper
    sudo mv /tmp/cmd-helper "$INSTALL_DIR/cmd-helper"
}

main() {
    echo "Starting installation..."
    ensure_uv_installed
    install_package
    create_launcher
    echo "cmd-helper installed successfully!"
    echo "Run 'cmd-helper' to start."
}

main "$@"