import sys
from termcolor import colored

def message(level, text):  # Output message in relevant colour based on the level of significance
    match level:
        case 0:
            print(colored(text, 'green'))
        case 1:
            print(colored(text, 'yellow'))
        case 2:
            print(colored(text + f'\n\nSystem Quitting',
                          'red'))  # Errors that may cause the program to crash will cause the program to quit
            sys.exit()


def raise_error(line, pos, line_index, expected="", invalid_message="Unknown", version=0, arg_required=0, arg_given=0):  # Describe relevant error according to 'version'
    match version:
        case 0:
            error = f"Error: Expected '{expected}'"
        case 1:
            error = f"Error: Expected {arg_required} argument(s), {arg_given} given"
        case 2:
            error = f"Error: Invalid Syntax"
        case 3:
            error = f"Warning: '{expected}' does not exist, defaulting to 0"
        case 4:
            error = f"Error: Unexpected '{expected}'"
        case 5:
            error = f"Error: Invalid code, {invalid_message}"
    if expected == ';':
        error = error + f"\n    {line}   (line:{line_index + 1})\n    "
    else:
        error = error + f"\n    {line};   (line:{line_index + 1})\n    "
    for i in range(pos):
        error = error + " "
    error = error + '^'
    if version == 3:
        message(1, error)
    else:
        message(2, error)
