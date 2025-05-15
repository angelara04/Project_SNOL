import re
import sys

# Global symbol table: var_name -> (value, type_str)
variables = {}

# Token specification
TOKEN_SPEC = [
    ('EXIT',    r'EXIT'),                # exit keyword
    ('BEG',     r'BEG'),                 # input keyword
    ('PRINT',   r'PRINT'),               # print keyword
    ('FLOAT',   r'-?\d+\.\d+'),          # floating-point literal
    ('INT',     r'-?\d+'),               # integer literal
    ('IDENT',   r'[A-Za-z][A-Za-z0-9]*'),# identifier
    ('OP',      r'[+\-*/%]'),            # arithmetic operators
    ('EQ',      r'='),                   # assignment operator
    ('SKIP',    r'[ \t]+'),              # skip spaces/tabs
    ('MISMATCH',r'.'),                   # any other character
]

# Compile combined regex
tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
master_pat = re.compile(tok_regex)

def print_error(msg):
    print(f"SNOL> Error! {msg}")

def tokenize(line):
    tokens = []
    pos = 0
    while pos < len(line):
        # At start of line, allow BEGvar or PRINTnum without space
        if pos == 0:
            m = re.match(r'BEG([A-Za-z][A-Za-z0-9]*)', line[pos:])
            if m:
                tokens.append(('BEG','BEG'))
                tokens.append(('IDENT', m.group(1)))
                pos += m.end()
                continue
            m2 = re.match(r'PRINT([A-Za-z][A-Za-z0-9]*)', line[pos:])
            if m2:
                tokens.append(('PRINT','PRINT'))
                tokens.append(('IDENT', m2.group(1)))
                pos += m2.end()
                continue

        mo = master_pat.match(line, pos)
        if not mo:
            raise ValueError(f"Unknown word at position {pos}")
        kind = mo.lastgroup
        text = mo.group()
        pos = mo.end()
        if kind == 'SKIP':
            continue
        if kind == 'MISMATCH':
            raise ValueError(f"Unknown word [{text}]")
        tokens.append((kind, text))
    return tokens

def get_literal_type(text):
    if re.fullmatch(r'-?\d+', text):
        return 'int'
    if re.fullmatch(r'-?\d+\.\d+', text):
        return 'float'
    return None

def check_defined(tokens):
    for k, t in tokens:
        if k == 'IDENT' and t not in variables:
            raise NameError(f"Undefined variable [{t}]")

def evaluate_expr(tokens):
    # 1) Undefined variables
    check_defined(tokens)
    # 2) Double-ops
    for i in range(len(tokens)-1):
        if tokens[i][0]=='OP' and tokens[i+1][0]=='OP':
            raise SyntaxError(f"Invalid sequence of operators [{tokens[i][1]}{tokens[i+1][1]}]")
    # 3) Tokens between literals
    lit_idxs = [i for i,(k,_) in enumerate(tokens) if k in ('INT','FLOAT')]
    for i in range(len(lit_idxs)-1):
        a, b = lit_idxs[i], lit_idxs[i+1]
        if b - a > 1:
            for j in range(a+1, b):
                if tokens[j][0] not in ('INT','FLOAT'):
                    raise SyntaxError("Tokens between literals are not allowed")
    # Build expr string & type-check
    expr, types = '', []
    for k,t in tokens:
        if k=='IDENT':
            val,typ = variables[t]
            expr += str(val); types.append(typ)
        elif k in ('INT','FLOAT'):
            expr += t; types.append('int' if k=='INT' else 'float')
        elif k=='OP':
            expr += t
    if types:
        base = types[0]
        if any(x!=base for x in types):
            raise TypeError("Operands must be of the same type in an arithmetic operation!")
        if '%' in expr and base!='int':
            raise TypeError("Modulo operation only allowed on integer operands!")
    # Evaluate to force syntax errors, but we discard result
    try:
        _ = eval(expr)
    except Exception:
        raise SyntaxError("Invalid arithmetic expression!")
    return

def handle_assignment(tokens):
    var = tokens[0][1]
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', var) is None:
        print_error(f"Invalid variable name: [{var}]")
        return
    expr_toks = tokens[2:]
    try:
        # We re-evaluate here to get the value and type
        check_defined(expr_toks)
        # simple reuse: build expr and eval
        expr, types = '', []
        for k,t in expr_toks:
            if k=='IDENT':
                v,ty = variables[t]; expr+=str(v); types.append(ty)
            elif k in ('INT','FLOAT'):
                expr+=t; types.append('int' if k=='INT' else 'float')
            else: expr+=t
        val = eval(expr)
        typ = 'int' if all(op not in expr for op in ('/', '%')) and isinstance(val,int) else 'float'
    except Exception as e:
        print_error(str(e)); return

    variables[var] = (val, typ)
    print(f"SNOL> [{var}] = {val}")

def handle_print(tokens):
    if len(tokens)<2:
        print_error("PRINT requires an argument"); return
    arg = tokens[1][1]
    if re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', arg):
        if arg not in variables:
            print_error(f"Undefined variable [{arg}]"); return
        v,_ = variables[arg]
        print(f"SNOL> [{arg}] = {v}")
    else:
        lit_ty = get_literal_type(arg)
        if not lit_ty:
            print_error(f"Undefined variable or invalid literal: [{arg}]")
        else:
            print(f"SNOL> {arg}")

def handle_beg(tokens):
    if len(tokens)<2 or tokens[1][0]!='IDENT':
        print_error("BEG requires a variable name"); return
    var = tokens[1][1]
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*', var):
        print_error(f"Invalid variable name: [{var}]"); return
    print(f"SNOL> Please enter value for [{var}]")
    inp = input("Input: ").strip()
    lt = get_literal_type(inp)
    if lt is None:
        print_error("Invalid number format!"); return
    val = int(inp) if lt=='int' else float(inp)
    variables[var] = (val, lt)

def process(tokens):
    if not tokens:
        return True
    k0, _ = tokens[0]

    if k0=='EXIT':
        print("Interpreter is now terminated..."); return False
    if k0=='BEG'   and len(tokens)==2 and tokens[1][0]=='IDENT':
        handle_beg(tokens);   return True
    if k0=='PRINT' and len(tokens)==2:
        handle_print(tokens); return True
    if k0=='IDENT' and len(tokens)>=3 and tokens[1][0]=='EQ':
        handle_assignment(tokens); return True

    # standalone literal or var → ignore silently
    if (k0 in ('INT','FLOAT') and len(tokens)==1) or (k0=='IDENT' and len(tokens)==1):
        return True

    # otherwise treat as expression → check for syntax errors
    try:
        evaluate_expr(tokens)
    except Exception as e:
        print_error(str(e))
    return True

def main():
    print("The SNOL environment is now active, you may proceed with giving your commands.")
    while True:
        try:
            line = input("Command: ")
        except EOFError:
            break
        try:
            toks = tokenize(line)
        except ValueError as ve:
            print_error(str(ve)); continue
        if not process(toks):
            break

if __name__ == "__main__":
    main()
