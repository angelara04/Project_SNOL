import re

MAX = 100
variables = {}

# Trim leading and trailing whitespace
def trim_whitespace(s):
    return s.strip()

# Print error messages
def print_error(message):
    print(f"SNOL ERROR: {message}")

# Check if input has assignment
def is_assignment(input_str):
    return '=' in input_str

# Command parser and dispatcher
def parse_command(input_str):
    input_str = input_str.strip()

    if is_assignment(input_str):
        handle_assignment_command(input_str)
        return 1

    if input_str == "EXIT!":
        return -1

    if input_str.startswith("PRINT"):
        arg = input_str[5:].strip()
        if not arg:
            print_error("Missing argument after PRINT")
            return 0
        handle_print_command(arg)
        return 1

    if input_str.startswith("BEG"):
        arg = input_str[3:].strip()
        if not arg:
            print_error("Missing variable name after BEG")
            return 0
        handle_beg_command(arg)
        return 1

    return 0  # Unknown command

# Handler for PRINT
def handle_print_command(var):
    print(f"PRINT called with variable/literal: {var}")
    if var in variables:
        print(f"{var} = {variables[var]}")
    else:
        try:
            # Try to interpret as a number
            print(float(var))
        except ValueError:
            print_error(f"Undefined variable or invalid literal: {var}")

# Handler for BEG
def handle_beg_command(var):
    if not var.isidentifier():
        print_error(f"Invalid variable name: {var}")
        return
    value = input(f"Enter value for {var}: ").strip()
    try:
        variables[var] = float(value)
        print(f"Variable {var} initialized with value {value}")
    except ValueError:
        print_error("Invalid value, please enter a number")

# Handler for assignment
def handle_assignment_command(input_str):
    print(f"ASSIGNMENT detected: {input_str}")
    try:
        var, expr = input_str.split('=', 1)
        var = var.strip()
        expr = expr.strip()

        if not var.isidentifier():
            print_error(f"Invalid variable name: {var}")
            return

        # Replace variable names in the expression with their values
        tokens = re.findall(r'[A-Za-z_]\w*|\d+\.?\d*|[+\-*/()]', expr)
        evaluated_expr = ''
        for token in tokens:
            if token.isidentifier():
                if token in variables:
                    evaluated_expr += str(variables[token])
                else:
                    print_error(f"Undefined variable: {token}")
                    return
            else:
                evaluated_expr += token

        value = eval(evaluated_expr)
        variables[var] = value
        print(f"{var} = {value}")

    except Exception as e:
        print_error(f"Assignment error: {e}")

# Main interpreter loop
def main():
    print("The SNOL environment is now active, you may proceed with giving your commands.")

    while True:
        try:
            input_str = input("Command: ")[:MAX]
        except EOFError:
            break

        input_str = trim_whitespace(input_str)
        if not input_str:
            continue

        result = parse_command(input_str)
        if result == -1:
            print("Exiting SNOL interpreter...")
            break
        elif result == 0:
            print_error("Invalid or unknown command")

if __name__ == "__main__":
    main()
