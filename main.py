#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Program Description:

#     • Name and student number of the program developers
#         – Angel Grace P. Arapoc   2023‑01741
#         – Richelle De Arce        2023‑15674
#         – Maron Christofer E. Morgia 2023‑60114
#         – Yldevier John A. Magpusao   2023‑60173
#     • Dates covered for the program development: May 11 - May 16
#
#   Workload breakdown:
#     • Angel: REPL loop & tokenizer design
#     • Richelle: BEG/PRINT commands & I/O handling 
#     • Maron: expression evaluator & error checking
#     • Yldevier: project write‑up & overall integration
#

import re
import sys

# Global symbol table: var_name -> (value, type_str)
variables = {}

# TOKEN_SPEC defines all token types and their regex patterns for SNOL
TOKEN_SPEC = [
    ('EXIT',    r'EXIT!'),              # exit keyword
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

# Compile the combined regex pattern from TOKEN_SPEC
tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
master_pat = re.compile(tok_regex)

# print_error: outputs error messages consistently prefixed with 'SNOL>'
def print_error(msg):
    print(f"SNOL> Error! {msg}")

# tokenize: splits a line of input into tokens based on TOKEN_SPEC
# supports shorthand BEGvar and PRINTvar at start-of-line
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

# get_literal_type: identifies if a text is an INT or FLOAT literal, else None
def get_literal_type(text):
    if re.fullmatch(r'-?\d+', text):
        return 'int'
    if re.fullmatch(r'-?\d+\.\d+', text):
        return 'float'
    return None

# check_defined: ensures all IDENT tokens refer to defined variables
# raises NameError for any undefined identifier
def check_defined(tokens):
    for k, t in tokens:
        if k == 'IDENT' and t not in variables:
            raise NameError(f"Unknown command! Does not match any valid command of the language. ")

# evaluate_expr: syntax & type checks on arithmetic expressions
# checks undefined vars, double-ops, tokens between literals, type consistency
# uses eval() to catch invalid syntax but discards the result
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
        if any(x != types[0] for x in types):
            raise TypeError("Operands must be of the same type in an arithmetic operation!")
        if '%' in expr:
            if any(t != 'int' for t in types):
                raise TypeError("Modulo operation only allowed on integer operands!")

    # Evaluate to force syntax errors, but we discard result
    try:
        _ = eval(expr)
    except Exception:
        raise SyntaxError("Invalid arithmetic expression!")
    return
# handle_assignment: processes "var = expr" statements
# evaluates expr, updates variables dict, prints the new value
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
                # Extra type check for modulo usage
        if any(x != types[0] for x in types):
            raise TypeError("Operands must be of the same type in an arithmetic operation!")

        if '%' in expr and any(t != 'int' for t in types):
            raise TypeError("Modulo operation only allowed on integer operands!")

        val = eval(expr)
        typ = 'int' if all(op not in expr for op in ('/', '%')) and isinstance(val,int) else 'float'

    except Exception as e:
        print_error(str(e)); return

    variables[var] = (val, typ)
    print(f"SNOL> [{var}] = {val}")

# handle_print: processes "PRINT x" commands
# if x is a variable, prints its value; if a literal, echoes it
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
# handle_beg: processes "BEG x" commands
# prompts user for input, validates number format, stores it
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

# process: main dispatcher for a single line of tokens
# routes to exit, beg, print, assignment, or expression-check
# returns False to break the REPL on EXIT
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

# main: REPL loop, reads lines, tokenizes, processes until EXIT
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
