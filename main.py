import re
import sys

variables = {}  # Store var_name: (value, type_str) where type_str is "int" or "float"

# Utility functions

def is_valid_var_name(name):
    keywords = {"BEG", "PRINT", "EXIT!"}
    if name in keywords:
        return False
    return re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', name) is not None

def is_integer_literal(s):
    return re.fullmatch(r'-?\d+', s) is not None

def is_float_literal(s):
    return re.fullmatch(r'-?\d+\.\d+', s) is not None

def get_literal_type(s):
    if is_integer_literal(s):
        return "int"
    elif is_float_literal(s):
        return "float"
    else:
        return None

def print_error(message):
    print(f"SNOL> Error! {message}")

def prompt_input(var):
    print(f"SNOL> Please enter value for [{var}]")
    val = input("Input: ").strip()
    t = get_literal_type(val)
    if t is None:
        print_error("Invalid number format!")
        return None, None
    if t == "int":
        return int(val), "int"
    else:
        return float(val), "float"

# Expression evaluation
def tokenize_expr(expr):
    token_spec = [
        ('FLOAT', r'-?\d+\.\d+'),
        ('INT', r'-?\d+'),
        ('VAR', r'[A-Za-z][A-Za-z0-9]*'),
        ('OP', r'[\+\-\*/%]'),
        ('SKIP', r'[ \t]+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
    tokens = []
    for mo in re.finditer(tok_regex, expr):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            return None, f"Unknown word [{value}]"
        tokens.append((kind, value))
    return tokens, None

def check_defined_vars(tokens):
    for kind, value in tokens:
        if kind == 'VAR' and value not in variables:
            return value
    return None

def evaluate_expr(expr):
    tokens, err = tokenize_expr(expr)
    if err:
        return None, None, err
    undef = check_defined_vars(tokens)
    if undef:
        return None, None, f"Undefined variable [{undef}]"

    expr_py = ""
    values_types = []
    for kind, val in tokens:
        if kind == 'VAR':
            val_val, val_type = variables[val]
            expr_py += str(val_val)
            values_types.append(val_type)
        elif kind == 'INT':
            expr_py += val
            values_types.append("int")
        elif kind == 'FLOAT':
            expr_py += val
            values_types.append("float")
        elif kind == 'OP':
            expr_py += val

    # Check all operands have the same type
    if values_types:
        base_type = values_types[0]
        if any(t != base_type for t in values_types):
            return None, None, "Operands must be of the same type in an arithmetic operation!"
    else:
        base_type = None

    # If modulo used, ensure int operands
    if '%' in expr_py and base_type != "int":
        return None, None, "Modulo operation only allowed on integer operands!"

    try:
        result = eval(expr_py)
        # If operands are int and no division/modulo, keep int type
        if base_type == "int" and all(op not in expr_py for op in ['/', '%']):
            result = int(result)
            base_type = "int"
        else:
            # Division or float operands yield float
            result = float(result)
            base_type = "float"
    except Exception:
        return None, None, "Invalid arithmetic expression!"

    return result, base_type, None

def handle_assignment(input_str):
    if '=' not in input_str:
        print_error("Invalid assignment syntax!")
        return
    var, expr = input_str.split('=', 1)
    var = var.strip()
    expr = expr.strip()

    if not is_valid_var_name(var):
        print_error(f"Invalid variable name: [{var}]")
        return

    val, val_type, err = evaluate_expr(expr)
    if err:
        print_error(err)
        return

    variables[var] = (val, val_type)
    print(f"SNOL> [{var}] = {val}")

def handle_print(arg):
    arg = arg.strip()
    if is_valid_var_name(arg):
        if arg not in variables:
            print_error(f"Undefined variable [{arg}]")
            return
        val, _ = variables[arg]
        print(f"SNOL> [{arg}] = {val}")
        return
    elif get_literal_type(arg) is not None:
        print(f"SNOL> {arg}")
        return
    else:
        print_error(f"Undefined variable or invalid literal: [{arg}]")

def handle_beg(var):
    var = var.strip()
    if not is_valid_var_name(var):
        print_error(f"Invalid variable name: [{var}]")
        return

    val, val_type = prompt_input(var)
    if val_type is None:
        return
    variables[var] = (val, val_type)

def process_command(command):
    command = command.strip()
    if not command:
        return True

    if command.upper() in ["EXIT", "EXIT!"]:
        print("Interpreter is now terminated...")
        return False

    if command.startswith("BEG"):
        parts = command.split(maxsplit=1)
        if len(parts) != 2:
            print_error("Unknown command!")
            return True
        handle_beg(parts[1])
        return True

    if command.startswith("PRINT"):
        parts = command.split(maxsplit=1)
        if len(parts) != 2:
            print_error("Missing argument after PRINT")
            return True
        handle_print(parts[1])
        return True

    if '=' in command:
        handle_assignment(command)
        return True

    if is_valid_var_name(command):
        if command not in variables:
            print_error(f"Undefined variable [{command}]")
        return True

    if get_literal_type(command) is not None:
        return True

    print_error("Unknown command!")
    return True

def main():
    print("The SNOL environment is now active, you may proceed with giving your commands.")
    while True:
        try:
            cmd = input("Command: ")
        except EOFError:
            break
        cont = process_command(cmd)
        if not cont:
            break

if __name__ == "__main__":
    main()
