import re
import argparse

# -- Setup Arguments --
# --infile / -if: REQUIRED, the path to the input file, example: -if ./input.txt
# --outfile / -of: REQUIRED, the path to the output file, example: -of ./output.txt
# --showparsed / -sp: OPTIONAL, show the parsed code in the console, example: -sp
parser = argparse.ArgumentParser(prog="Compiler")
parser.add_argument("-if", "--infile", help="The path to the input file")
parser.add_argument("-of", "--outfile", help="The path to the output file")
parser.add_argument("-sp", "--showparsed", help="Show the parsed code in the console",
                    action=argparse.BooleanOptionalAction)
parsed_args = parser.parse_args()
if not parsed_args.infile and not parsed_args.outfile:
    raise Exception(
        "Error: No arguments specified, please specify an input file and output file with the -if and -of flags: -if <path> -of <path>")
if not parsed_args.infile:
    raise Exception("Error: No input file specified, please specify an input file with the -if flag: -if <path>")
if not parsed_args.outfile:
    raise Exception("Error: No output file specified, please specify an output file with the -of flag: -of <path>")


# Token Types (Using a class because python match-case statements
# don't support comparison against variables [for some reason], using a class somehow works)
# https://stackoverflow.com/questions/67525257/capture-makes-remaining-patterns-unreachable
class Tokens:
    IF = 'IF'
    ELSE = 'ELSE'
    OPEN_BRACE = 'OPEN_BRACE'
    CLOSE_BRACE = 'CLOSE_BRACE'
    GREATER_THAN = 'GREATER_THAN'
    LESS_THAN = 'LESS_THAN'
    GREATER_THAN_EQUAL = 'GREATER_THAN_EQUAL'
    LESS_THAN_EQUAL = 'LESS_THAN_EQUAL'
    EQUAL = 'EQUAL'
    VARIABLE_IDENTIFIER = 'VARIABLE_IDENTIFIER'
    VARIABLE_ASSIGNMENT = 'VARIABLE_ASSIGNMENT'
    WHILE = 'WHILE'
    PRINT = 'PRINT'
    LINE_COMMENT = 'LINE_COMMENT'
    OPEN_BLOCK_COMMENT = 'OPEN_BLOCK_COMMENT'
    CLOSE_BLOCK_COMMENT = 'CLOSE_BLOCK_COMMENT'
    TYPE_INT = 'TYPE_INT'
    TYPE_STRING = 'TYPE_STRING'
    TYPE_BOOL = 'TYPE_BOOLEAN'
    STRING = 'STRING'
    INT = 'INT'
    BOOL_TRUE = 'BOOL_TRUE'
    BOOL_FALSE = 'BOOL_FALSE'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'


# Token Regex Patterns, Variable Identifier is last because it is the most general
TOKEN_PATTERN_MAP = [
    (r'//', Tokens.LINE_COMMENT),
    (r'/\*', Tokens.OPEN_BLOCK_COMMENT),
    (r'\*/', Tokens.CLOSE_BLOCK_COMMENT),
    (r'provided', Tokens.IF),
    (r'contrarily', Tokens.ELSE),
    (r'commence', Tokens.OPEN_BRACE),
    (r'conclude', Tokens.CLOSE_BRACE),
    (r'corresponds', Tokens.VARIABLE_ASSIGNMENT),
    (r'supposing', Tokens.WHILE),
    (r'resultant', Tokens.PRINT),
    (r'>', Tokens.GREATER_THAN),
    (r'<', Tokens.LESS_THAN),
    (r'>=', Tokens.GREATER_THAN_EQUAL),
    (r'<=', Tokens.LESS_THAN_EQUAL),
    (r'==', Tokens.EQUAL),
    (r'\+', Tokens.PLUS),
    (r'-', Tokens.MINUS),
    (r'\*', Tokens.MULTIPLY),
    (r'/', Tokens.DIVIDE),
    (r'int', Tokens.TYPE_INT),
    (r'string', Tokens.TYPE_STRING),
    (r'bool', Tokens.TYPE_BOOL),
    (r'true', Tokens.BOOL_TRUE),
    (r'false', Tokens.BOOL_FALSE),
    (r'".+?"', Tokens.STRING),
    (r'\d+', Tokens.INT),
    (r'\w+', Tokens.VARIABLE_IDENTIFIER),
]

# Replacements to be used in the pseudocode generator, uses string templates to use with the .format() function
# to achieve desired output format for values.
TOKEN_REPLACEMENT_MAP = dict([
    (Tokens.IF, 'IF'),
    (Tokens.ELSE, 'ELSE'),
    (Tokens.OPEN_BRACE, '{'),
    (Tokens.CLOSE_BRACE, '}'),
    (Tokens.GREATER_THAN, '>'),
    (Tokens.LESS_THAN, '<'),
    (Tokens.GREATER_THAN_EQUAL, '>='),
    (Tokens.LESS_THAN_EQUAL, '<='),
    (Tokens.EQUAL, '=='),
    (Tokens.VARIABLE_IDENTIFIER, '{0}'),
    (Tokens.VARIABLE_ASSIGNMENT, ':='),
    (Tokens.WHILE, 'WHILE'),
    (Tokens.PRINT, 'PRINT'),
    (Tokens.LINE_COMMENT, '#'),
    (Tokens.OPEN_BLOCK_COMMENT, '/*'),
    (Tokens.CLOSE_BLOCK_COMMENT, '*/'),
    (Tokens.TYPE_INT, 'int var'),
    (Tokens.TYPE_STRING, 'string var'),
    (Tokens.TYPE_BOOL, 'bool var'),
    (Tokens.STRING, '{0}'),
    (Tokens.INT, '{0}'),
    (Tokens.BOOL_TRUE, 'true'),
    (Tokens.BOOL_FALSE, 'false'),
    (Tokens.PLUS, '+'),
    (Tokens.MINUS, '-'),
    (Tokens.MULTIPLY, '*'),
    (Tokens.DIVIDE, '/'),
])


