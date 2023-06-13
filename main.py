import re
import argparse

# Setup Arguments
parser = argparse.ArgumentParser(prog="Compiler")
parser.add_argument("filepath", help="The path to the file to be compiled")
parsed_args = parser.parse_args()

# Token Types
TOKEN_IF = 'IF'
TOKEN_ELSE = 'ELSE'
TOKEN_OPEN_BRACE = 'OPEN_BRACE'
TOKEN_CLOSE_BRACE = 'CLOSE_BRACE'
TOKEN_GREATER_THAN = 'GREATER_THAN'
TOKEN_LESS_THAN = 'LESS_THAN'
TOKEN_GREATER_THAN_EQUAL = 'GREATER_THAN_EQUAL'
TOKEN_LESS_THAN_EQUAL = 'LESS_THAN_EQUAL'
TOKEN_EQUAL = 'EQUAL'
TOKEN_VARIABLE_IDENTIFIER = 'VARIABLE_IDENTIFIER'
TOKEN_VARIABLE_ASSIGNMENT = 'VARIABLE_ASSIGNMENT'
TOKEN_WHILE = 'WHILE'
TOKEN_PRINT = 'PRINT'
TOKEN_LINE_COMMENT = 'LINE_COMMENT'
TOKEN_OPEN_BLOCK_COMMENT = 'OPEN_BLOCK_COMMENT'
TOKEN_CLOSE_BLOCK_COMMENT = 'CLOSE_BLOCK_COMMENT'
TOKEN_TYPE_INT = 'TYPE_INT'
TOKEN_TYPE_STRING = 'TYPE_STRING'
TOKEN_TYPE_BOOL = 'TYPE_BOOL'
TOKEN_STRING = 'STRING'
TOKEN_INT = 'INT'
TOKEN_BOOL_TRUE = 'BOOL_TRUE'
TOKEN_BOOL_FALSE = 'BOOL_FALSE'
TOKEN_ARITH_PLUS = 'PLUS'
TOKEN_ARITH_MINUS = 'MINUS'
TOKEN_ARITH_MULTIPLY = 'MULTIPLY'
TOKEN_ARITH_DIVIDE = 'DIVIDE'

# Token Patterns
TOKEN_PATTERNS = [
    (r'//', TOKEN_LINE_COMMENT),
    (r'/\*', TOKEN_OPEN_BLOCK_COMMENT),
    (r'\*/', TOKEN_CLOSE_BLOCK_COMMENT),
    (r'provided', TOKEN_IF),
    (r'contrarily', TOKEN_ELSE),
    (r'commence', TOKEN_OPEN_BRACE),
    (r'conclude', TOKEN_CLOSE_BRACE),
    (r'corresponds', TOKEN_VARIABLE_ASSIGNMENT),
    (r'supposing', TOKEN_WHILE),
    (r'resultant', TOKEN_PRINT),
    (r'>', TOKEN_GREATER_THAN),
    (r'<', TOKEN_LESS_THAN),
    (r'>=', TOKEN_GREATER_THAN_EQUAL),
    (r'<=', TOKEN_LESS_THAN_EQUAL),
    (r'==', TOKEN_EQUAL),
    (r'\+', TOKEN_ARITH_PLUS),
    (r'-', TOKEN_ARITH_MINUS),
    (r'\*', TOKEN_ARITH_MULTIPLY),
    (r'/', TOKEN_ARITH_DIVIDE),
    (r'int', TOKEN_TYPE_INT),
    (r'string', TOKEN_TYPE_STRING),
    (r'bool', TOKEN_TYPE_BOOL),
    (r'true', TOKEN_BOOL_TRUE),
    (r'false', TOKEN_BOOL_FALSE),
    (r'".+?"', TOKEN_STRING),
    (r'\d+', TOKEN_INT),
    (r'\w+', TOKEN_VARIABLE_IDENTIFIER),
]


# Load file and return string
def load_in_code_file(args):
    array = []
    with open(args.filepath) as file:
        for line in file.readlines():
            array.append(line.strip('\n\t'))
    return " ".join(array)


# Load parser table and return dictionary
def load_in_parser_table():
    terminals = []
    non_terminals = []
    parse_table = []
    with open("parse_table.csv") as file:
        for line in file.readlines():
            items = line.strip('\n').split(',')
            if not terminals:
                terminals = items[1:]
            else:
                non_terminals.append(items[0])
                parse_table.append(items[1:])
    return terminals, non_terminals, parse_table


# Take string input and return tokens
def tokenizer(string_input):
    tokens = []
    current_index = 0

    while current_index < len(string_input):
        match = None

        for token_pattern, token_type in TOKEN_PATTERNS:
            pattern = re.compile(token_pattern)
            match = pattern.match(string_input, current_index)

            if match:
                tokens.append((token_type, match.group()))
                break

        if match:
            current_index += match.end() - match.start()
        else:
            current_index += 1

    return tokens


