#!/bin/bash

# Build the binary
./build.sh

# Make it executable
chmod +x dist/cmd-helper

# Move to a directory in PATH
sudo mv dist/cmd-helper /usr/local/bin/cmd-helper

echo "Command Line Helper installed successfully from local build!"