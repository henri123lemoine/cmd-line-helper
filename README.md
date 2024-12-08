# cmd_line_helper

My submission for Tyler's AI Control stream.

## Installation

```bash
pip install cmd_line_helper
```

## Usage

TODO

## Example

```bash
~/Documents/Programming/PersonalProjects/cmd_line_helper (main*) » uv run -m src.shell
Welcome to the LLM Shell Helper!
--------------------------------

What would you like to do? (or 'exit' to quit): commit file .env.example to git
2024-12-08 18:10:44,460 [INFO] httpx: HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

Suggested command: git add .env.example
Execute this command? (y/n): y
Success!

Suggested command: git commit -m "Add .env.example file"
Execute this command? (y/n): y   
Success!
[main 5a983f6] Add .env.example file
 1 file changed, 3 insertions(+)
 create mode 100644 .env.example


What would you like to do? (or 'exit' to quit): now, push
2024-12-08 18:11:02,061 [INFO] httpx: HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

Suggested command: git push
Execute this command? (y/n): y
Success!

What would you like to do? (or 'exit' to quit): exit
```