# Take Tokens and parse
def parser(tokens):
    parsed_tokens = []

    terminals, non_terminals, parse_table = load_in_parser_table()

    token_index = 0
    stack = ['<statement>']

    while True:
        if token_index + 1 < len(tokens):
            if tokens[token_index+1] and not stack:
                stack.extend(['<statement>'])
        top = stack[-1]
        current_token = tokens[token_index][0]

        if top in non_terminals:
            row_index = non_terminals.index(top)
            column_index = terminals.index(current_token)

            production_rule = parse_table[row_index][column_index]
            if not production_rule:
                raise Exception("Error: Invalid Token: " + current_token)
            stack.pop()

            # duct tape fix because I couldn't get the else clause to work properly
            if top == '<else-clause>':
                if tokens[token_index + 1][0] == TOKEN_OPEN_BRACE:
                    production_rule = 18

            match int(production_rule):
                case 1:
                    stack.extend(['<variable-statement>'])
                case 2:
                    stack.extend(['<if-statement>'])
                case 3:
                    stack.extend(['<loop-statement>'])
                case 4:
                    stack.extend(['<print-statement>'])
                case 5:
                    stack.extend(['<comment>'])
                case 6:
                    stack.extend(['<variable-creation>'])
                case 7:
                    stack.extend(['<variable-reassignment>'])
                case 8:
                    stack.extend(['<variable-name>', '<type>'])
                case 9:
                    stack.extend(['<assignment>', '<variable-name>', '<type>'])
                case 10:
                    stack.extend(['<assignment>', '<variable-name>'])
                case 11:
                    stack.extend(['<arithmetic-statement>', '<variable-name>'])
                case 12:
                    stack.extend(['<value>', 'VARIABLE_ASSIGNMENT'])
                case 13:
                    stack.extend(
                        ['<else-clause>', 'CLOSE_BRACE', '<statement>', 'OPEN_BRACE', '<comparison-expression>', 'IF'])
                case 14:
                    stack.extend(['<else-if-statement>'])
                case 15:
                    stack.extend(['<else-statement>'])
                case 16:
                    stack.extend(['conclude'])
                case 17:
                    stack.extend(['<if-statement>', 'ELSE'])
                case 18:
                    stack.extend(['CLOSE_BRACE', '<statement>', 'OPEN_BRACE', 'ELSE'])
                case 19:
                    stack.extend(['<while-statement>'])
                case 20:
                    stack.extend(['<do-while-statement>'])
                case 21:
                    stack.extend(['CLOSE_BRACE', '<statement>', 'OPEN_BRACE', '<comparison-expression>', 'WHILE'])
                case 22:
                    stack.extend(['<comparison-expression>', 'WHILE', 'CLOSE_BRACE', '<statement>', 'OPEN_BRACE'])
                case 23:
                    stack.extend(['<print-value>', 'PRINT'])
                case 24:
                    stack.extend(['<variable-name>'])
                case 25:
                    stack.extend(['<value>'])
                case 26:
                    stack.extend(['<line-comment>'])
                case 27:
                    stack.extend(['<block-comment>'])
                case 28:
                    stack.extend(['<string>', 'LINE_COMMENT'])
                case 29:
                    stack.extend(['CLOSE_BLOCK_COMMENT', '<string>', 'OPEN_BLOCK_COMMENT'])
                case 30:
                    stack.extend(['<arithmetic-value>', '<arithmetic-operator>', '<arithmetic-value>'])
                case 31:
                    stack.extend(['<arithmetic-statement>'])
                case 32:
                    stack.extend(['<int>'])
                case 33:
                    stack.extend(['<variable-name>'])
                case 34:
                    stack.extend(['PLUS'])
                case 35:
                    stack.extend(['MINUS'])
                case 36:
                    stack.extend(['MULTIPLY'])
                case 37:
                    stack.extend(['DIVIDE'])
                case 38:
                    stack.extend(['<comparison-value>', '<comparison-operator>', '<comparison-value>'])
                case 39:
                    stack.extend(['<value>'])
                case 40:
                    stack.extend(['<variable-name>'])
                case 41:
                    stack.extend(['LESS_THAN'])
                case 42:
                    stack.extend(['LESS_THAN_EQUAL'])
                case 43:
                    stack.extend(['EQUAL'])
                case 44:
                    stack.extend(['GREATER_THAN_EQUAL'])
                case 45:
                    stack.extend(['GREATER_THAN'])
                case 46:
                    stack.extend(['TYPE_STRING'])
                case 47:
                    stack.extend(['TYPE_INT'])
                case 48:
                    stack.extend(['TYPE_BOOLEAN'])
                case 49:
                    stack.extend(['VARIABLE_IDENTIFIER'])
                case 50:
                    stack.extend(['<string>'])
                case 51:
                    stack.extend(['<int>'])
                case 52:
                    stack.extend(['<boolean>'])
                case 53:
                    stack.extend(['STRING'])
                case 54:
                    stack.extend(['INT'])
                case 55:
                    stack.extend(['BOOL_TRUE'])
                case 56:
                    stack.extend(['BOOL_FALSE'])
                case _:
                    raise Exception("Production Rule Not Found: " + production_rule)

        elif top == current_token:
            parsed_tokens.append(current_token)
            stack.pop()
            token_index += 1

            if token_index >= len(tokens) and not stack:
                print("Successfully Parsed Tokens")
                return parsed_tokens
            # elif token_index >= len(tokens) and stack:
            #     print("Error: Failed to Parse Tokens")
            #     return False


# Main Function
def __main__():
    file_input_string = load_in_code_file(parsed_args)
    tokens = tokenizer(file_input_string)
    parsed_tokens = parser(tokens)
    print(parsed_tokens)


__main__()
