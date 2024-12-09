import argparse
import shlex
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import ell
from loguru import logger
from openai import OpenAI

from src.logging import setup_logging


@ell.simple(model="chatgpt-4o-latest")
def cli_assistant(intput_1: str, input_2: str):
    """You are a helpful CLI assistant that suggests bash commands."""

    prompt = f"""Your goal is to provide ..."""

    return prompt


class ShellHelper:
    def __init__(self, api_key: str, trust_mode: bool = False):
        """Initialize the shell helper with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        self.trust_mode = trust_mode
        self.command_context: List[Dict] = []  # Store recent command history

        self.system_prompt = """You are a helpful CLI assistant that suggests bash commands.
        Your goal is to provide complete solutions that accomplish the full task.
        Always try to think if additional commands would be helpful to complete the task fully.
        
        IMPORTANT: Return ONLY the exact commands to run, one per line. DO NOT include any explanations 
        or descriptions. Return ONLY valid shell commands that can be executed directly.
        
        Example good response:
        ls -la
        
        Example bad response:
        If you want to see files, use: ls -la
        
        Bad responses will cause errors. Return ONLY the command itself."""

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

    def get_command_suggestion(
        self, task_description: str, error_context: Optional[str] = None
    ) -> List[str]:
        """Get command suggestion(s) from LLM with command history context."""
        # Build context string from command history
        context = ""
        if self.command_context:
            context = "Recent commands and their outputs:\n"
            for cmd in self.command_context:
                context += f"$ {cmd['command']}\n"
                if cmd["output"]:
                    context += f"Output: {cmd['output']}\n"
                context += f"Status: {'Success' if cmd['success'] else 'Failed'}\n\n"

        messages = [{"role": "system", "content": self.system_prompt}]

        content = f"""Current directory structure:
{self._get_directory_info()}

{context if context else ''}
{f'Error context:\n{error_context}\n' if error_context else ''}
Task: {task_description}"""

        messages.append({"role": "user", "content": content})

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        commands = response.choices[0].message.content.strip().split("\n")
        return [cmd.strip() for cmd in commands if cmd.strip()]

    def execute_command(self, command: str, task_description: str) -> Tuple[bool, str]:
        """Execute a shell command and return success status and output."""
        try:
            args = shlex.split(command)
            result = subprocess.run(args, shell=False, capture_output=True, text=True, check=False)

            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            self._add_to_context(command, output, success)

            if not success:
                error_context = f"""
                Failed command: {command}
                Error output: {result.stderr}
                Return code: {result.returncode}
                """

                logger.debug("Command failed, getting new suggestion with error context")
                new_commands = self.get_command_suggestion(task_description, error_context)

                if new_commands:
                    print("\n🔄 Attempting recovery with modified command...")
                    for new_cmd in new_commands:
                        print(f"\n>>> {new_cmd}")
                        if not self.trust_mode:
                            if input("Execute this modified command? (y/n): ").lower() != "y":
                                return False, "Modified command execution cancelled by user"

                        # Execute the new command
                        return self.execute_command(new_cmd, task_description)
                else:
                    return False, "Could not generate recovery command"

            return success, output

        except Exception as e:
            self._add_to_context(command, str(e), False)
            return False, str(e)

    def run_interactive(self):
        """Run the shell helper in interactive mode."""
        print(
            "Welcome to the LLM Shell Helper!"
            + (" (trust mode activated)" if self.trust_mode else "")
        )

        while True:
            try:
                task = input("\nWhat would you like to do? (or 'exit' to quit): ").strip()
                if task.lower() == "exit":
                    break

                commands = self.get_command_suggestion(task)
                if not commands:
                    continue

                if not self.trust_mode and len(commands) > 1:
                    if input("\nExecute all commands? (y/n): ").lower() != "y":
                        print("Command chain cancelled")
                        continue

                for cmd in commands:
                    logger.debug(f"Executing command: {cmd}")
                    if not self.trust_mode:
                        print(f"\n>>> {cmd}")
                        if input("Execute this command? (y/n): ").lower() != "y":
                            print("Command chain cancelled")
                            break
                    else:
                        print(f"\n>>> {cmd}")

                    success, output = self.execute_command(cmd, task)
                    if success:
                        print("✓ Success!")
                        if output.strip():
                            print(output.rstrip())
                    else:
                        print(f"✗ Failed: {output}")
                        logger.error(f"Command failed: {output}")
                        break

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"An error occurred: {e}")
                print("\nAn error occurred. Please try again or type 'exit' to quit")


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
    from src.settings import OPENAI_API_KEY

    args = parse_args()
    setup_logging(args.debug)

    try:
        helper = ShellHelper(api_key=OPENAI_API_KEY, trust_mode=args.trust)
        print(
            "Welcome to the LLM Shell Helper!" + (" (trust mode activated)" if args.trust else "")
        )
        helper.run_interactive()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
