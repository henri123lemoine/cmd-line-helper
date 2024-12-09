import argparse
import shlex
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import ell
from loguru import logger


@ell.simple(model="chatgpt-4o-latest")
def get_command_suggestions(
    task: str, dir_structure: str = "", command_history: str = "", error_context: str = ""
) -> str:
    """You are a helpful and intelligent CLI assistant that suggests bash commands.
    Your goal is to provide complete solutions that accomplish the full task.
    Always try to think if additional commands would be helpful to complete the task fully.

    You should interpret what the user wants to accomplish, not just literally what they type.
    For example:
    - If they ask to 'diff' a file in a git repo, they probably mean 'git diff'
    - If they ask to 'check status', they probably mean 'git status'
    - If they mention 'viewing changes', they probably want 'git diff'

    IMPORTANT: Return ONLY the exact commands to run, one per line. DO NOT include any explanations
    or descriptions. Return ONLY valid shell commands that can be executed directly.

    Example good response:
    git diff file.py

    Example bad response:
    If you want to see files, use: ls -la"""

    prompt = f"""Current directory structure:
{dir_structure}

{command_history if command_history else ''}
{f'Error context:\n{error_context}\n' if error_context else ''}
Task: {task}"""

    return prompt


@ell.simple(model="chatgpt-4o-latest")
def analyze_error_pattern(error_history: str, dir_structure: str, task: str) -> str:
    """You are a CLI debugging assistant."""

    prompt = f"""Analyze the command execution history and error pattern to explain why commands are failing.
Provide a brief but specific explanation of the root cause, focusing on factual observations
rather than suggestions.

Recent command execution history:
{error_history}

Current directory structure:
{dir_structure}

Original task: {task}

What is the root cause of these failures? Focus on the current state and what's missing or incorrect."""
    return prompt


@ell.simple(model="chatgpt-4o-latest")
def get_recovery_commands(analysis: str, dir_structure: str, task: str) -> str:
    """You are a CLI assistant that suggests recovery commands.
    Your goal is to provide executable bash commands that will fix the current issue.
    Return ONLY executable commands, one per line, without any formatting, quotes, or explanation.

    Example good response:
    touch hello.py
    git add hello.py

    Example bad response:
    ```bash
    touch hello.py
    ```

    Bad response (with explanation):
    # First create the file
    touch hello.py"""

    prompt = f"""Based on this error analysis:
{analysis}

Current directory structure:
{dir_structure}

Original task: {task}

What commands would fix this issue? Return ONLY the commands, one per line."""

    return prompt


