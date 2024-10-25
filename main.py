import os  # Importa o módulo os para manipulação de diretórios e arquivos
import re  # Importa o módulo re para expressões regulares
from tabulate import tabulate  # Importa a função tabulate para formatar tabelas
from colorama import Fore, Style  # Importa o módulo colorama para coloração de texto no terminal

def tokenize(code, symbol_table):
    tokens = []  # Lista para armazenar tokens
    line_number = 1  # Contador de linhas
    # Definição das especificações de tokens com expressões regulares
    token_specification = [
        ('KEYWORD', r'\b(?:public|class|static|void|int|float|boolean|double|char|if|else|while|for|return|switch|case|default|break|continue|synchronized|this|super)\b'),
        ('ANNOTATION', r'@\w+'),  # Anotações
        ('BOOLEAN', r'\b(?:true|false)\b'),  # Valores booleanos
        ('IDENTIFIER', r'[A-Za-z_]\w*'),  # Identificadores
        ('NUMBER', r'\b\d+(\.\d+)?\b'),  # Números inteiros e decimais
        ('CHAR', r'\'(\\.|[^\\])\''),  # Caracteres
        ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),  # Strings
        ('COMMENT', r'//.*|/\*[\s\S]*?\*/'),  # Comentários
        ('OPERATOR', r'(<|>|<=|>=|==|!=|[+*/=%\-]|&&|\|\|)'),  # Operadores
        ('DELIMITER', r'[{};,()]'),  # Delimitadores
        ('DOT', r'\.'),  # Ponto
        ('BRACKET', r'[\[\]]'),  # Colchetes
        ('SKIP', r'[ \t]+'),  # Espaços em branco
        ('NEWLINE', r'\n'),  # Quebras de linha
        ('MISMATCH', r'.')  # Erros de sintaxe
    ]

    # Combina todas as expressões regulares em uma única expressão
    token_re = '|'.join(f'(?P<{name}>{regex})' for name, regex in token_specification)
    
    # Itera sobre as correspondências encontradas no código
    for match in re.finditer(token_re, code):
        kind = match.lastgroup  # Tipo de token
        value = match.group()  # Valor do token

        if kind == 'SKIP':
            continue  # Ignora espaços em branco
        elif kind == 'NEWLINE':
            line_number += 1  # Incrementa o contador de linhas
            continue
        elif kind == 'COMMENT':
            line_number += value.count('\n')  # Incrementa por cada linha em comentários
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Erro de sintaxe: {value!r} inesperado na linha {line_number}')  # Erro de sintaxe
        else:
            token = {
                'type': kind,  # Tipo do token
                'value': value,  # Valor do token
                'line': line_number  # Linha onde o token foi encontrado
            }

            if kind == 'IDENTIFIER':  # Se o token for um identificador
                if value not in symbol_table:
                    symbol_table[value] = {
                        'count': 0,  # Contagem de ocorrências
                        'lines': []  # Lista de linhas onde aparece
                    }
                symbol_table[value]['count'] += 1  # Incrementa contagem
                if line_number not in symbol_table[value]['lines']:
                    symbol_table[value]['lines'].append(line_number)  # Adiciona linha se não estiver presente
                
                token['symbol_table_index'] = list(symbol_table.keys()).index(value)  # Adiciona índice na tabela de símbolos

            tokens.append(token)  # Adiciona o token à lista de tokens

    return tokens  # Retorna a lista de tokens

def print_tokens(tokens):
    print("Lista de Tokens:")  # Imprime título
    token_list = []  # Lista para armazenar os tokens formatados
    # Define as cores para cada tipo de token
    for token in tokens:
        color = {
            'KEYWORD': Fore.BLUE,
            'ANNOTATION': Fore.CYAN,
            'BOOLEAN': Fore.LIGHTMAGENTA_EX,
            'IDENTIFIER': Fore.GREEN,
            'NUMBER': Fore.MAGENTA,
            'CHAR': Fore.LIGHTYELLOW_EX,
            'STRING': Fore.YELLOW,
            'OPERATOR': Fore.RED,
            'DELIMITER': Fore.CYAN,
            'DOT': Fore.WHITE,
            'BRACKET': Fore.LIGHTCYAN_EX
        }.get(token['type'], Style.RESET_ALL)

        # Adiciona informações sobre o token à lista
        if token['type'] == 'IDENTIFIER':
            token_list.append([
                f"{color}{token['type']}{Style.RESET_ALL}",
                f"{color}{token['value']}{Style.RESET_ALL}",
                f"{token['line']}",
                f"{token.get('symbol_table_index', '-')}"] )
        else:
            token_list.append([
                f"{color}{token['type']}{Style.RESET_ALL}",
                f"{color}{token['value']}{Style.RESET_ALL}",
                f"{token['line']}"] )

    # Imprime a tabela formatada dos tokens
    print()
    print(tabulate(token_list, headers=["Type", "Value", "Line", "Symbol Table Ref"], tablefmt="fancy_grid"))

