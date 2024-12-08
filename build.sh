#!/bin/bash
set -e
uv venv
source .venv/bin/activate
uv sync
if [ ! -f cmd-helper.spec ]; then
    uvx pyi-makespec --name=cmd-helper src/shell.py
fi
uvx pyinstaller --clean cmd-helper.spec
echo "Build completed successfully!"