class ShellHelper:
    def __init__(self, trust_mode: bool = False, max_retries: int = 3):
        """Initialize the shell helper."""
        self.trust_mode = trust_mode
        self.max_retries = max_retries
        self.command_context: List[Dict] = []

    def _get_directory_info(self) -> str:
        """Get directory structure using tree or ls as fallback."""
        try:
            result = subprocess.run(["tree"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            pass

        try:
            result = subprocess.run(["ls", "-R"], capture_output=True, text=True)
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to get directory info: {e}")
            return "Unable to get directory structure"

    def _add_to_context(self, command: str, output: str, success: bool):
        """Add a command and its output to the context history."""
        self.command_context.append(
            {
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "output": output[:500] if output else "",  # Truncate long outputs
                "success": success,
            }
        )
        # Keep only last 5 commands for context
        self.command_context = self.command_context[-5:]

    def _format_command_history(self) -> str:
        """Format command history for the prompt."""
        if not self.command_context:
            return ""

        history = "Recent commands and their outputs:\n"
        for cmd in self.command_context:
            history += f"$ {cmd['command']}\n"
            if cmd["output"]:
                history += f"Output: {cmd['output']}\n"
            history += f"Status: {'Success' if cmd['success'] else 'Failed'}\n\n"
        return history

    def get_commands(self, task_description: str, error_context: Optional[str] = None) -> List[str]:
        """Get command suggestion(s) from LLM with command history context."""
        response = get_command_suggestions(
            task=task_description,
            dir_structure=self._get_directory_info(),
            command_history=self._format_command_history(),
            error_context=error_context or "",
        )
        return [cmd.strip() for cmd in response.split("\n") if cmd.strip()]

    def execute_command(
        self, command: str, task_description: str, retry_count: int = 0
    ) -> Tuple[bool, str]:
        """Execute a shell command and return success status and output."""
        try:
            args = shlex.split(command)
            result = subprocess.run(args, shell=False, capture_output=True, text=True, check=False)

            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            self._add_to_context(command, output, success)

            if not success:
                if retry_count >= self.max_retries:
                    # First get analysis
                    logger.debug("\n⚠️ Multiple attempts failed. Analyzing the issue...")
                    analysis = analyze_error_pattern(
                        error_history=str(self.command_context[-self.max_retries :]),
                        dir_structure=self._get_directory_info(),
                        task=task_description,
                    )

                    if self.trust_mode:
                        # In trust mode, get and execute recovery commands
                        logger.info(f"\n🔍 Analysis: {analysis}")
                        recovery_commands = get_recovery_commands(
                            analysis=analysis,
                            dir_structure=self._get_directory_info(),
                            task=task_description,
                        ).split("\n")

                        if recovery_commands:
                            logger.info("\n🔄 Attempting recovery based on analysis...")
                            for cmd in recovery_commands:
                                if not cmd.strip():
                                    continue
                                logger.info(f"\n>>> {cmd}")
                                recovery_result = self.execute_command(
                                    cmd, task_description, 0
                                )  # Reset retry count
                                if not recovery_result[0]:
                                    return False, f"Recovery failed: {recovery_result[1]}"
                            return True, "Recovery completed successfully"

                    return False, f"Error analysis: {analysis}"
                else:
                    return False, "Could not generate recovery command"

            return success, output

        except Exception as e:
            self._add_to_context(command, str(e), False)
            return False, str(e)

    def run_interactive(self):
        """Run the shell helper in interactive mode."""
        logger.info(
            "Welcome to the LLM Shell Helper!"
            + (" (trust mode activated)" if self.trust_mode else "")
        )

        while True:
            try:
                task = input("\nWhat would you like to do? (or 'exit' to quit): ").strip()
                if task.lower() == "exit":
                    break

                commands = self.get_commands(task)
                if not commands:
                    continue

                if not self.trust_mode and len(commands) > 1:
                    if input("\nExecute all commands? (y/n): ").lower() != "y":
                        logger.info("Command chain cancelled")
                        continue

                for cmd in commands:
                    logger.debug(f"Executing command: {cmd}")
                    if not self.trust_mode:
                        logger.info(f"\n>>> {cmd}")
                        if input("Execute this command? (y/n): ").lower() != "y":
                            logger.info("Command chain cancelled")
                            break
                    else:
                        logger.info(f"\n>>> {cmd}")

                    success, output = self.execute_command(cmd, task, 3)
                    if success:
                        logger.info("✓ Success!")
                        if output.strip():
                            logger.info(output.rstrip())
                    else:
                        logger.warning(f"✗ Failed: {output}")
                        logger.error(f"Command failed: {output}")
                        break

            except KeyboardInterrupt:
                logger.info("\nExiting...")
                break
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                logger.warning("\nAn error occurred. Please try again or type 'exit' to quit")


def parse_args():
    parser = argparse.ArgumentParser(description="LLM Shell Helper")
    parser.add_argument(
        "--trust",
        action="store_true",
        help="Run in trust mode (executes commands without asking for permission)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


def main():
    from src.logging import setup_logging

    args = parse_args()
    setup_logging(args.debug)

    try:
        helper = ShellHelper(trust_mode=args.trust)
        helper.run_interactive()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
