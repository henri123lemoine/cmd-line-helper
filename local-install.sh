#!/bin/bash
./build.sh
chmod +x dist/cmd-helper
sudo mv dist/cmd-helper /usr/local/bin/cmd-helper
echo "Command Line Helper installed successfully from local build!"