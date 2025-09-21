import os
import shlex
import sys
import requests
import shutil
import subprocess
import re
from dotenv import load_dotenv

# Import prompt_toolkit components
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, PathCompleter, merge_completers

# --- Load Environment Variables ---
load_dotenv()

# --- Terminal Colors ---
PROMPT_COLOR = '\033[92m' # Green
AI_COLOR = '\033[96m'   # Cyan
ERROR_COLOR = '\033[91m' # Red
RESET_COLOR = '\033[0m'

# --- Built-in Command Handlers (Operating on Real FS) ---

def cmd_cd(args):
    """Changes the current working directory."""
    try:
        target_path = args[0] if args else os.path.expanduser('~')
        os.chdir(target_path)
    except FileNotFoundError:
        return f"cd: no such file or directory: {target_path}"
    except Exception as e:
        return f"cd: an error occurred: {e}"
    return ""

def cmd_ls(args):
    """Lists files and directories."""
    try:
        target_path = args[0] if args else '.'
        contents = os.listdir(target_path)
        return "\t".join(sorted(contents))
    except FileNotFoundError:
        return f"ls: cannot access '{target_path}': No such file or directory"
    except Exception as e:
        return f"ls: an error occurred: {e}"

def cmd_pwd(args):
    """Prints the current working directory."""
    try:
        return os.getcwd()
    except Exception as e:
        return f"pwd: an error occurred: {e}"

def cmd_mkdir(args):
    """Creates a new directory."""
    if not args: return "mkdir: missing operand"
    try:
        os.mkdir(args[0])
    except FileExistsError:
        return f"mkdir: cannot create directory '{args[0]}': File exists"
    except Exception as e:
        return f"mkdir: an error occurred: {e}"
    return ""

def cmd_touch(args):
    """Creates an empty file or updates its timestamp."""
    if not args: return "touch: missing operand"
    try:
        with open(args[0], 'a'):
            os.utime(args[0], None)
    except Exception as e:
        return f"touch: an error occurred: {e}"
    return ""

def cmd_cat(args):
    """Displays the content of a file."""
    if not args: return "cat: missing operand"
    try:
        with open(args[0], 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"cat: {args[0]}: No such file or directory"
    except IsADirectoryError:
         return f"cat: {args[0]}: Is a directory"
    except Exception as e:
        return f"cat: an error occurred: {e}"

def cmd_echo(args):
    """Prints text or writes it to a file."""
    if '>' in args:
        try:
            idx = args.index('>')
            content = " ".join(args[:idx])
            filename = args[idx + 1]
            with open(filename, 'w') as f:
                f.write(content + '\n')
            return ""
        except IndexError:
            return "Syntax error: no file specified for redirection."
        except Exception as e:
            return f"echo: an error occurred: {e}"
    else:
        return " ".join(args)

def cmd_rm(args):
    """Removes files or directories."""
    if not args: return "rm: missing operand"
    recursive = '-r' in args
    targets = [arg for arg in args if arg != '-r']
    
    for target in targets:
        try:
            if not os.path.exists(target):
                return f"rm: cannot remove '{target}': No such file or directory"
            if os.path.isfile(target):
                os.remove(target)
            elif os.path.isdir(target):
                if recursive:
                    shutil.rmtree(target)
                else:
                    return f"rm: cannot remove '{target}': Is a directory (use -r)"
        except Exception as e:
            return f"rm: an error occurred: {e}"
    return ""

def cmd_mv(args):
    """Moves or renames a file or directory."""
    if len(args) != 2: return "mv: missing source or destination operand"
    try:
        shutil.move(args[0], args[1])
    except FileNotFoundError:
        return f"mv: cannot move '{args[0]}': No such file or directory"
    except Exception as e:
        return f"mv: an error occurred: {e}"
    return ""

def cmd_clear(args):
    """Clears the terminal screen."""
    print("\033c", end="")
    return ""

def cmd_exit(args):
    """Exits the terminal."""
    sys.exit("Goodbye!")

def cmd_help(args):
    return """
Available commands:
  ls, cd, pwd, mkdir, cat, echo, rm, mv, touch, clear, exit, help
AI Integration:
  Type any natural language sentence to get a command suggestion.
  Example: create a directory called my_project
"""

BUILTIN_COMMANDS = {
    'ls': cmd_ls, 'cd': cmd_cd, 'pwd': cmd_pwd, 'mkdir': cmd_mkdir,
    'cat': cmd_cat, 'echo': cmd_echo, 'rm': cmd_rm, 'mv': cmd_mv,
    'touch': cmd_touch, 'clear': cmd_clear, 'exit': cmd_exit, 'help': cmd_help,
}

# --- AI Command Generation ---
def get_ai_command(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or "YOUR_API_KEY" in api_key:
        return {"error": "OpenRouter API key not found in .env file."}

    print(f"{AI_COLOR}Asking AI...{RESET_COLOR}", end='\r')
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": f"You are a shell command expert for a {'Windows' if os.name == 'nt' else 'Linux/macOS'} terminal. Convert the user's request into a single, executable command. Provide only the command."},
                    {"role": "user", "content": prompt}
                ]
            }
        )
        response.raise_for_status()
        result = response.json()
        
        raw_command = result['choices'][0]['message']['content'].strip()
        # Use a more robust regular expression to clean various model-specific tokens
        command = re.sub(r'\[.*?\]|<s>|</s>|`', '', raw_command).strip()
        
        return {"command": command}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}
    except (KeyError, IndexError):
        return {"error": "Failed to parse API response."}

