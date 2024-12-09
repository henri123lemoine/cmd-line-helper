# Command Line Helper

An AI-powered command-line helper that suggests and executes shell commands.

## Quick Install

```bash
curl -L https://raw.githubusercontent.com/henri123lemoine/cmd-line-helper/main/install.sh | bash
```

## Development

Clone the repository and run the install script:
```bash
git clone https://github.com/henri123lemoine/cmd-line-helper.git`
cd cmd-line-helper
./install.sh --local
```

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
cmd-helper --trust
Welcome to the LLM Shell Helper! (trust mode activated)

What would you like to do? (or 'exit' to quit): hey

👋 Hello! How can I help you?

What would you like to do? (or 'exit' to quit): can you tlel me hwo to commit a ne wfile called bob.py

🔍 Gathering system information...

📊 Analyzing current state...

>>> touch bob.py
✓ Success!

>>> git add bob.py
✓ Success!

>>> git commit -m "Add bob.py"
✓ Success!
[main 8577392] Add bob.py
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 bob.py

📊 Analyzing current state...

✓ Task completed successfully!
```
