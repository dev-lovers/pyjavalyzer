import re
from tabulate import tabulate
from colorama import Fore, Style

# Função de Tokenização
def tokenize(code, symbol_table):
    tokens = []
    line_number = 1
    # Definição das expressões regulares dos tokens
    token_specification = [
        ('KEYWORD', r'\b(?:public|class|static|void|int|float|boolean)\b'),
        ('IDENTIFIER', r'[A-Za-z_]\w*'),
        ('NUMBER', r'\b\d+\b'),
        ('OPERATOR', r'(<|>|<=|>=|==|!=|[+*/=%-])'),
        ('DELIMITER', r'[{};,()]'),
        ('DOT', r'\.'),
        ('BRACKET', r'[\[\]]'),
        ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),
        ('SKIP', r'[ \t\n]+'),
        ('MISMATCH', r'.')
    ]
    
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
            token = {
                'type': kind,
                'value': value,
                'line': line_number
            }

            if kind == 'IDENTIFIER':
                # Verifica se o identificador já existe na tabela de símbolos
                if value not in symbol_table:
                    symbol_table[value] = {
                        'count': 0,
                        'lines': []
                    }
                symbol_table[value]['count'] += 1
                if line_number not in symbol_table[value]['lines']:
                    symbol_table[value]['lines'].append(line_number)
                
                # Adiciona referência ao token, apontando para o índice na tabela de símbolos
                token['symbol_table_index'] = list(symbol_table.keys()).index(value)
            
            tokens.append(token)
        
        line_number += value.count('\n')
    
    return tokens

# Função para imprimir a lista de tokens
def print_tokens(tokens):
    print("Lista de Tokens:")
    token_list = []
    for token in tokens:
        color = {
            'KEYWORD': Fore.BLUE,
            'IDENTIFIER': Fore.GREEN,
            'NUMBER': Fore.MAGENTA,
            'OPERATOR': Fore.RED,
            'DELIMITER': Fore.CYAN,
            'DOT': Fore.WHITE,
            'BRACKET': Fore.LIGHTCYAN_EX,
            'STRING': Fore.YELLOW
        }.get(token['type'], Style.RESET_ALL)

        if token['type'] == 'IDENTIFIER':
            token_list.append([
                f"{color}{token['type']}{Style.RESET_ALL}",
                f"{color}{token['value']}{Style.RESET_ALL}",
                f"{token['line']}",
                f"{token.get('symbol_table_index', '-')}"  # Mostra a referência para a tabela de símbolos
            ])
        else:
            token_list.append([
                f"{color}{token['type']}{Style.RESET_ALL}",
                f"{color}{token['value']}{Style.RESET_ALL}",
                f"{token['line']}"
            ])

    print(tabulate(token_list, headers=["Type", "Value", "Line", "Symbol Table Ref"], tablefmt="fancy_grid"))

# Função para imprimir a tabela de símbolos
def print_symbol_table(symbol_table):
    print("\nTabela de Símbolos:")
    symbol_list = []
    for i, (symbol, data) in enumerate(symbol_table.items()):
        symbol_list.append([symbol, data['count'], ", ".join(map(str, data['lines']))])

    print(tabulate(symbol_list, headers=["Symbol", "Occurrences", "Lines"], tablefmt="fancy_grid"))

# Função para ler arquivo .java
def read_java_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        return None
    
if __name__ == "__main__":
    # Solicita o caminho do arquivo Java
    file_path = input("Digite o caminho do arquivo .java: ")
    
    # Lê o arquivo .java
    code = read_java_file(file_path)
    
    if code is not None:
        # Inicializa a tabela de símbolos
        symbol_table = {}

        # Realiza a tokenização
        tokens = tokenize(code, symbol_table)

        # Imprime os tokens e a tabela de símbolos
        print_tokens(tokens)
        print_symbol_table(symbol_table)
