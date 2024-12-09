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
$ cmd-helper --trust
Welcome to the LLM Shell Helper! (trust mode activated)

What would you like to do? (or 'exit' to quit): commit the changes to shell.py

>>> git add shell.py

🔄 Attempting recovery with modified command...

>>> git add src/shell.py
✓ Success!

>>> git commit -m "Committing changes to shell.py"
✓ Success!
[main 06bb89e] Committing changes to shell.py
 1 file changed, 74 insertions(+), 14 deletions(-)

What would you like to do? (or 'exit' to quit): ```