# --- Main REPL Loop ---
def main():
    # Use a file-based history to remember commands between sessions
    history = FileHistory(os.path.expanduser('~/.ai_terminal_history'))
    
    # Setup autocompletion for commands and file paths
    command_completer = WordCompleter(list(BUILTIN_COMMANDS.keys()), ignore_case=True)
    path_completer = PathCompleter()
    merged_completer = merge_completers([command_completer, path_completer])

    session = PromptSession(
        history=history,
        completer=merged_completer,
        auto_suggest=None
    )

    print("Welcome to the AI Terminal. Type 'help' for a list of commands.")

    while True:
        try:
            prompt_str = f"{PROMPT_COLOR}{os.getcwd()}{RESET_COLOR}$ "
            user_input = session.prompt(prompt_str)
            
            if not user_input.strip():
                continue

            # Check if the command is a built-in one
            try:
                tokens = shlex.split(user_input)
                if not tokens: continue
                command_name = tokens[0]
                args = tokens[1:]
            except ValueError:
                print(f"{ERROR_COLOR}Error: Unmatched quotes in command.{RESET_COLOR}")
                continue


            if command_name in BUILTIN_COMMANDS:
                output = BUILTIN_COMMANDS[command_name](args)
                if output:
                    print(output)
            else:
                # If not a built-in, treat as a prompt for the AI
                ai_result = get_ai_command(user_input)
                print(" " * 20, end='\r') # Clear the "Asking AI..." message

                if "error" in ai_result:
                    print(f"{ERROR_COLOR}{ai_result['error']}{RESET_COLOR}")
                else:
                    suggested_command = ai_result['command']
                    if not suggested_command:
                        print(f"{ERROR_COLOR}AI returned an empty command.{RESET_COLOR}")
                        continue
                        
                    print(f"{AI_COLOR}AI Suggestion: {RESET_COLOR}{suggested_command}")
                    
                    # Ask user for confirmation to execute
                    confirm = session.prompt(f"Execute this command? (y/n): ", default='y').lower()
                    if confirm in ['y', 'yes']:
                        try:
                            # CORRECTED LOGIC: Check if AI suggested a built-in command first
                            s_tokens = shlex.split(suggested_command)
                            s_command_name = s_tokens[0]
                            s_args = s_tokens[1:]

                            if s_command_name in BUILTIN_COMMANDS:
                                # Execute built-in command in the current process
                                output = BUILTIN_COMMANDS[s_command_name](s_args)
                                if output:
                                    print(output)
                            else:
                                # Execute other commands in a subprocess
                                subprocess.run(suggested_command, shell=True, check=True)

                        except subprocess.CalledProcessError as e:
                            print(f"{ERROR_COLOR}Command failed with exit code {e.returncode}{RESET_COLOR}")
                        except FileNotFoundError:
                            print(f"{ERROR_COLOR}Command not found: {s_command_name}{RESET_COLOR}")
                        except IndexError:
                            print(f"{ERROR_COLOR}AI returned an empty or invalid command.{RESET_COLOR}")
                        except Exception as e:
                            print(f"{ERROR_COLOR}Error executing command: {e}{RESET_COLOR}")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"{ERROR_COLOR}An unexpected error occurred: {e}{RESET_COLOR}")

if __name__ == "__main__":
    main()

