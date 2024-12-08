#!/bin/bash
curl -L https://github.com/yourusername/cmd-line-helper/releases/download/main/cmd-helper -o cmd-helper
chmod +x cmd-helper
sudo mv cmd-helper /usr/local/bin/cmd-helper
echo "Command Line Helper installed successfully! Run 'cmd-helper' to start."