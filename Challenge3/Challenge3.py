import re, Report


class Stack: #Basic stack to store line number of the start of the current while loop
    def __init__(self):
        self.start_pos = []
        return

    def push(self, line_num):
        self.start_pos.append(line_num)

    def pop(self):
        return self.start_pos.pop()

    def get_size(self):
        return len(self.start_pos)


class Interpreter:
    variables = {}

    def __init__(self, lines, limit): # Interpret the entire script, the parameter 'limit' restricts the number of lines of code processed

        self.while_stack = Stack()
        self.skip = False
        line_num = 0
        self.formatted_lines = []
        for line in lines:  # Split each line up
            line_num += 1
            self.formatted_lines.append(re.split(' +', line))
        self.validate_while(self.formatted_lines, lines)
        current_line = 0
        iterations = 0
        while current_line < len(self.formatted_lines) and iterations < limit:  # Each line is interpreted until there are no more lines left, or the user set limit is reached
            iterations += 1
            current_line = self.interpret_line(lines[current_line],current_line)  # If a while loop is activated then 'current_line' is set to the relevant line
            current_line += 1
        if iterations >= limit:
            Report.message(2, "Error: maximum iterations reached")
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
            Report.message(1,f"Warning: '{var}' does not exist, defaulting to 0")
            self.variables[var] = 0
        else:
            self.variables[var] += 1


    def decr(self, var): #Decrease value of variable by 1
        if not self.check_exists(var):
            Report.message(1,f"Warning: '{var}' does not exist, defaulting to 0")
            self.variables[var] = 0
        elif self.variables[var] == 0:
            Report.message(1, f"Warning: integers cannot go below zero, defaulting '{var}' 0")
        else:
            self.variables[var] -= 1

    def operation(self, arg1, arg2, arg3, operator, line, line_num):
        output = 0
        arguments = [arg2, arg3]
        for i in range(len(arguments)):
            try:
                arguments[i] = int(arguments[i])
            except ValueError:
                if not self.check_exists(arguments[i]): #Checks if variable exists
                    Report.raise_error(line, len(line), line_num, expected=arguments[i], version=3)
                    self.variables[arguments[i]] = 0
                arguments[i] = self.variables[arguments[i]]
        match operator:
            case '+':
                self.variables[arg1] = arguments[0] + arguments[1]
            case '-':
                self.variables[arg1] = arguments[0] - arguments[1]
            case '*':
                self.variables[arg1] = arguments[0] * arguments[1]
            case '/':
                self.variables[arg1] = arguments[0] / arguments[1]
            case _:
                Report.raise_error(line, line.find(operator), line_num, invalid_message="invalid operator", version=5)



    def condition(self, arg1, arg2, operator, line_num, line): #Check validity of condition inputs and confirm outcome of operation
        try:
            arg1 = int(arg1)
        except ValueError:
            #Report.raise_error(line, line.find(arg1), line_num, , version=5)
            if not self.check_exists(arg1):
                Report.raise_error(line, len(line), line_num, expected=arg1, version=3)
                self.variables[arg1] = 0
            arg1 = self.variables[arg1]
        try:
            arg2 = int(arg2)
        except ValueError:
            if not self.check_exists(arg2):
                Report.raise_error(line, len(line), line_num, expected=arg2, version=3)
                self.variables[arg2] = 0
            arg2 = self.variables[arg2]
        if operator == 'not':
            return arg1 != arg2
        elif operator == 'is':
            return arg1 == arg2
        elif operator == '<':
            return arg1 < arg2
        elif operator == '>':
            return arg1 > arg2
        Report.raise_error(line, line.find(operator), line_num, invalid_message=f" unrecognised operator '{operator}'", version=5)


    def while_loop(self, line_num, line, line_complete): #Check if loop satisfies condition and push the line number to the stack if it does
        loop = self.condition(line[1],line[3], line[2], line_num, line_complete)
        if loop:
            self.while_stack.push(line_num)
        return loop


    def interpret_line(self, line_complete, line_num): #Interpret a single line
        line = self.formatted_lines[line_num]
        if not self.skip:
            if line[0] == 'clear' or line[0] == 'incr' or line[0] == 'decr':
                if len(line) == 1: #Raise an error if no argument is provided
                    Report.raise_error(line_complete, len(line[0])+1, line_num, version=1, arg_required=1, arg_given=0)
                elif len(line) > 2: #Raise an error if more than 1 argument is provided
                    Report.raise_error(line_complete, len(line[0])+1, line_num, version=1, arg_required=1, arg_given=len(line)-1)
                else:
                    match line[0]:
                        case 'clear':
                            self.clear(line[1])
                        case 'incr':
                            self.incr(line[1])
                        case 'decr':
                            self.decr(line[1])
            elif line[0] == 'while':
                if len(line) == 5:
                    if line[4] == 'do':
                        if not self.while_loop(line_num, line, line_complete): #If the while loop condition is checked and found to be false, all subsequent lines up to the next 'end;' should be skipped
                            self.skip = True
                    else:
                        Report.raise_error(line_complete,len(line_complete), line_num,'do')
                else:
                    Report.raise_error(line_complete, len(line_complete), line_num, version=2)
            elif line[0] == 'end':
                if len(line) > 1 or self.while_stack.get_size() == 0:
                    Report.raise_error(line_complete, 4, line_num, version=2)
                else:
                    last_while = self.while_stack.pop()
                    if self.while_loop(last_while, self.formatted_lines[last_while], lines[last_while]):
                        return last_while
            elif len(line) == 5 and line[1] == '=': #if line has 5 items and the 2nd item is '='
                self.operation(line[0], line[2], line[4], line[3], line_complete, line_num)
            elif line[0] != '#':
                Report.raise_error(line_complete, len(line_complete), line_num, version=5) #In any other case (unhandled) use generic error message
        else:
            if line[0] == 'end':
                if len(line) > 1:
                    Report.raise_error(line_complete, 4, line_num, version=2)
                else:
                    self.skip = False
        self.output_variables(line_num+1)
        return line_num


    def validate_while(self, formatted_lines, virgin_lines): #Validate the while loops have an 'end' and that there aren't too many 'end'
        while_nums = 0
        line_index = 0
        for line in formatted_lines:
            match line[0]:
                case 'while':
                    while_nums += 1
                case 'end':
                    while_nums -= 1
                    if while_nums < 0:
                        Report.raise_error(virgin_lines[line_index], 3, line_index, expected='end', version=4)
            line_index += 1
        if while_nums > 0:
            Report.raise_error(virgin_lines[line_index-1], len(virgin_lines[line_index-1]), line_index-1, expected='end', version=0)


if __name__ == '__main__':
    lines = []
    line = ''

    line_num = 1
    hashing = False
    hash_pos = 0
    pos = 0
    for character in open('input.txt','r').read(): #Format the text file removing ';' and unnecessary whitespaces
        if hashing and character != '\n':
            continue
        elif character == '\n':
            if line != '' and len(line.strip()) > 0 and line[len(line)-1] != ';': #Checks for ';' after instructions, allows for whitespaces after ';'
                Report.raise_error(line.strip(), len(line.strip()), line_num-1, expected=';')
            line_num += 1
            pos = 0
            hashing = False
        elif character == '#':
            hashing = True
            hash_pos = pos
        elif character == ';':
            lines.append(re.sub(' +;', ';', line.strip('\n')).strip(';').strip()) #Generate a list of formated lines
            line = ''
            pos = 0
        else:
            line = line + character
            pos += 1
    if line.strip() != '':
        Report.raise_error(line.strip(), len(line.strip()), line_num-1, expected=';')
    bare_bones = Interpreter(lines, 100000)