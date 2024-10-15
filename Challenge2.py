import re, sys
from termcolor import colored


class stack: #Basic stack to store line number of the start of the current while loop
    def __init__(self):
        self.start_pos = []
        return

    def push(self, line_num):
        self.start_pos.append(line_num)

    def pop(self):
        return self.start_pos.pop()

    def get_size(self):
        return len(self.start_pos)


class interpreter:
    variables = {}

    def __init__(self, lines):
        self.while_stack = stack()
        self.skip = False
        return


    def output_variables(self, line_num): #Output all variables with the values with the previously processed line number
        print(f"Line: {line_num}")
        for var in self.variables:
            print(f"    {var}: {self.variables[var]}")


    def check_exists(self, var): #Check if variable exists
        return var in self.variables


    def clear(self, var): #Set variable to 0
        self.variables[var] = 0


    def incr(self, var): #Increase value of variable by 1
        if not self.check_exists(var):
            self.message(1,f"Warning: {var} does not exist, defaulting to 0")
            self.variables[var] = 0
        self.variables[var] += 1


    def decr(self, var): #Decrease value of variable by 1
        if not self.check_exists(var):
            self.message(1,f"Warning: {var} does not exist, defaulting to 0")
            self.variables[var] = 0
        self.variables[var] -= 1


    def message(self, level, text): #Output message in relevant colour based on the level of significance
        match level:
            case 0:
                print(colored(text,'green'))
            case 1:
                print(colored(text,'yellow'))
            case 2:
                print(colored(text+f'\n\nSystem Quitting','red')) #Errors that may cause the program to crash will cause the program to quit preventably
                sys.exit()


    def raise_error(self, line, pos, line_num, expected="", version=0, arg_required=0, arg_given=0): #Describe relevant error according to 'version'
        match version:
            case 0:
                error = f"Error: Expected '{expected}'"
            case 1:
                error = f"Error: Expected {arg_required} argument(s), {arg_given} given"
            case 2:
                error = f"Error: Invalid Syntax"
            case 3:
                error = f"Warning: '{expected}' does not exist, defaulting to 0"
        error = error+f"\n    {line};   (line:{line_num+1})\n    "
        for i in range(pos):
            error = error + " "
        error = error + '^'
        if version == 3:
            self.message(1,error)
        else:
            self.message(2, error)


    def condition(self, arg1, arg2, operator, line_num, line): #Check validity of condition inputs and confirm outcome of operation
        try:
            arg1 = int(arg1)
        except ValueError:
            if not self.check_exists(arg1):
                self.raise_error(line, len(line), line_num, expected=arg1, version=3)
            else:
                arg1 = self.variables[arg1]
        try:
            arg2 = int(arg2)
        except ValueError:
            if not self.check_exists(arg2):
                self.raise_error(line, len(line), line_num, expected=arg2, version=3)
            else:
                arg2 = self.variables[arg2]
        if operator == 'not':
            return arg1 != arg2
        print(self.message(2,"Error: unrecognised operator"))


    def while_loop(self, line_num, line, line_complete): #Check if loop satisfies condition and push the line number to the stack if it does
        loop = self.condition(line[1],line[3],'not', line_num, line_complete)
        if loop:
            self.while_stack.push(line_num)
        return loop


    def interpret_line(self, line, line_complete, line_num): #Interpret a single line
        if not self.skip:
            match line[0]:
                case 'clear':
                    if len(line) == 1: #Raise an error if no argument is provided
                        self.raise_error(line_complete, 5, line_num, version=1, arg_required=1, arg_given=0)
                    elif len(line) > 2: #Raise an error if more than 1 argument is provided
                        self.raise_error(line_complete, 5, line_num, version=1, arg_required=1, arg_given=len(line)-1)
                    else:
                        self.clear(line[1])
                case 'incr':
                    if len(line) == 1: #Raise an error if no argument is provided
                        self.raise_error(line_complete, 4, line_num, version=1, arg_required=1, arg_given=0)
                    elif len(line) > 2: #Raise an error if more than 1 argument is provided
                        self.raise_error(line_complete, 4, line_num, version=1, arg_required=1, arg_given=len(line)-1)
                    else:
                        self.incr(line[1])
                case 'decr':
                    if len(line) == 1: #Raise an error if no argument is provided
                        self.raise_error(line_complete, 4, line_num, version=1, arg_required=1, arg_given=0)
                    elif len(line) > 2: #Raise an error if more than 1 argument is provided
                        self.raise_error(line_complete, 4, line_num, version=1, arg_required=1, arg_given=len(line)-1)
                    else:
                        self.decr(line[1])
                case 'while':
                    if len(line) == 5:
                        if line[2] != 'not':
                            self.raise_error(line_complete, len(line[0]+line[1])+2, line_num, version=2)
                        if line[4] == 'do':
                            if not self.while_loop(line_num, line, line_complete): #If the while loop condition is checked and found to be false, all subsequent lines up to the next 'end;' should be skipped
                                self.skip = True
                        else:
                            self.raise_error(line_complete,len(line_complete), line_num,'do')
                    else:
                        self.raise_error(line_complete, len(line_complete), line_num, version=2)
                case 'end':
                    if len(line) > 1 or self.while_stack.get_size() == 0:
                        self.raise_error(line_complete, 4, line_num, version=2)
                    else:
                        last_while = self.while_stack.pop()
                        if self.while_loop(last_while, self.formatted_lines[last_while], lines[last_while]):
                            return last_while
                case _:
                    print(f"line: {line_complete} ")
                    self.raise_error(line_complete, len(line_complete), line_num, version=2)
        else:
            if line[0] == 'end':
                if len(line) > 1:
                    self.raise_error(line_complete, 4, line_num, version=2)
                else:
                    self.skip = False
        self.output_variables(line_num+1)
        return line_num

    def interpret_script(self, limit): #Interpret the entire script, the parameter 'limit' restricts the number of lines of code processed
        line_num = 0
        self.formatted_lines = []
        for line in lines: #Split each line up
            line_num += 1
            self.formatted_lines.append(re.split(' +', line))
        current_line = 0
        iterations = 0
        while current_line < len(self.formatted_lines) and iterations < limit: #Each line is interpreted until there are no more lines left, or the user set limit is reached
            iterations += 1
            current_line = self.interpret_line(self.formatted_lines[current_line], lines[current_line], current_line) #If a while loop is activated then 'current_line' is set to the relevant line
            current_line += 1


if __name__ == '__main__':
    lines = []
    line = ''

    for character in open('input.txt','r').read(): #Format the text file removing ';' and unnecessary whitespaces
        line = line + character
        if character == ';':
            lines.append(re.sub(' +;', ';', line.strip('\n')).strip(';').strip()) #Generate a list of formated lines
            line = ''

    bare_bones = interpreter(lines)
    bare_bones.interpret_script(1000000000)