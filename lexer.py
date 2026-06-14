"""
A lexer (short for lexical analyzer or tokenizer) 
is a program or function that takes
raw text (like source code) and breaks it down
into a stream of meaningful, categorized pieces called tokens
"""
import re #regex pattern to recognize keywords...

class Token: #A token is one piece of JavaScript.
    def __init__(self, type_, value, line, column):#types of tokens...
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):#Controls printing.
        return f"Token({self.type}, {repr(self.value)}, Line: {self.line}, Col: {self.column})"

# Keywords set
KEYWORDS = {
    'let', 'const', 'var', 'function', 'return', 'if', 'else', 
    'for', 'while', 'do', 'switch', 'case', 'default', 'break', 
    'continue', 'true', 'false', 'null', 'undefined', 'new'
}

# Token specification
TOKEN_SPEC = [
    # Comments & whitespace
    ('COMMENT_LINE',  r'//.*'),
    ('COMMENT_MULTI', r'/\*[\s\S]*?\*/'),
    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t\r]+'),

    # Multi-character operators
    ('EQ_STRICT', r'==='),
    ('NE_STRICT', r'!=='),
    ('EQ_LOOSE',  r'=='),
    ('NE_LOOSE',  r'!='),
    ('ARROW',     r'=>'),
    ('INC',       r'\+\+'),
    ('DEC',       r'--'),
    ('ADD_ASSIGN',r'\+='),
    ('SUB_ASSIGN',r'-='),
    ('EXP',       r'\*\*'),
    ('LE',        r'<='),
    ('GE',        r'>='),
    ('SPREAD',    r'\.\.\.'),
    
    # Single-character operators/symbols
    ('LT',        r'<'),
    ('GT',        r'>'),
    ('ASSIGN',    r'='),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('MUL',       r'\*'),
    ('DIV',       r'/'),
    ('MOD',       r'%'),
    ('AND',       r'&&'),
    ('OR',        r'\|\|'),
    ('NOT',       r'!'),
    
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),
    ('LBRACKET',  r'\['),
    ('RBRACKET',  r'\]'),
    ('SEMICOLON', r';'),
    ('COMMA',     r','),
    ('DOT',       r'\.'),
    ('QUESTION',  r'\?'),
    ('COLON',     r':'),
    
    # Literals
    ('NUMBER',    r'\d+(?:\.\d+)?'),
    ('STRING',    r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`(?:[^`\\]|\\.)*`'),
    ('IDENTIFIER',r'[a-zA-Z_$][a-zA-Z0-9_$]*'),
    
    ('MISMATCH',  r'.'),
]

# Compile dynamic regex
TOKEN_REGEX = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC))

def tokenize(code):
    tokens = []
    line_num = 1
    line_start = 0
    
    for mo in TOKEN_REGEX.finditer(code):
        kind = mo.lastgroup
        value = mo.group(kind)
        column = mo.start() - line_start + 1
        
        if kind == 'NEWLINE':
            line_num += 1
            line_start = mo.end()
            continue
        elif kind == 'SKIP' or kind == 'COMMENT_LINE' or kind == 'COMMENT_MULTI':
            # Count internal newlines for multi-line comments
            if kind == 'COMMENT_MULTI':
                newlines = value.count('\n')
                if newlines > 0:
                    line_num += newlines
                    line_start = mo.start() + value.rfind('\n') + 1
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected character {repr(value)} at line {line_num}, column {column}")
        
        # Check if identifier is keyword
        if kind == 'IDENTIFIER' and value in KEYWORDS:
            kind = value.upper() # e.g. LET, CONST, FUNCTION
            
        # Strip quotes from strings
        if kind == 'STRING':
            # Keep string values without leading/trailing quotes for raw content,
            # but wait, template strings might have different processing. Let's keep it clean:
            # strip enclosing quote but keep internal escapes to parse later.
            quote = value[0]
            val_content = value[1:-1]
            # Unescape basic escape characters
            # In JS, standard escapes are \n, \t, \r, \\, \", \', \`
            val_content = (val_content
                           .replace('\\n', '\n')
                           .replace('\\t', '\t')
                           .replace('\\r', '\r')
                           .replace('\\\\', '\\')
                           .replace(f'\\{quote}', quote))
            tokens.append(Token(kind, val_content, line_num, column))
        elif kind == 'NUMBER':
            # Parse number
            val_num = float(value) if '.' in value or 'e' in value.lower() else int(value)
            tokens.append(Token(kind, val_num, line_num, column))
        else:
            tokens.append(Token(kind, value, line_num, column))
            
    tokens.append(Token('EOF', '', line_num, len(code) - line_start + 1))
    return tokens