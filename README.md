# Command Line Helper

An AI-powered command-line helper that suggests and executes shell commands.

## Quick Install

```bash
curl -L https://raw.githubusercontent.com/henri123lemoine/cmd-line-helper/main/install.sh | bash
```

## Development

Clone the repository at `git clone https://github.com/henri123lemoine/cmd-line-helper.git`.

## Usage

1. Set your OpenAI API key:
    ```bash
    export OPENAI_API_KEY=your-key-here
    ```

2. Run `./install.sh` to install the helper.

3. Run the helper:
    ```bash
    cmd-helper [--trust] [--debug]
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
