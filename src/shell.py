import argparse
import shlex
import subprocess
import sys
from typing import List, Optional, Tuple

from loguru import logger
from openai import OpenAI


def setup_logging(debug: bool):
    """Configure logging based on debug mode."""
    logger.remove()
    if debug:
        logger.add(sys.stderr, level="DEBUG")
    else:
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

    def _get_directory_info(self) -> str:
        """Get directory structure using tree or ls as fallback."""
        try:
            result = subprocess.run(["tree"], capture_output=True, text=True)
            if result.returncode == 0:
                # Truncate tree output to first 10 and last 10 output lines
                return "\n".join(
                    result.stdout.split("\n")[:10] + ["..."] + result.stdout.split("\n")[-10:]
                )
        except FileNotFoundError:
            pass

        # Fallback to ls if tree fails or isn't available
        try:
            result = subprocess.run(["ls", "-R"], capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            logger.error(f"Failed to get directory info: {e}")
            return "Unable to get directory structure"

    def get_command_suggestion(
        self, task_description: str, error_context: Optional[str] = None
    ) -> List[str]:
        """Get command suggestion(s) from LLM, optionally with error context."""
        messages = [{"role": "system", "content": self.system_prompt}]

        if error_context:
            # Add error context to the prompt
            messages.append(
                {
                    "role": "user",
                    "content": f"""The previous command failed with the following context:
                {error_context}
                
                Current directory structure:
                {self._get_directory_info()}
                
                Please provide a corrected command for: {task_description}""",
                }
            )
        else:
            messages.append({"role": "user", "content": task_description})

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

            if result.returncode != 0:
                # Command failed, get new suggestion with error context
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

            return True, result.stdout

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
