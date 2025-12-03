"""
AST Node definitions for the compiler
"""
from typing import List, Tuple, Optional, Any

class ASTNode:
    """Base class for all AST nodes"""
    pass

# Program structure
class Program(ASTNode):
    def __init__(self, funcs: List['FuncDecl']):
        self.funcs = funcs

class FuncDecl(ASTNode):
    def __init__(self, return_type: str, name: str, params: List[Tuple[str,str]], body: List['Stmt']):
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body

# Statements
class Stmt(ASTNode):
    """Base class for statements"""
    pass

class VarDecl(Stmt):
    def __init__(self, vtype: str, names: List[Tuple[str, Optional['Expr']]]):
        self.vtype = vtype
        self.names = names  # list of (name, optional initializer)

class ExprStmt(Stmt):
    def __init__(self, expr: 'Expr'):
        self.expr = expr

class IfStmt(Stmt):
    def __init__(self, cond: 'Expr', then_block: List[Stmt], else_block: Optional[List[Stmt]]):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block

class WhileStmt(Stmt):
    def __init__(self, cond: 'Expr', body: List[Stmt]):
        self.cond = cond
        self.body = body

class ForStmt(Stmt):
    def __init__(self, init: Optional[Stmt], cond: Optional['Expr'], post: Optional['Expr'], body: List[Stmt]):
        self.init = init
        self.cond = cond
        self.post = post
        self.body = body

class ReturnStmt(Stmt):
    def __init__(self, expr: Optional['Expr']):
        self.expr = expr

# Expressions
class Expr(ASTNode):
    """Base class for expressions"""
    pass

class BinaryExpr(Expr):
    def __init__(self, left: Expr, op: str, right: Expr):
        self.left = left
        self.op = op
        self.right = right

class UnaryExpr(Expr):
    def __init__(self, op: str, expr: Expr):
        self.op = op
        self.expr = expr

class Literal(Expr):
    def __init__(self, value: Any):
        self.value = value

class VarRef(Expr):
    def __init__(self, name: str):
        self.name = name

class AssignExpr(Expr):
    def __init__(self, name: str, value: Expr):
        self.name = name
        self.value = value

class FuncCall(Expr):
    def __init__(self, name: str, args: List[Expr]):
        self.name = name
        self.args = args