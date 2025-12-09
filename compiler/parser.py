from typing import List, Optional
from .lexer import Token
from .ast_nodes import *

class Parser:
    """Recursive descent parser for the language"""
    
    # Operator precedence for expression parsing
    PRECEDENCE = {
        "||": 1,
        "&&": 2,
        "==": 3, "!=": 3,
        "<": 4, ">": 4, "<=": 4, ">=": 4,
        "+": 5, "-": 5,
        "*": 6, "/": 6, "%": 6,
    }
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def next(self) -> Token:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def match(self, *types) -> Optional[Token]:
        if self.peek()[0] in types:
            return self.next()
        return None

    def expect(self, typ: str) -> Token:
        t = self.next()
        if t[0] != typ:
            raise SyntaxError(f"Expected {typ}, got {t}")
        return t

    def expect_op(self, s: str):
        """Expect a specific operator"""
        t = self.next()
        if t[1] != s:
            raise SyntaxError(f"Expected operator {s}, got {t}")

    def expect_type(self) -> Token:
        """Expect a type keyword (int, float, string, bool, void)"""
        t = self.peek()
        if t[0] in ("INT", "FLOAT", "STRING", "BOOL", "VOID"):
            return self.next()
        raise SyntaxError(f"Expected type, got {t}")

    
    def parse(self) -> Program:
        """Parse entire program (list of function declarations)"""
        funcs = []
        while self.peek()[0] != "EOF":
            funcs.append(self.parse_function())
        return Program(funcs)

    def parse_function(self) -> FuncDecl:
        """Parse: func <type> name (params) { body }"""
        self.expect("FUNC")
        ret_type = self.expect_type()[1]
        name = self.expect("ID")[1]
        
        self.expect("OP")
        if self.tokens[self.pos-1][1] != "(":
            raise SyntaxError("Expected '(' after function name")
        
        # Parse parameters
        params = []
        if self.peek()[1] != ")":
            while True:
                p_type = self.expect_type()[1]
                p_name = self.expect("ID")[1]
                params.append((p_type, p_name))
                if self.peek()[1] == ",":
                    self.next()
                    continue
                break
        
        self.expect("OP")
        if self.tokens[self.pos-1][1] != ")":
            raise SyntaxError("Expected ')' after params")
        
        self.expect("OP")
        if self.tokens[self.pos-1][1] != "{":
            raise SyntaxError("Expected '{' to start function body")
        
        body = self.parse_block()
        return FuncDecl(ret_type, name, params, body)

    def parse_block(self) -> List[Stmt]:
        """Parse block of statements until closing }"""
        stmts = []
        while True:
            if self.peek()[1] == "}":
                self.next()  # consume }
                break
            stmts.append(self.parse_statement())
        return stmts

    
    def parse_statement(self) -> Stmt:
        """Parse a single statement"""
        t = self.peek()
        
        if t[0] in ("INT", "FLOAT", "STRING", "BOOL"):
            return self.parse_vardecl()
        
        if t[0] == "IF":
            return self.parse_if()
        
        if t[0] == "WHILE":
            return self.parse_while()
        
        if t[0] == "FOR":
            return self.parse_for()
        
        if t[0] == "RETURN":
            self.next()
            if self.peek()[1] == ";":
                self.next()
                return ReturnStmt(None)
            expr = self.parse_expr()
            self.expect_op(";")
            return ReturnStmt(expr)
        
        # Expression statement
        expr = self.parse_expr()
        self.expect_op(";")
        return ExprStmt(expr)

    def parse_vardecl(self) -> VarDecl:
        """Parse: type name1, name2 = init, ...; """
        typ = self.expect_type()[1]
        names = []
        
        while True:
            name = self.expect("ID")[1]
            init = None
            if self.peek()[1] == "=":
                self.next()
                init = self.parse_expr()
            names.append((name, init))
            
            if self.peek()[1] == ",":
                self.next()
                continue
            break
        
        self.expect_op(";")
        return VarDecl(typ, names)

    def parse_if(self) -> IfStmt:
        """Parse: if (cond) { ... } else { ... }"""
        self.expect("IF")
        self.expect_op("(")
        cond = self.parse_expr()
        self.expect_op(")")
        self.expect_op("{")
        then_block = self.parse_block()
        
        else_block = None
        if self.peek()[0] == "ELSE":
            self.next()
            self.expect_op("{")
            else_block = self.parse_block()
        
        return IfStmt(cond, then_block, else_block)

    def parse_while(self) -> WhileStmt:
        """Parse: while (cond) { ... }"""
        self.expect("WHILE")
        self.expect_op("(")
        cond = self.parse_expr()
        self.expect_op(")")
        self.expect_op("{")
        body = self.parse_block()
        return WhileStmt(cond, body)

    def parse_for(self) -> ForStmt:
        """Parse: for (init; cond; post) { ... }"""
        self.expect("FOR")
        self.expect_op("(")
        
        # Init (optional)
        init = None
        if self.peek()[1] != ";":
            if self.peek()[0] in ("INT", "FLOAT", "STRING", "BOOL"):
                init = self.parse_vardecl_for()
            else:
                expr = self.parse_expr()
                self.expect_op(";")
                init = ExprStmt(expr)
        else:
            self.expect_op(";")
        
        # Condition (optional)
        cond = None
        if self.peek()[1] != ";":
            cond = self.parse_expr()
        self.expect_op(";")
        
        # Post (optional)
        post = None
        if self.peek()[1] != ")":
            post = self.parse_expr()
        self.expect_op(")")
        
        self.expect_op("{")
        body = self.parse_block()
        return ForStmt(init, cond, post, body)

    def parse_vardecl_for(self) -> VarDecl:
        """Parse variable declaration inside for loop (already consumes ;)"""
        typ = self.expect_type()[1]
        names = []
        
        while True:
            name = self.expect("ID")[1]
            init = None
            if self.peek()[1] == "=":
                self.next()
                init = self.parse_expr()
            names.append((name, init))
            
            if self.peek()[1] == ",":
                self.next()
                continue
            break
        
        self.expect_op(";")
        return VarDecl(typ, names)

    # ============ Expression parsing ============
    
    def parse_expr(self, min_prec=1) -> Expr:
        """Parse expression using precedence climbing"""
        t = self.peek()
        
        # Parse unary operators
        if t[1] in ("+", "-", "!"):
            op = self.next()[1]
            left: Expr = UnaryExpr(op, self.parse_expr(7))
        else:
            left = self.parse_primary()
        
        # Parse binary operators
        while True:
            tok = self.peek()
            op = tok[1]
            
            if op not in self.PRECEDENCE:
                break
            
            prec = self.PRECEDENCE[op]
            if prec < min_prec:
                break
            
            self.next()
            right = self.parse_expr(prec + 1)
            left = BinaryExpr(left, op, right)
        
        return left

    def parse_primary(self) -> Expr:
        """Parse primary expressions (literals, variables, function calls, etc.)"""
        t = self.peek()
        
        # Number literal
        if t[0] == "NUMBER":
            tok = self.next()[1]
            if "." in tok:
                return Literal(float(tok))
            return Literal(int(tok))
        
        # String literal
        if t[0] == "STRING":
            s = self.next()[1]
            val = bytes(s[1:-1], "utf-8").decode("unicode_escape")
            return Literal(val)
        
        # Boolean literal
        if t[0] in ("TRUE", "FALSE"):
            v = (self.next()[0] == "TRUE")
            return Literal(v)
        
        # Identifier (variable, function call, or assignment)
        if t[0] == "ID":
            name = self.next()[1]
            
            # Function call
            if self.peek()[1] == "(":
                self.next()
                args = []
                if self.peek()[1] != ")":
                    while True:
                        args.append(self.parse_expr())
                        if self.peek()[1] == ",":
                            self.next()
                            continue
                        break
                self.expect_op(")")
                return FuncCall(name, args)
            
            # Assignment
            if self.peek()[1] == "=":
                self.next()
                val = self.parse_expr()
                return AssignExpr(name, val)
            
            # Variable reference
            return VarRef(name)
        
        # Parenthesized expression
        if t[1] == "(":
            self.next()
            e = self.parse_expr()
            self.expect_op(")")
            return e
        
        raise SyntaxError(f"Unexpected token in expression: {t}")