# Load file (using path from -if arg) and return file as string with newlines and tabs stripped
def load_in_code_file(args):
    array = []
    with open(args.infile) as file:
        for line in file.readlines():
            array.append(line.strip('\n\t'))
    return " ".join(array)


# Load parser table and return terminals, non-terminals, and parse table
def load_in_parser_table():
    terminals = []
    non_terminals = []
    parse_table = []
    with open("parse_table.csv") as file:  # CSV IS REQUIRED TO BE IN THE SAME DIRECTORY AS THE PARSER
        for line in file.readlines():
            items = line.strip('\n').split(',')
            if not terminals:
                terminals = items[1:]  # Collect terminals from column headers (without first column as it is empty)
            else:
                non_terminals.append(items[0])  # Collect non-terminals from first column of each row
                parse_table.append(items[1:])
    return terminals, non_terminals, parse_table


# Load pseudocode output into file (using path from -of arg)
def create_output_file(output, args):
    with open(args.outfile, "w") as file:
        file.write(output)


# Take string input (from load_in_code_file()) and return tokens
def tokenizer(string_input):
    tokens = []
    current_index = 0

    while current_index < len(string_input):  # Loop until end of string
        match = None

        for token_pattern, token_type in TOKEN_PATTERN_MAP:  # Check each token pattern
            pattern = re.compile(token_pattern)
            match = pattern.match(string_input, current_index)

            if match:
                tokens.append((token_type, match.group()))  # Add token and matched value to tokens list
                break

        if match:
            current_index += match.end() - match.start()  # Increment index by length of matched value
        else:
            current_index += 1

    return tokens


# Take Tokens (from tokenizer()) and parse
def parser(tokens):
    parsed_tokens = []

    terminals, non_terminals, parse_table = load_in_parser_table()  # Get values from loaded parse table

    token_index = 0
    stack = ['<statement>']

    while True:
        # Load a new statement if the current statement has been parsed and there are more tokens to parse
        if token_index + 1 < len(tokens):
            if tokens[token_index + 1] and not stack:
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

            # duct tape fix because I couldn't get the else clause to work properly (not sure what I did wrong,
            # please let me know in my feedback)
            if top == '<else-clause>':
                if tokens[token_index + 1][0] == Tokens.OPEN_BRACE:
                    production_rule = 18

            # Use a switch statement to determine which production rule to use (helps with readability)
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
                    stack.extend(['<arithmetic-statement>', 'VARIABLE_ASSIGNMENT', '<variable-name>'])
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
            parsed_tokens.append(current_token)  # if token is terminal matching top of stack, add to parsed tokens
            stack.pop()
            token_index += 1

            if token_index >= len(tokens) and not stack:  # if stack is empty and no more tokens, parsing is complete
                print("Successfully Parsed Tokens")
                return parsed_tokens


# Take Tokens (from tokenizer()) and pass through Semantic Analyzer
def semantic_analyzer(parsed_tokens):
    for i in range(len(parsed_tokens)):  # iterate through tokens
        match parsed_tokens[i]:  # use switch statement to determine which token is being analyzed
            case 'TYPE_STRING':
                if parsed_tokens[i + 3] != 'STRING':
                    raise Exception("Semantic Error: STRING Type Not Assigned to STRING Value")
            case 'TYPE_INT':
                if parsed_tokens[i + 3] != 'INT':
                    raise Exception("Semantic Error: INT Type Not Assigned to INT Value")
            case 'TYPE_BOOLEAN':
                if parsed_tokens[i + 3] != 'BOOL_TRUE' and parsed_tokens[i + 3] != 'BOOL_FALSE':
                    raise Exception("Semantic Error: BOOLEAN Type Not Assigned to BOOLEAN Value")
            case _:
                pass


# Generate Output from Tokens (from tokenizer())
def generate_output(tokens):
    output = []

    comment_skip = 0
    for i in range(len(tokens)):
        token, value = tokens[i]

        # If token is a comment, skip it and the related tokens
        if token == 'LINE_COMMENT':
            comment_skip = 1
            continue
        elif token == 'OPEN_BLOCK_COMMENT':
            comment_skip = 2
            continue

        if comment_skip > 0:
            comment_skip -= 1
            continue

        # Add token to output, including value if applicable (Try Except as the OPEN_BRACE and CLOSE_BRACE tokens cause
        # ValueErrors when trying to format them due to the curly braces being used for formatting)
        try:
            output.append(TOKEN_REPLACEMENT_MAP[token].format(str(value)))
        except ValueError:
            output.append(TOKEN_REPLACEMENT_MAP[token])

    return " ".join(output)  # return output as a string


# Main Function (Each step has its own error handling so the program will stop at the first error)
def __main__():
    file_input_string = load_in_code_file(parsed_args)
    tokens = tokenizer(file_input_string)
    parsed_tokens = parser(tokens)
    print("\n".join(parsed_tokens)) if parsed_args.showparsed is True else None  # print parsed tokens if flag is set
    semantic_analyzer(parsed_tokens)
    output = generate_output(tokens)
    create_output_file(output, parsed_args)


__main__()  # Run Main Function