def print_symbol_table(symbol_table):
    print()
    print("Tabela de Símbolos:")  # Imprime título
    symbol_list = []  # Lista para armazenar informações da tabela de símbolos
    # Itera sobre a tabela de símbolos
    for i, (symbol, data) in enumerate(symbol_table.items()):
        symbol_list.append([symbol, data['count'], ", ".join(map(str, data['lines']))])  # Adiciona símbolo, contagem e linhas

    # Imprime a tabela formatada da tabela de símbolos
    print()
    print(tabulate(symbol_list, headers=["Symbol", "Occurrences", "Lines"], tablefmt="fancy_grid"))

def read_java_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()  # Retorna o conteúdo do arquivo
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")  # Mensagem de erro se o arquivo não for encontrado
        return None

def generate_markdown(tokens, symbol_table):
    output_dir = "output"  # Diretório de saída
    os.makedirs(output_dir, exist_ok=True)  # Cria o diretório se não existir

    markdown_file_path = os.path.join(output_dir, "output.md")  # Caminho do arquivo markdown
    
    # Cria e escreve no arquivo markdown
    with open(markdown_file_path, "w", encoding='utf-8') as f:
        f.write("# Análise de Código Java\n\n")  # Título do markdown

        f.write("## Lista de Tokens\n\n")  # Subtítulo para a lista de tokens
        f.write("Esta tabela contém a lista de todos os tokens encontrados no código analisado.\n\n")
        f.write("| Type | Value | Line | Symbol Table Ref |\n")
        f.write("|------|-------|------|------------------|\n")
        # Adiciona tokens à tabela no markdown
        for token in tokens:
            if token['type'] == 'IDENTIFIER':
                ref = f"{token.get('symbol_table_index', '-')}"

            else:
                ref = "-"
            f.write(f"| {token['type']} | {token['value']} | {token['line']} | {ref} |\n")

        f.write("\n## Tabela de Símbolos\n\n")  # Subtítulo para a tabela de símbolos
        f.write("Esta tabela apresenta a contagem de ocorrências e as linhas onde cada símbolo é utilizado.\n\n")
        f.write("| Symbol | Occurrences | Lines |\n")
        f.write("|--------|-------------|-------|\n")
        # Adiciona símbolos à tabela no markdown
        for symbol, data in symbol_table.items():
            f.write(f"| {symbol} | {data['count']} | {', '.join(map(str, data['lines']))} |\n")
    
    print()
    print(f"Arquivo Markdown '{markdown_file_path}' gerado com sucesso!")  # Mensagem de sucesso na geração do arquivo

if __name__ == "__main__":
    code = None  # Inicializa a variável de código como None
    while code is None:  # Laço para garantir que o código seja lido corretamente
        print()
        file_path = input("Digite o caminho do arquivo .java: ").strip()  # Solicita o caminho do arquivo
        
        if file_path:  # Verifica se o caminho não está vazio
            code = read_java_file(file_path)  # Lê o arquivo
        else:
            print()
            print("O caminho do arquivo não pode estar vazio. Por favor, insira um caminho válido.")  # Mensagem de erro

    symbol_table = {}  # Inicializa a tabela de símbolos

    tokens = tokenize(code, symbol_table)  # Tokeniza o código

    print() 
    print_tokens(tokens)  # Imprime a lista de tokens

    print()
    print_symbol_table(symbol_table)  # Imprime a tabela de símbolos

    print()
    generate_file = input("Deseja gerar um arquivo com a lista de tokens e a tabela de símbolos? (s/n): ").strip().lower()  # Pergunta ao usuário se deseja gerar arquivo
    if generate_file == 's':
        generate_markdown(tokens, symbol_table)  # Gera o arquivo markdown
