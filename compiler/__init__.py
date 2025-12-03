"""
Simple C-like language compiler
"""
from .compiler import compile_source
from .lexer import lex, Lexer
from .parser import Parser
from .codegen import CodeGen
from .ast_nodes import *

__version__ = "1.0.0"
__all__ = [
    'compile_source',
    'lex',
    'Lexer',
    'Parser',
    'CodeGen',
]