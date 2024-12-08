# Command Line Helper

An AI-powered command-line helper that suggests and executes shell commands.

## Quick Install

```bash
curl -L https://raw.githubusercontent.com/yourusername/cmd-line-helper/main/install.sh | bash
```

This repository runs with `uv`.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/henri123lemoine/cmd-line-helper.git
    cd cmd-line-helper
    ```

2. Install dependencies:
    ```bash
    uv sync
    ```

3. Run the local installation script:
    ```bash
    chmod +x ./local-install.sh
    ./local-install.sh
    ```

## Usage

1. Set your OpenAI API key:
    ```bash
    export OPENAI_API_KEY=your-key-here
    ```

2. Run the helper:
    ```bash
    cmd-helper
    ```

Or with trust mode (no command confirmations):
```bash
cmd-helper --trust
```

## Examples

```bash
$ cmd-helper
Welcome to the LLM Shell Helper!

What would you like to do? (or 'exit' to quit): commit my recent changes

>>> git add .
✓ Success!
>>> git commit -m "Update command helper implementation"
✓ Success!
[main a1b2c3d] Update command helper implementation
 3 files changed, 45 insertions(+), 12 deletions(-)
```