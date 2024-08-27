import re
from collections import defaultdict
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

# Definição das expressões regulares para os tokens
token_specification = [
    ('KEYWORD', r'\b(class|public|static|void|if|else|int|float|return|for|while)\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'),
    ('NUMBER', r'\b\d+\b'),
    ('OPERATOR', r'[\+\-*/%&|<>=!]+'),
    ('ASSIGNMENT', r'='),
    ('DELIMITER', r'[()\{\};,]'),
    ('DOT', r'\.'),
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
            line_number += value.count('\n')
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'{value!r} inesperado na linha {line_number}')
        else:
            tokens.append({
                'type': kind,
                'value': value,
                'line': line_number
            })

        line_number += value.count('\n')
    
    return tokens

def build_symbol_table(tokens):
    symbol_table = defaultdict(lambda: {'count': 0, 'lines': []})
    
    for token in tokens:
        if token['type'] == 'IDENTIFIER':
            symbol_info = symbol_table[token['value']]
            symbol_info['count'] += 1
            if token['line'] not in symbol_info['lines']:
                symbol_info['lines'].append(token['line'])
    
    # Convertendo o defaultdict para um dicionário comum, ordenando as chaves
    sorted_symbols = dict(sorted(symbol_table.items()))
    
    return sorted_symbols

def print_tokens(tokens):
    print("Lista de Tokens:")
    token_list = []
    for token in tokens:
        color = {
            'KEYWORD': Fore.BLUE,
            'IDENTIFIER': Fore.GREEN,
            'NUMBER': Fore.MAGENTA,
            'OPERATOR': Fore.RED,
            'ASSIGNMENT': Fore.YELLOW,
            'DELIMITER': Fore.CYAN,
            'DOT': Fore.WHITE,
            'STRING': Fore.LIGHTMAGENTA_EX,
            'COMMENT': Fore.LIGHTBLACK_EX,
            'BRACKET': Fore.LIGHTCYAN_EX
        }.get(token['type'], Style.RESET_ALL)
        
        token_list.append([
            f"{color}{token['type']}{Style.RESET_ALL}",
            f"{color}{token['value']}{Style.RESET_ALL}",
            f"{token['line']}"
        ])
    
    print(tabulate(token_list, headers=["Type", "Value", "Line"], tablefmt="fancy_grid"))

def print_symbol_table(symbol_table):
    print("\nTabela de Símbolos:")
    symbol_list = []
    for symbol, info in symbol_table.items():
        symbol_list.append([
            symbol,
            info['count'],
            ', '.join(map(str, info['lines']))
        ])
    
    print(tabulate(symbol_list, headers=["Symbol", "Occurrences", "Lines"], tablefmt="fancy_grid"))

# Lendo o conteúdo de um arquivo Java para análise léxica
with open('examples/complexExample.java', 'r') as file:
    code = file.read()

tokens = tokenize(code)
symbol_table = build_symbol_table(tokens)

print_tokens(tokens)
print_symbol_table(symbol_table)
