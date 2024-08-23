import re

# Definição das expressões regulares para os tokens
token_specification = [
    ('KEYWORD', r'\b(class|public|static|void|if|else)\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'),
    ('NUMBER', r'\b\d+\b'),
    ('OPERATOR', r'[+\-*/=]'),
    ('DOT', r'\.'),  
    ('DELIMITER', r'[()\{\};,]'),
    ('STRING', r'\".*?\"'),
    ('COMMENT', r'//.*?$|/\*.*?\*/'),
    ('BRACKET', r'[\[\]]'), 
    ('SKIP', r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]

def tokenize(code):
    tokens = []
    line_number = 1
    token_re = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_specification)
    
    for match in re.finditer(token_re, code):
        kind = match.lastgroup
        value = match.group()
        
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} inesperado na linha {line_number}')
        else:
            tokens.append((kind, value))
        
        line_number += value.count('\n')
    
    return tokens

# Teste do analisador léxico com um arquivo Java
with open('examples/firstExample.java', 'r') as file:
    code = file.read()

tokens = tokenize(code)
for token in tokens:
    print(token)
