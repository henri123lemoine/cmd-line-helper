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

### No Debug

```bash
~/Documents/Programming/PersonalProjects/cmd_line_helper (main*) » cmd
-helper --trust
Welcome to the LLM Shell Helper! (trust mode activated)

What would you like to do? (or 'exit' to quit): hi

👋 Hello! How can I help you?

What would you like to do? (or 'exit' to quit): add changes to install.sh to githb

🔍 Gathering system information...

📊 Analyzing current state...

>>> git add install.sh
✓ Success!

>>> git commit -m "Update install.sh with relevant changes"
✓ Success!
[main e001043] Update install.sh with relevant changes
 1 file changed, 14 insertions(+), 78 deletions(-)

>>> git push origin main
✓ Success!

📊 Analyzing current state...

✓ Task completed successfully!
```

### Debug

```bash
~/Documents/Programming/PersonalProjects/cmd_line_helper (main*) » cmd-helper --trust --debug
2024-12-08 19:46:56.238 | INFO     | src.shell:run_interactive:281 - Welcome to the LLM Shell Helper! (trust mode activated)

What would you like to do? (or 'exit' to quit): add file src/bob.py 
2024-12-08 19:47:03.768 | INFO     | src.shell:gather_information:195 - 
🔍 Gathering system information...
2024-12-08 19:47:04.273 | DEBUG    | src.shell:gather_information:206 - Gathering info: pwd  
2024-12-08 19:47:04.273 | DEBUG    | src.shell:execute_command:179 - Executing command: pwd  
2024-12-08 19:47:04.289 | DEBUG    | src.shell:gather_information:206 - Gathering info: ls src  
2024-12-08 19:47:04.289 | DEBUG    | src.shell:execute_command:179 - Executing command: ls src  
2024-12-08 19:47:04.296 | DEBUG    | src.shell:gather_information:206 - Gathering info: ls src/__pycache__  
2024-12-08 19:47:04.296 | DEBUG    | src.shell:execute_command:179 - Executing command: ls src/__pycache__  
2024-12-08 19:47:04.301 | DEBUG    | src.shell:gather_information:206 - Gathering info: git status  
2024-12-08 19:47:04.301 | DEBUG    | src.shell:execute_command:179 - Executing command: git status  
2024-12-08 19:47:04.314 | DEBUG    | src.shell:gather_information:206 - Gathering info: git branch  
2024-12-08 19:47:04.314 | DEBUG    | src.shell:execute_command:179 - Executing command: git branch  
2024-12-08 19:47:04.324 | INFO     | src.shell:process_task:228 - 
📊 Analyzing current state...
2024-12-08 19:47:06.030 | DEBUG    | src.shell:process_task:235 - 
Analysis:
### Analysis:
1. **Actions to be Taken**:
   - The file `src/bob.py` needs to be added to the `src/` directory.
   - Confirm if the desired file exists already. It is not present based on the directory listing of `src/`.
   - Create the file `src/bob.py` using a file creation command (e.g., `touch src/bob.py` or with a text editor).
   - Once created, add the file to git using `git add src/bob.py`.

2. **Potential Issues or Risks**:
   - Ensure that the file is created in the correct directory (`src/`).
   - Unstaged changes to `src/shell.py` should not be accidentally committed unless intended. Address this separately.

3. **Task Completion**:
   - The task is **not yet complete** as the file `src/bob.py` is missing. Create the file and add it to the repository to accomplish this task.
2024-12-08 19:47:06.456 | INFO     | src.shell:process_task:261 - 
>>> touch src/bob.py
2024-12-08 19:47:06.457 | DEBUG    | src.shell:execute_command:179 - Executing command: touch src/bob.py
2024-12-08 19:47:06.465 | INFO     | src.shell:process_task:265 - ✓ Success!
2024-12-08 19:47:06.465 | INFO     | src.shell:process_task:261 - 
>>> git add src/bob.py
2024-12-08 19:47:06.465 | DEBUG    | src.shell:execute_command:179 - Executing command: git add src/bob.py
2024-12-08 19:47:06.476 | INFO     | src.shell:process_task:265 - ✓ Success!
2024-12-08 19:47:06.476 | INFO     | src.shell:process_task:228 - 
📊 Analyzing current state...
2024-12-08 19:47:08.281 | DEBUG    | src.shell:process_task:235 - 
Analysis:
### Analysis:

1. **Actions Needed**:
   - The file `src/bob.py` has been successfully added with `git add`.
   - Commit the addition of `src/bob.py` to version control with:  
     ```bash
     git commit -m "Add src/bob.py"
     ```

2. **Potential Issues**:
   - The file `src/shell.py` has been modified and is not staged for commit. Decide whether to handle this file now (stage and commit) or defer it.
   - If `src/bob.py` is empty (since the `touch` command was just run), make sure it’s intentional. Otherwise, you might want to populate it with content before committing.

3. **Task Completion**:
   - The task of adding `src/bob.py` is **not yet complete**. The remaining step is committing the change.
2024-12-08 19:47:08.827 | INFO     | src.shell:process_task:261 - 
>>> git commit -m "Add src/bob.py"
2024-12-08 19:47:08.828 | DEBUG    | src.shell:execute_command:179 - Executing command: git commit -m "Add src/bob.py"
2024-12-08 19:47:08.851 | INFO     | src.shell:process_task:265 - ✓ Success!
2024-12-08 19:47:08.851 | INFO     | src.shell:process_task:267 - [main 416726a] Add src/bob.py
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 src/bob.py
2024-12-08 19:47:08.851 | INFO     | src.shell:process_task:228 - 
📊 Analyzing current state...
2024-12-08 19:47:10.763 | DEBUG    | src.shell:process_task:235 - 
Analysis:
### Analysis of the Current State:
1. **What specific actions need to be taken:**
   - No further actions are required; the task of adding `src/bob.py` is complete. The file has been created, added to Git, and committed successfully.

2. **Any potential issues or risks:**
   - The file `src/shell.py` has unstaged modifications based on the `git status` output. Since this was not mentioned in the task, ensure these changes are intentional and handled (either committed, restored, or ignored) to avoid accidental loss or inclusion in future commits.
   - The new file `src/bob.py` currently has no content. If it was intended to contain something specific, ensure it is updated before further development or commits.

3. **Whether the task is already complete or what remains:**
   - The task of adding the file is **complete**.
   - Verify contents of the new file if necessary.
   - Address the unstaged changes in `src/shell.py` as a separate task if needed.
2024-12-08 19:47:11.040 | INFO     | src.shell:process_task:246 - 
✓ Task completed successfully!
```