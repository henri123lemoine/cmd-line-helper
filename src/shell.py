import argparse
import subprocess
import sys
from typing import List, Tuple

from loguru import logger
from openai import OpenAI


def setup_logging(debug: bool):
    """Configure logging based on debug mode."""
    logger.remove()  # Remove default handler
    if debug:
        logger.add(sys.stderr, level="DEBUG")
    else:
        # Only show ERROR and CRITICAL by default
        logger.add(sys.stderr, level="ERROR")


class ShellHelper:
    def __init__(self, api_key: str, trust_mode: bool = False):
        """Initialize the shell helper with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        self.trust_mode = trust_mode

        self.system_prompt = """You are a helpful CLI assistant that suggests bash commands.
        Your goal is to provide complete solutions that accomplish the full task.
        Always try to think if additional commands would be helpful to complete the task fully.
        For example:
        - When committing to git, consider if the files need to be added first
        - When creating directories, consider if any files need to be created inside
        - When installing packages, consider if the environment needs to be activated
        - When starting services, consider if config files need to be created
        
        Return only the exact commands to run, one per line, nothing else.
        Do not include explanations or markdown formatting."""

    def get_command_suggestion(self, task_description: str) -> List[str]:
        """Get command suggestion(s) from LLM."""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": task_description},
            ],
        )
        commands = response.choices[0].message.content.strip().split("\n")
        return [cmd.strip() for cmd in commands if cmd.strip()]

    def execute_command(self, command: str) -> Tuple[bool, str]:
        """Execute a shell command and return success status and output."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return (
                result.returncode == 0,
                result.stdout if result.returncode == 0 else result.stderr,
            )
        except Exception as e:
            return False, str(e)

    def run_interactive(self):
        """Run the shell helper in interactive mode."""
        while True:
            try:
                task = input("\nWhat would you like to do? (or 'exit' to quit): ").strip()
                if task.lower() == "exit":
                    break

                commands = self.get_command_suggestion(task)
                if not commands:
                    continue

                if len(commands) > 1:
                    print(f"\nSuggested commands:")
                    for i, cmd in enumerate(commands, 1):
                        print(f"{i}. {cmd}")
                    logger.debug(f"Suggesting {len(commands)} commands to complete this task")

                    if not self.trust_mode:
                        if input("\nExecute all commands? (y/n): ").lower() != "y":
                            print("Command chain cancelled")
                            continue

                for cmd in commands:
                    if not self.trust_mode:
                        print(f"\nSuggested command: {cmd}")
                        if input("Execute this command? (y/n): ").lower() != "y":
                            print("Command chain cancelled")
                            break
                    else:
                        print(f"\nExecuting: {cmd}")

                    success, output = self.execute_command(cmd)
                    if success:
                        print("✓ Success!")
                        logger.debug("Command executed successfully")
                        if output:
                            print(output)
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


if __name__ == "__main__":
    from src.settings import OPENAI_API_KEY

    args = parse_args()
    setup_logging(args.debug)

    try:
        helper = ShellHelper(api_key=OPENAI_API_KEY, trust_mode=args.trust)
        print("Welcome to the LLM Shell Helper!")
        if args.debug:
            print("Debug mode enabled")
        if helper.trust_mode:
            print("Trust mode enabled - commands will execute without confirmation")
        print("--------------------------------")
        helper.run_interactive()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        exit(1)
