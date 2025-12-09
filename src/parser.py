from scanner import tokenize

class Parser:
    def __init__(self, tokens):
        # Filter out comments and other non-essential tokens if any
        self.tokens = [t for t in tokens if t.type != 'Comments']
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def error(self, message):
        if self.current_token:
            t = self.current_token
            raise SyntaxError(f"Syntax error at line {t.line}: {message}. Found '{t.value}' ({t.type})")
        else:
            raise SyntaxError(f"Syntax error at end of input: {message}")

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def eat(self, token_type, value=None):
        if self.current_token:
            # Check type match
            type_match = (self.current_token.type == token_type)
            # Check value match if provided
            value_match = (value is None) or (self.current_token.value == value)
            
            if type_match and value_match:
                self.advance()
            else:
                expected = f"{token_type}" + (f" ('{value}')" if value else "")
                self.error(f"Expected {expected}")
        else:
            self.error(f"Unexpected end of input, expected {token_type}")

    def parse(self):
        self.program()
        if self.current_token is not None:
            self.error("Unexpected tokens after valid program")
        return "Accepted"

    def program(self):
        # <program> ::= <statement_list>
        self.statement_list()

    def statement_list(self):
        # <statement_list> ::= <statement> { <statement> }
        # We assume if it looks like a statement, we parse it.
        # Statement starts with:
        # - Type (int, float...) -> declaration
        # - Identifier -> assignment (or declaration start if type is identifier? No types are reserved keywords usually)
        # - 'if'
        # - 'while'
        # - 'for'
        # - 'return'
        # - '{'
        while self.current_token and self.is_statement_start():
            self.statement()

    def is_statement_start(self):
        t = self.current_token
        if not t: return False
        if t.type == 'Keywords':
            if t.value in ('int', 'float', 'double', 'bool', 'char', 'string', 'void', 'if', 'while', 'for', 'return'):
                return True
        if t.type == 'Identifiers':
            return True
        if t.type == 'Special_characters' and t.value == '{':
            return True
        return False

    def statement(self):
        t = self.current_token
        
        # Block
        if t.type == 'Special_characters' and t.value == '{':
            self.block()
            return

        if t.type == 'Keywords':
            val = t.value
            # Control flow
            if val == 'if':
                self.if_statement()
                return
            if val == 'while':
                self.while_statement()
                return
            if val == 'for':
                self.for_statement()
                return
            if val == 'return':
                self.return_statement()
                return
            # Type -> Declaration
            if val in ('int', 'float', 'double', 'bool', 'char', 'string', 'void'):
                self.declaration()
                self.eat('Special_characters', ';')
                return

        # Assignment
        if t.type == 'Identifiers':
            self.assignment()
            self.eat('Special_characters', ';')
            return

        self.error("Invalid statement start")

    def block(self):
        self.eat('Special_characters', '{')
        self.statement_list()
        self.eat('Special_characters', '}')

    def declaration(self):
        # <declaration> ::= <type> <identifier>
        # Type is already checked/consumed in statement? No, peeked.
        self.eat('Keywords') # consume type
        self.eat('Identifiers')

    def assignment(self):
        # <assignment> ::= <identifier> '=' <expression>
        self.eat('Identifiers')
        self.eat('Operators', '=')
        self.expression()

    def if_statement(self):
        # "if" '(' <expression> ')' <statement> [ "else" <statement> ]
        self.eat('Keywords', 'if')
        self.eat('Special_characters', '(')
        self.expression()
        self.eat('Special_characters', ')')
        self.statement()
        
        if self.current_token and self.current_token.type == 'Keywords' and self.current_token.value == 'else':
            self.eat('Keywords', 'else')
            self.statement()

    def while_statement(self):
        # "while" '(' <expression> ')' <statement>
        self.eat('Keywords', 'while')
        self.eat('Special_characters', '(')
        self.expression()
        self.eat('Special_characters', ')')
        self.statement()

    def for_statement(self):
        # "for" '(' <assignment> ';' <expression> ';' <assignment> ')' <statement>
        # Note: grammar provided says <assignment> but C allows declarations or empty.
        # User grammar: "for" '(' <assignment> ';' <expression> ';' <assignment> ')' <statement>
        # I will strictly follow the provided grammar initially, but be robust if I see a type.
        # Actually proper C for loop: for (init; cond; update).
        # Init can be declaration or assignment.
        
        self.eat('Keywords', 'for')
        self.eat('Special_characters', '(')
        
        # Init
        if self.current_token.type == 'Keywords' and self.current_token.value in ('int', 'float', 'double', 'bool', 'char', 'string', 'void'):
             self.declaration() # consumes type then identifier
             # Assuming declaration inside for loop doesn't have a semicolon terminator in this context? 
             # Standard C: for(int i=0; ...) -> that's a declaration with assignment.
             # Grammar says: <assignment> ';' ...
             # Code provided: <for> ... <assignment>
             # To be safe and compliant with common sense + requirement "expand grammar":
             # Logic: Check if type -> Declaration. Else -> Assignment.
             pass 
        else:
             self.assignment() # identifier = expr
        
        self.eat('Special_characters', ';')
        
        # Condition
        self.expression()
        self.eat('Special_characters', ';')
        
        # Update
        self.assignment()
        self.eat('Special_characters', ')')
        
        self.statement()

    def return_statement(self):
        # "return" <expression> ';'
        self.eat('Keywords', 'return')
        self.expression()
        self.eat('Special_characters', ';')

    # --- Expressions ---
    # Grammar:
    # <expression> ::= <comparison> ( ('==' | '!=' | '<' | '<=' | '>' | '>=') <comparison> )*
    # <comparison> ::= <term> ( ('+' | '-') <term> )*
    # <term> ::= <factor> ( ('*' | '/') <factor> )*
    # <factor> ::= <identifier> | <number> | '(' <expression> ')' | "true" | "false"

    def expression(self):
        self.comparison()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value in ('==', '!=', '<', '<=', '>', '>='):
            self.eat('Operators', self.current_token.value)
            self.comparison()

    def comparison(self):
        self.term()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value in ('+', '-'):
            self.eat('Operators', self.current_token.value)
            self.term()

    def term(self):
        self.factor()
        while self.current_token and self.current_token.type == 'Operators' and self.current_token.value in ('*', '/'):
            self.eat('Operators', self.current_token.value)
            self.factor()

    def factor(self):
        t = self.current_token
        if not t:
            self.error("Unexpected end of input in expression")

        if t.type == 'Identifiers':
            self.eat('Identifiers')
        elif t.type == 'Numeric_constants':
            self.eat('Numeric_constants') # covers integers and floats
        elif t.type == 'Keywords' and t.value in ('true', 'false'):
            self.eat('Keywords')
        elif t.type == 'Special_characters' and t.value == '(':
            self.eat('Special_characters', '(')
            self.expression()
            self.eat('Special_characters', ')')
        else:
            self.error("Expected identifier, number, boolean or '('")


def main():
    print("Type your C-like code. Enter an empty line to finish:")
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                break
            lines.append(line)
        except EOFError:
            break
    
    code = "\n".join(lines)
    if not code.strip():
        return

    try:
        tokens = tokenize(code)
        parser = Parser(tokens)
        result = parser.parse()
        print(result)
    except SyntaxError as e:
        print(e)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
