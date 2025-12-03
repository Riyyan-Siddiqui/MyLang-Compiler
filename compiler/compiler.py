"""
Main compiler interface
"""
from .lexer import lex
from .parser import Parser
from .codegen import CodeGen
from .ast_nodes import Program

def compile_source(source_text: str) -> str:
    """
    Compile source code to Python
    
    Args:
        source_text: Source code string
        
    Returns:
        Generated Python code string
    """
    # Lexical analysis
    tokens = lex(source_text)
    
    # Syntax analysis
    parser = Parser(tokens)
    program = parser.parse()
    
    # Code generation
    codegen = CodeGen(program)
    pycode = codegen.generate()
    
    return pycode