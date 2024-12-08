import subprocess
from typing import List, Tuple

from openai import OpenAI


class ShellHelper:
    def __init__(self, api_key: str):
        """Initialize the shell helper with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)

        self.system_prompt = """You are a helpful CLI assistant that suggests bash commands.
        When suggesting commands, only return the exact command to run, nothing else.
        If multiple commands are needed, return them one per line.
        Do not include explanations or markdown formatting."""

    def get_command_suggestion(self, task_description: str, chain_mode: bool = False) -> List[str]:
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

                for cmd in commands:
                    print(f"\nSuggested command: {cmd}")
                    if input("Execute this command? (y/n): ").lower() != "y":
                        continue

                    success, output = self.execute_command(cmd)
                    if success:
                        print("Success!")
                        if output:
                            print(output)
                    else:
                        print(f"Failed: {output}")
                        break

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                print("Please try again or type 'exit' to quit")


if __name__ == "__main__":
    import os

    from src.settings import OPENAI_API_KEY

    try:
        helper = ShellHelper(api_key=OPENAI_API_KEY)
        print("Welcome to the LLM Shell Helper!")
        print("--------------------------------")
        helper.run_interactive()
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)
