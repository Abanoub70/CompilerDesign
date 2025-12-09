from scanner import tokenize


class Parser:
    """A simple recursive-descent parser that consumes tokens
    produced by `scanner.tokenize`. It returns an AST or raises
    SyntaxError with a clear message.
    """

    BASIC_TYPES = {'int', 'float', 'double', 'bool', 'char', 'void'}

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def error(self, expected):
        t = self.current_token
        if t:
            raise SyntaxError(f"Syntax error at line {t.line}, column {t.column}: expected {expected}, found '{t.value}' ({t.type})")
        else:
            raise SyntaxError(f"Syntax error at end of input: expected {expected}")

    def eat(self, token_type):
        """Consume a token of given type, advance to next token."""
        if self.current_token and self.current_token.type == token_type:
            self.pos += 1
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        else:
            self.error(token_type)

    def eat_value(self, value):
        """Consume the current token if its textual value matches `value`."""
        if self.current_token and self.current_token.value == value:
            self.eat(self.current_token.type)
        else:
            self.error(repr(value))

    # Top-level
    def parse(self):
        ast = self.program()
        if self.current_token is not None:
            self.error('end of input')
        return ast

    def program(self):
        return {'type': 'program', 'body': self.statement_list()}

    def statement_list(self):
        stmts = []
        while self.current_token and not (self.current_token.type == 'Special_characters' and self.current_token.value == '}'):
            stmts.append(self.statement())
        return stmts

    def statement(self):
        if not self.current_token:
            self.error('statement')

        t = self.current_token

        # Keywords-driven statements
        if t.type == 'Keywords':
            if t.value in self.BASIC_TYPES:
                # Could be function definition or variable declaration
                return self.declaration_or_function()
            if t.value == 'if':
                return self.if_statement()
            if t.value == 'while':
                return self.while_statement()
            if t.value == 'for':
                return self.for_statement()
            if t.value == 'return':
                return self.return_statement()

        # Block
        if t.type == 'Special_characters' and t.value == '{':
            self.eat('Special_characters')  # consume '{'
            body = self.statement_list()
            self.eat_value('}')
            return {'type': 'block', 'body': body}

        # Assignment or expression statement starting with identifier or '(' or number
        if t.type == 'Identifiers':
            # Could be assignment or function call (not implemented) -> treat as assignment
            stmt = self.assignment()
            self.eat_value(';')
            return stmt

        # Expression statement (starting with literal or '(')
        if (t.type == 'Numeric_constants') or (t.type == 'Special_characters' and t.value == '(') or (t.type == 'Keywords' and t.value in ('true', 'false')):
            expr = self.expression()
            self.eat_value(';')
            return {'type': 'expr_stmt', 'expr': expr}

        self.error('statement')

    def declaration_or_function(self):
        # Peek: type IDENT ( '(' -> function def ) else declaration
        type_name = self.current_token.value
        self.eat('Keywords')
        if self.current_token and self.current_token.type == 'Identifiers':
            name = self.current_token.value
            self.eat('Identifiers')
            if self.current_token and self.current_token.type == 'Special_characters' and self.current_token.value == '(':
                # function definition (simple, no parameter parsing beyond empty or identifiers)
                self.eat_value('(')
                params = []
                if self.current_token and not (self.current_token.type == 'Special_characters' and self.current_token.value == ')'):
                    # simple comma-separated parameters: type id
                    while True:
                        if self.current_token.type != 'Keywords':
                            self.error('parameter type')
                        ptype = self.current_token.value
                        self.eat('Keywords')
                        if self.current_token.type != 'Identifiers':
                            self.error('parameter name')
                        pname = self.current_token.value
                        self.eat('Identifiers')
                        params.append({'type': ptype, 'name': pname})
                        if self.current_token.type == 'Special_characters' and self.current_token.value == ',':
                            self.eat('Special_characters')
                            continue
                        break
                self.eat_value(')')
                # function body is a block
                body = self.statement()
                return {'type': 'function_def', 'return_type': type_name, 'name': name, 'params': params, 'body': body}
            else:
                # variable declaration; expect semicolon
                self.eat_value(';')
                return {'type': 'declaration', 'var_type': type_name, 'name': name}
        else:
            self.error('identifier')

    def assignment(self):
        if not (self.current_token and self.current_token.type == 'Identifiers'):
            self.error('identifier')
        name = self.current_token.value
        self.eat('Identifiers')
        self.eat_value('=')
        expr = self.expression()
        return {'type': 'assignment', 'target': name, 'value': expr}

    def if_statement(self):
        self.eat_value('if')
        self.eat_value('(')
        cond = self.expression()
        self.eat_value(')')
        then_branch = self.statement()
        else_branch = None
        if self.current_token and self.current_token.type == 'Keywords' and self.current_token.value == 'else':
            self.eat_value('else')
            else_branch = self.statement()
        return {'type': 'if', 'cond': cond, 'then': then_branch, 'else': else_branch}

    def while_statement(self):
        self.eat_value('while')
        self.eat_value('(')
        cond = self.expression()
        self.eat_value(')')
        body = self.statement()
        return {'type': 'while', 'cond': cond, 'body': body}

    def for_statement(self):
        self.eat_value('for')
        self.eat_value('(')
        init = None
        if not (self.current_token.type == 'Special_characters' and self.current_token.value == ';'):
            # either declaration or assignment
            if self.current_token.type == 'Keywords' and self.current_token.value in self.BASIC_TYPES:
                # declaration without consuming trailing ';' (for clause will consume it)
                tname = self.current_token.value
                self.eat('Keywords')
                if self.current_token.type != 'Identifiers':
                    self.error('identifier')
                iname = self.current_token.value
                self.eat('Identifiers')
                init = {'type': 'declaration', 'var_type': tname, 'name': iname}
            else:
                init = self.assignment()
        self.eat_value(';')
        cond = None
        if not (self.current_token.type == 'Special_characters' and self.current_token.value == ';'):
            cond = self.expression()
        self.eat_value(';')
        update = None
        if not (self.current_token.type == 'Special_characters' and self.current_token.value == ')'):
            if self.current_token.type == 'Identifiers':
                update = self.assignment()
            else:
                update = self.expression()
        self.eat_value(')')
        body = self.statement()
        return {'type': 'for', 'init': init, 'cond': cond, 'update': update, 'body': body}

    def return_statement(self):
        self.eat_value('return')
        expr = self.expression()
        self.eat_value(';')
        return {'type': 'return', 'expr': expr}

    # Expression parsing with precedence
    def expression(self):
        node = self.logical_or()
        return node

    def logical_or(self):
        node = self.logical_and()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value == '||':
            op = self.current_token.value
            self.eat('Operators')
            right = self.logical_and()
            node = {'type': 'binary_op', 'op': op, 'left': node, 'right': right}
        return node

    def logical_and(self):
        node = self.equality()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value == '&&':
            op = self.current_token.value
            self.eat('Operators')
            right = self.equality()
            node = {'type': 'binary_op', 'op': op, 'left': node, 'right': right}
        return node

    def equality(self):
        node = self.relational()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value in ('==', '!='):
            op = self.current_token.value
            self.eat('Operators')
            right = self.relational()
            node = {'type': 'binary_op', 'op': op, 'left': node, 'right': right}
        return node

    def relational(self):
        node = self.additive()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value in ('<', '>', '<=', '>='):
            op = self.current_token.value
            self.eat('Operators')
            right = self.additive()
            node = {'type': 'binary_op', 'op': op, 'left': node, 'right': right}
        return node

    def additive(self):
        node = self.multiplicative()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value in ('+', '-'):
            op = self.current_token.value
            self.eat('Operators')
            right = self.multiplicative()
            node = {'type': 'binary_op', 'op': op, 'left': node, 'right': right}
        return node

    def multiplicative(self):
        node = self.unary()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value in ('*', '/', '%'):
            op = self.current_token.value
            self.eat('Operators')
            right = self.unary()
            node = {'type': 'binary_op', 'op': op, 'left': node, 'right': right}
        return node

    def unary(self):
        if self.current_token and self.current_token.type == 'Operators' and self.current_token.value in ('+', '-', '!'):
            op = self.current_token.value
            self.eat('Operators')
            operand = self.unary()
            return {'type': 'unary_op', 'op': op, 'operand': operand}
        return self.primary()

    def primary(self):
        t = self.current_token
        if not t:
            self.error('primary expression')
        if t.type == 'Identifiers':
            name = t.value
            self.eat('Identifiers')
            return {'type': 'identifier', 'value': name}
        if t.type == 'Numeric_constants':
            val = t.value
            self.eat('Numeric_constants')
            return {'type': 'number', 'value': val}
        if t.type == 'Keywords' and t.value in ('true', 'false'):
            val = t.value
            self.eat('Keywords')
            return {'type': 'boolean', 'value': val}
        if t.type == 'Special_characters' and t.value == '(':
            self.eat('Special_characters')
            node = self.expression()
            self.eat_value(')')
            return node
        self.error('identifier, number, boolean, or (expression)')


def parse_code(code):
    tokens = tokenize(code)
    p = Parser(tokens)
    try:
        ast = p.parse()
        print('Accepted')
        return 'Accepted', ast
    except SyntaxError as e:
        print('Syntax Error:', e)
        return f'Syntax Error: {e}', None


if __name__ == '__main__':
    sample = '''
    int x;
    x = 5 + 3 * 2;
    if (x > 10) {
        return x;
    } else {
        x = x + 1;
    }
    '''
    parse_code(sample)
