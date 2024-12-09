#!/bin/bash

# Exit on error
set -e

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

main() {
    # Ensure uv is installed
    ensure_uv_installed

    # Create a shell script in /usr/local/bin
    echo "Creating cmd-helper launcher..."
    cat > /tmp/cmd-helper << 'EOF'
#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvx python -m src.shell "$@"
EOF

    # Make it executable and move it to /usr/local/bin
    chmod +x /tmp/cmd-helper
    sudo mv /tmp/cmd-helper /usr/local/bin/cmd-helper

    echo "cmd-helper installed successfully!"
    echo "Run 'cmd-helper' to start."
}

main "$@"