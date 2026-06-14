"""
the parser takes those tokens and organizes them into a hierarchical,
 structural tree to verify the code's grammar and meaning
"""
# AST Nodes definitions

class ASTNode:
    pass
"""
Program([
    VarDecl(...),
    VarDecl(...)
])
"""
class Program(ASTNode):
    def __init__(self, body):
        self.body = body  # list of statements

class VarDecl(ASTNode):
    def __init__(self, kind, name, init, line, col):
        self.kind = kind  # 'let' or 'const' or 'var'
        self.name = name  # string identifier
        self.init = init  # ASTNode expression or None
        self.line = line
        self.col = col

class IfStmt(ASTNode):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class ForStmt(ASTNode):
    def __init__(self, init, test, update, body):
        self.init = init      # VarDecl, Expression or None
        self.test = test      # Expression or None
        self.update = update  # Expression or None
        self.body = body      # Statement

class WhileStmt(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class DoWhileStmt(ASTNode):
    def __init__(self, body, condition):
        self.body = body
        self.condition = condition

class SwitchCase(ASTNode):
    def __init__(self, test, consequent):
        self.test = test          # Expression or None (default case)
        self.consequent = consequent  # list of statements

class SwitchStmt(ASTNode):
    def __init__(self, discriminant, cases):
        self.discriminant = discriminant
        self.cases = cases  # list of SwitchCase

class FunctionDecl(ASTNode):
    def __init__(self, name, params, rest_param, body):
        self.name = name          # string
        self.params = params      # list of strings
        self.rest_param = rest_param  # string or None
        self.body = body          # BlockStmt

class ReturnStmt(ASTNode):
    def __init__(self, value):
        self.value = value  # ASTNode or None

class BlockStmt(ASTNode):
    def __init__(self, body):
        self.body = body  # list of statements

class ExpressionStmt(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class BreakStmt(ASTNode):
    pass

class ContinueStmt(ASTNode):
    pass

class EmptyStmt(ASTNode):
    pass

# Expression AST Nodes

class BinaryExpr(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryExpr(ASTNode):
    def __init__(self, op, right):
        self.op = op
        self.right = right

class UpdateExpr(ASTNode):
    def __init__(self, op, argument, prefix):
        self.op = op          # '++', '--'
        self.argument = argument  # Identifier or MemberExpr
        self.prefix = prefix  # True/False

class AssignmentExpr(ASTNode):
    def __init__(self, left, op, right):
        self.left = left      # Identifier or MemberExpr
        self.op = op          # '=', '+=', '-='
        self.right = right

class TernaryExpr(ASTNode):
    def __init__(self, condition, then_expr, else_expr):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr

class CallExpr(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args  # list of ASTNodes, which can be SpreadExpr

class MemberExpr(ASTNode):
    def __init__(self, object_, property_, computed):
        self.object = object_
        self.property = property_  # string or Expression
        self.computed = computed    # Boolean (True for obj[prop], False for obj.prop)

class ObjectLiteral(ASTNode):
    def __init__(self, properties):
        self.properties = properties  # dict of string -> ASTNode

class ArrayLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements  # list of ASTNodes (or SpreadExpr)

class SpreadExpr(ASTNode):
    def __init__(self, argument):
        self.argument = argument

class NewExpr(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class ArrowFunction(ASTNode):
    def __init__(self, params, rest_param, body, is_expression_body):
        self.params = params          # list of strings
        self.rest_param = rest_param  # string or None
        self.body = body              # BlockStmt or Expression
        self.is_expression_body = is_expression_body

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value


# Precedences
PREC_LOWEST = 0
PREC_ASSIGN = 1
PREC_TERNARY = 2
PREC_OR = 3
PREC_AND = 4
PREC_EQUALS = 5
PREC_LESS_GREATER = 6
PREC_SUM = 7
PREC_PRODUCT = 8
PREC_EXPONENT = 9
PREC_UNARY = 10
PREC_CALL = 11
PREC_MEMBER = 12

PRECEDENCE_MAP = {
    'ASSIGN': PREC_ASSIGN,
    'ADD_ASSIGN': PREC_ASSIGN,
    'SUB_ASSIGN': PREC_ASSIGN,
    'QUESTION': PREC_TERNARY,
    'OR': PREC_OR,
    'AND': PREC_AND,
    'EQ_LOOSE': PREC_EQUALS,
    'NE_LOOSE': PREC_EQUALS,
    'EQ_STRICT': PREC_EQUALS,
    'NE_STRICT': PREC_EQUALS,
    'LT': PREC_LESS_GREATER,
    'GT': PREC_LESS_GREATER,
    'LE': PREC_LESS_GREATER,
    'GE': PREC_LESS_GREATER,
    'PLUS': PREC_SUM,
    'MINUS': PREC_SUM,
    'MUL': PREC_PRODUCT,
    'DIV': PREC_PRODUCT,
    'MOD': PREC_PRODUCT,
    'EXP': PREC_EXPONENT,
    'LPAREN': PREC_CALL,
    'DOT': PREC_MEMBER,
    'LBRACKET': PREC_MEMBER,
    'INC': PREC_UNARY,
    'DEC': PREC_UNARY,
}

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    #current token
    def current(self):
        return self.tokens[self.pos]
    #Looks one token ahead. --> Useful to detect arrow functions.
    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[self.pos]

    def is_eof(self):
        return self.current().type == 'EOF'

    def advance(self):
        if not self.is_eof():
            self.pos += 1
        return self.tokens[self.pos - 1]

    def consume(self, type_):
        curr = self.current()
        if curr.type != type_:
            raise SyntaxError(f"Expected token {type_}, got {curr.type} ({repr(curr.value)}) at line {curr.line}, column {curr.column}")
        return self.advance()

    def match(self, type_):
        if self.current().type == type_:
            self.advance()
            return True
        return False

    def get_current_precedence(self):
        return PRECEDENCE_MAP.get(self.current().type, PREC_LOWEST)

    # Parsing Entrypoint
    # Produces:Program(...) -> Program(stmt1,stmt2...)
    def parse(self):
        body = []
        while not self.is_eof():
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        return Program(body)

    # Statements
    def parse_statement(self):
        curr = self.current()
        
        if curr.type in ('LET', 'CONST', 'VAR'):
            return self.parse_var_declaration()
        elif curr.type == 'IF':
            return self.parse_if_statement()
        elif curr.type == 'FOR':
            return self.parse_for_statement()
        elif curr.type == 'WHILE':
            return self.parse_while_statement()
        elif curr.type == 'DO':
            return self.parse_do_while_statement()
        elif curr.type == 'SWITCH':
            return self.parse_switch_statement()
        elif curr.type == 'FUNCTION':
            return self.parse_function_declaration()
        elif curr.type == 'RETURN':
            return self.parse_return_statement()
        elif curr.type == 'BREAK':
            self.advance()
            self.match('SEMICOLON')
            return BreakStmt()
        elif curr.type == 'CONTINUE':
            self.advance()
            self.match('SEMICOLON')
            return ContinueStmt()
        elif curr.type == 'LBRACE':
            return self.parse_block_statement()
        elif curr.type == 'SEMICOLON':
            self.advance()
            return EmptyStmt()
        else:
            return self.parse_expression_statement()

    def parse_var_declaration(self):
        kind_tok = self.advance() # let / const / var
        kind = kind_tok.value
        name_tok = self.consume('IDENTIFIER')
        name = name_tok.value
        
        init = None
        if self.match('ASSIGN'):
            init = self.parse_expression()
            
        self.match('SEMICOLON')
        return VarDecl(kind, name, init, kind_tok.line, kind_tok.column)

    def parse_if_statement(self):
        self.consume('IF')
        self.consume('LPAREN')
        cond = self.parse_expression()
        self.consume('RPAREN')
        
        then_branch = self.parse_statement()
        else_branch = None
        
        if self.match('ELSE'):
            else_branch = self.parse_statement()
            
        return IfStmt(cond, then_branch, else_branch)

    def parse_for_statement(self):
        self.consume('FOR')
        self.consume('LPAREN')
        
        init = None
        if not self.match('SEMICOLON'):
            if self.current().type in ('LET', 'CONST', 'VAR'):
                init = self.parse_var_declaration()
                # parse_var_declaration consumes the semicolon
            else:
                init = self.parse_expression()
                self.consume('SEMICOLON')
                
        test = None
        if not self.match('SEMICOLON'):
            test = self.parse_expression()
            self.consume('SEMICOLON')
            
        update = None
        if not self.match('RPAREN'):
            update = self.parse_expression()
            self.consume('RPAREN')
            
        body = self.parse_statement()
        return ForStmt(init, test, update, body)

    def parse_while_statement(self):
        self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_expression()
        self.consume('RPAREN')
        body = self.parse_statement()
        return WhileStmt(cond, body)

    def parse_do_while_statement(self):
        self.consume('DO')
        body = self.parse_statement()
        self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_expression()
        self.consume('RPAREN')
        self.match('SEMICOLON')
        return DoWhileStmt(body, cond)

    def parse_switch_statement(self):
        self.consume('SWITCH')
        self.consume('LPAREN')
        disc = self.parse_expression()
        self.consume('RPAREN')
        self.consume('LBRACE')
        
        cases = []
        while not self.match('RBRACE'):
            if self.match('CASE'):
                test = self.parse_expression()
                self.consume('COLON')
                consequent = []
                while self.current().type not in ('CASE', 'DEFAULT', 'RBRACE'):
                    consequent.append(self.parse_statement())
                cases.append(SwitchCase(test, consequent))
            elif self.match('DEFAULT'):
                self.consume('COLON')
                consequent = []
                while self.current().type not in ('CASE', 'DEFAULT', 'RBRACE'):
                    consequent.append(self.parse_statement())
                cases.append(SwitchCase(None, consequent))
            else:
                raise SyntaxError(f"Unexpected token inside switch: {self.current().value}")
                
        return SwitchStmt(disc, cases)

    def parse_function_declaration(self):
        self.consume('FUNCTION')
        name_tok = self.consume('IDENTIFIER')
        name = name_tok.value
        
        self.consume('LPAREN')
        params, rest_param = self.parse_formal_params()
        self.consume('RPAREN')
        
        body = self.parse_block_statement()
        return FunctionDecl(name, params, rest_param, body)

    def parse_formal_params(self):
        params = []
        rest_param = None
        if self.current().type == 'RPAREN':
            return params, rest_param
            
        while True:
            if self.match('SPREAD'):
                rest_tok = self.consume('IDENTIFIER')
                rest_param = rest_tok.value
                break
            
            p_tok = self.consume('IDENTIFIER')
            params.append(p_tok.value)
            
            if not self.match('COMMA'):
                break
        return params, rest_param

    def parse_return_statement(self):
        self.consume('RETURN')
        val = None
        if self.current().type != 'SEMICOLON':
            # Check if there's an expression on same line
            val = self.parse_expression()
        self.match('SEMICOLON')
        return ReturnStmt(val)

    def parse_block_statement(self):
        self.consume('LBRACE')
        body = []
        while not self.match('RBRACE'):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        return BlockStmt(body)

    def parse_expression_statement(self):
        expr = self.parse_expression()
        self.match('SEMICOLON')
        return ExpressionStmt(expr)

    # Expression parsing (Pratt Parser)
    def parse_expression(self, precedence=PREC_LOWEST):
        # Lookahead for Arrow Function
        if self.is_arrow_function_start():
            return self.parse_arrow_function()

        token = self.current()
        prefix_fn = self.get_prefix_fn(token.type)
        if not prefix_fn:
            raise SyntaxError(f"Unexpected token {token.value} ({token.type}) at line {token.line}, column {token.column}")
        
        left = prefix_fn()
        
        while precedence < self.get_current_precedence():
            infix_token = self.current()
            infix_fn = self.get_infix_fn(infix_token.type)
            if not infix_fn:
                break
            left = infix_fn(left)
            
        return left

    def is_arrow_function_start(self):
        curr = self.current()
        # Pattern 1: identifier =>
        if curr.type == 'IDENTIFIER' and self.peek().type == 'ARROW':
            return True
        # Pattern 2: ( ... ) =>
        if curr.type == 'LPAREN':
            # Scan forward to matching RPAREN
            depth = 0
            i = self.pos
            while i < len(self.tokens):
                t = self.tokens[i]
                if t.type == 'LPAREN':
                    depth += 1
                elif t.type == 'RPAREN':
                    depth -= 1
                    if depth == 0:
                        # Check if token after RPAREN is ARROW
                        if i + 1 < len(self.tokens) and self.tokens[i+1].type == 'ARROW':
                            return True
                        break
                i += 1
        return False

    def parse_arrow_function(self):
        params = []
        rest_param = None
        
        if self.current().type == 'IDENTIFIER':
            p_tok = self.consume('IDENTIFIER')
            params.append(p_tok.value)
        else:
            self.consume('LPAREN')
            params, rest_param = self.parse_formal_params()
            self.consume('RPAREN')
            
        self.consume('ARROW')
        
        if self.current().type == 'LBRACE':
            body = self.parse_block_statement()
            is_expression_body = False
        else:
            body = self.parse_expression()
            is_expression_body = True
            
        return ArrowFunction(params, rest_param, body, is_expression_body)

    # Pratt prefix parse functions
    def get_prefix_fn(self, token_type):
        prefix_fns = {
            'IDENTIFIER': self.parse_identifier,
            'NUMBER': self.parse_literal,
            'STRING': self.parse_literal,
            'TRUE': self.parse_literal_bool,
            'FALSE': self.parse_literal_bool,
            'NULL': self.parse_literal_null,
            'UNDEFINED': self.parse_literal_undefined,
            
            'PLUS': self.parse_prefix_expr,
            'MINUS': self.parse_prefix_expr,
            'NOT': self.parse_prefix_expr,
            'INC': self.parse_prefix_expr,
            'DEC': self.parse_prefix_expr,
            
            'LPAREN': self.parse_grouped_expr,
            'LBRACKET': self.parse_array_literal,
            'LBRACE': self.parse_object_literal,
            'FUNCTION': self.parse_function_expression,
            'SPREAD': self.parse_spread_expr,
            'NEW': self.parse_new_expr,
        }
        return prefix_fns.get(token_type)

    def parse_identifier(self):
        tok = self.consume('IDENTIFIER')
        return Identifier(tok.value)

    def parse_literal(self):
        tok = self.advance()
        return Literal(tok.value)

    def parse_literal_bool(self):
        tok = self.advance()
        return Literal(True if tok.type == 'TRUE' else False)

    def parse_literal_null(self):
        self.advance()
        return Literal(None)

    def parse_literal_undefined(self):
        self.advance()
        # In python, we can represent JS undefined as a sentinel or just None.
        # But wait, undefined is different from null in JS. Let's make a sentinel or standard object.
        # Let's import a sentinel Undefined from js_types or define a special class
        return Literal(Undefined)

    def parse_prefix_expr(self):
        op_tok = self.advance()
        right = self.parse_expression(PREC_UNARY)
        # Prefix increment/decrement is an UpdateExpr
        if op_tok.type in ('INC', 'DEC'):
            return UpdateExpr(op_tok.value, right, prefix=True)
        return UnaryExpr(op_tok.value, right)

    def parse_grouped_expr(self):
        self.consume('LPAREN')
        expr = self.parse_expression()
        self.consume('RPAREN')
        return expr

    def parse_array_literal(self):
        self.consume('LBRACKET')
        elements = []
        if self.current().type == 'RBRACKET':
            self.consume('RBRACKET')
            return ArrayLiteral(elements)
            
        while True:
            el = self.parse_expression()
            elements.append(el)
            if not self.match('COMMA'):
                break
        self.consume('RBRACKET')
        return ArrayLiteral(elements)

    def parse_spread_expr(self):
        self.consume('SPREAD')
        expr = self.parse_expression()
        return SpreadExpr(expr)

    def parse_new_expr(self):
        self.consume('NEW')
        callee = self.parse_expression(PREC_CALL - 1)
        if isinstance(callee, CallExpr):
            return NewExpr(callee.callee, callee.args)
        return NewExpr(callee, [])

    def parse_object_literal(self):
        self.consume('LBRACE')
        properties = {}
        if self.current().type == 'RBRACE':
            self.consume('RBRACE')
            return ObjectLiteral(properties)
            
        while True:
            # Keys can be identifiers, strings, or numbers
            curr = self.current()
            if curr.type in ('IDENTIFIER', 'STRING', 'NUMBER'):
                key = str(self.advance().value)
            else:
                raise SyntaxError(f"Expected object property name, got {curr.type} at line {curr.line}")
                
            self.consume('COLON')
            val = self.parse_expression()
            properties[key] = val
            
            if not self.match('COMMA'):
                break
        self.consume('RBRACE')
        return ObjectLiteral(properties)

    def parse_function_expression(self):
        self.consume('FUNCTION')
        name = None
        if self.current().type == 'IDENTIFIER':
            name = self.consume('IDENTIFIER').value
            
        self.consume('LPAREN')
        params, rest_param = self.parse_formal_params()
        self.consume('RPAREN')
        
        body = self.parse_block_statement()
        # In expressions, it evaluates to a closure, we can represent it via an anonymous FunctionDecl
        return FunctionDecl(name, params, rest_param, body)

    # Pratt infix parse functions
    def get_infix_fn(self, token_type):
        infix_fns = {
            'PLUS': self.parse_binary_expr,
            'MINUS': self.parse_binary_expr,
            'MUL': self.parse_binary_expr,
            'DIV': self.parse_binary_expr,
            'MOD': self.parse_binary_expr,
            'EXP': self.parse_binary_expr,
            'EQ_LOOSE': self.parse_binary_expr,
            'NE_LOOSE': self.parse_binary_expr,
            'EQ_STRICT': self.parse_binary_expr,
            'NE_STRICT': self.parse_binary_expr,
            'LT': self.parse_binary_expr,
            'GT': self.parse_binary_expr,
            'LE': self.parse_binary_expr,
            'GE': self.parse_binary_expr,
            'AND': self.parse_binary_expr,
            'OR': self.parse_binary_expr,
            
            'ASSIGN': self.parse_assignment_expr,
            'ADD_ASSIGN': self.parse_assignment_expr,
            'SUB_ASSIGN': self.parse_assignment_expr,
            
            'LPAREN': self.parse_call_expr,
            'DOT': self.parse_member_expr,
            'LBRACKET': self.parse_member_expr,
            'QUESTION': self.parse_ternary_expr,
            
            'INC': self.parse_postfix_expr,
            'DEC': self.parse_postfix_expr,
        }
        return infix_fns.get(token_type)

    def parse_binary_expr(self, left):
        op_tok = self.advance()
        prec = PRECEDENCE_MAP.get(op_tok.type, PREC_LOWEST)
        # Exponentiation is right-associative, so parse with slightly lower precedence
        if op_tok.type == 'EXP':
            right = self.parse_expression(prec - 1)
        else:
            right = self.parse_expression(prec)
        return BinaryExpr(left, op_tok.value, right)

    def parse_assignment_expr(self, left):
        op_tok = self.advance()
        prec = PRECEDENCE_MAP.get(op_tok.type, PREC_LOWEST)
        # Assignment is right-associative
        right = self.parse_expression(prec - 1)
        return AssignmentExpr(left, op_tok.value, right)

    def parse_call_expr(self, left):
        self.consume('LPAREN')
        args = []
        if self.current().type == 'RPAREN':
            self.consume('RPAREN')
            return CallExpr(left, args)
            
        while True:
            arg = self.parse_expression()
            args.append(arg)
            if not self.match('COMMA'):
                break
        self.consume('RPAREN')
        return CallExpr(left, args)

    def parse_member_expr(self, left):
        op_tok = self.advance()
        if op_tok.type == 'DOT':
            prop_tok = self.consume('IDENTIFIER')
            return MemberExpr(left, prop_tok.value, computed=False)
        else: # LBRACKET
            prop_expr = self.parse_expression()
            self.consume('RBRACKET')
            return MemberExpr(left, prop_expr, computed=True)

    def parse_ternary_expr(self, left):
        self.consume('QUESTION')
        then_expr = self.parse_expression()
        self.consume('COLON')
        else_expr = self.parse_expression(PREC_TERNARY - 1)
        return TernaryExpr(left, then_expr, else_expr)

    def parse_postfix_expr(self, left):
        op_tok = self.advance()
        return UpdateExpr(op_tok.value, left, prefix=False)


# Undefined singleton pattern
class JSUndefinedType:
    def __repr__(self):
        return "undefined"
    def __str__(self):
        return "undefined"

Undefined = JSUndefinedType()