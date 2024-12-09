import argparse
import shlex
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import ell
from loguru import logger


@ell.simple(model="chatgpt-4o-latest")
def gather_system_info(task: str, dir_structure: str = "") -> str:
    """You are a CLI intelligence gatherer. Your goal is to identify what information
    would be helpful to know before suggesting commands for the given task.

    Return ONLY executable shell commands that gather information, one per line.
    These commands should be safe information gathering commands like ls, pwd, git status, etc.
    DO NOT return commands that make any changes."""

    prompt = f"""Task to be performed: {task}

Current directory structure:
{dir_structure}

What information would be helpful to gather before proceeding with this task?
Return ONLY safe information gathering commands, one per line.
Example commands: pwd, ls, git status, git branch, etc.

Do not return commands that modify anything."""
    return prompt


@ell.simple(model="chatgpt-4o-latest")
def analyze_system_state(
    task: str,
    dir_structure: str,
    gathered_info: Dict[str, str],
    command_history: Optional[List[Dict]] = None,
) -> str:
    """You are a CLI system state analyzer. Your goal is to assess the current state
    and determine what actions need to be taken to accomplish the task.

    Return a concise analysis of:
    1. What needs to be done
    2. Any potential issues or risks
    3. Whether the task is complete or what remains to be done"""

    info_str = "\n".join(f"{cmd}:\n{output}" for cmd, output in gathered_info.items())
    history_str = ""
    if command_history:
        history_str = "Recent commands and their results:\n" + "\n".join(
            f"$ {cmd['command']}\nSuccess: {cmd['success']}\nOutput: {cmd['output']}"
            for cmd in command_history[-3:]
        )

    prompt = f"""Task to be performed: {task}

Current directory structure:
{dir_structure}

Gathered system information:
{info_str}

{history_str if history_str else ''}

Analyze the current state and what needs to be done.
Focus on:
1. What specific actions need to be taken
2. Any potential issues or risks
3. Whether the task is already complete or what remains

Be concise and factual."""
    return prompt


@ell.simple(model="chatgpt-4o-latest")
def get_next_commands(
    task: str,
    analysis: str,
    dir_structure: str = "",
    command_history: str = "",
) -> str:
    """You are a helpful and intelligent CLI assistant that suggests bash commands.
    Your goal is to provide the next step(s) needed based on the current analysis.

    Return ONLY executable commands, one per line. If no further commands are needed,
    return 'TASK_COMPLETE'.

    Example good response:
    git add file.py
    git commit -m "Update file.py"

    Example when done:
    TASK_COMPLETE"""

    prompt = f"""Task to be performed: {task}

Current analysis:
{analysis}

Directory structure:
{dir_structure}

{command_history if command_history else ''}

What commands should be run next? If the task is complete, return TASK_COMPLETE.
Return ONLY executable commands or TASK_COMPLETE."""
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

    def execute_command(self, command: str, task_description: str) -> Tuple[bool, str]:
        """Execute a shell command and return success status and output."""
        try:
            args = shlex.split(command)
            result = subprocess.run(args, shell=False, capture_output=True, text=True, check=False)

            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            self._add_to_context(command, output, success)

            return success, output

        except Exception as e:
            self._add_to_context(command, str(e), False)
            return False, str(e)

    def gather_information(self, task: str) -> Dict[str, str]:
        """Gather relevant system information before proceeding."""
        logger.info("\n🔍 Gathering system information...")

        info_commands = gather_system_info(
            task=task,
            dir_structure=self._get_directory_info(),
        ).split("\n")

        gathered_info = {}
        for cmd in info_commands:
            if not cmd.strip():
                continue
            logger.debug(f"Gathering info: {cmd}")
            success, output = self.execute_command(cmd, task)
            if success:
                gathered_info[cmd] = output
            else:
                logger.warning(f"Failed to gather info with {cmd}: {output}")

        return gathered_info

    def process_task(self, task: str) -> bool:
        """Process a single task with information gathering and analysis."""
        try:
            # Step 1: Gather information
            gathered_info = self.gather_information(task)

            while True:
                # Step 2: Analyze current state
                logger.info("\n📊 Analyzing current state...")
                analysis = analyze_system_state(
                    task=task,
                    dir_structure=self._get_directory_info(),
                    gathered_info=gathered_info,
                    command_history=self.command_context,
                )
                logger.debug(f"\nAnalysis:\n{analysis}")

                # Step 3: Get next commands
                commands = get_next_commands(
                    task=task,
                    analysis=analysis,
                    dir_structure=self._get_directory_info(),
                    command_history=self._format_command_history(),
                ).split("\n")

                if not commands or commands[0].strip() == "TASK_COMPLETE":
                    logger.info("\n✓ Task completed successfully!")
                    return True

                # Step 4: Execute commands
                for cmd in commands:
                    cmd = cmd.strip()
                    if not cmd:
                        continue

                    if not self.trust_mode:
                        logger.info(f"\n>>> {cmd}")
                        if input("Execute this command? (y/n): ").lower() != "y":
                            logger.info("Command execution cancelled")
                            return False
                    else:
                        logger.info(f"\n>>> {cmd}")

                    success, output = self.execute_command(cmd, task)
                    if success:
                        logger.info("✓ Success!")
                        if output.strip():
                            logger.info(output.rstrip())
                    else:
                        logger.warning(f"✗ Failed: {output}")
                        # Don't immediately return - let the next analysis determine what to do
                        break

                # The loop will continue with another analysis to determine next steps

        except Exception as e:
            logger.error(f"Error processing task: {e}")
            return False

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

                self.process_task(task)

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
