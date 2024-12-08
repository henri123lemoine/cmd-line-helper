#!/bin/bash

# Download the latest release
curl -L https://github.com/yourusername/cmd-line-helper/releases/download/main/cmd-helper -o cmd-helper

# Make it executable
chmod +x cmd-helper

# Move to a directory in PATH
sudo mv cmd-helper /usr/local/bin/cmd-helper

echo "Command Line Helper installed successfully! Run 'cmd-helper' to start."