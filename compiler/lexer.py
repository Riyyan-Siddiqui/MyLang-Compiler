"""
Lexical analyzer (tokenizer) for the compiler
"""
import re
from typing import List, Tuple

Token = Tuple[str, str]  # (type, text)

TOKEN_SPEC = [
    ("COMMENT", r"//[^\n]*"),
    ("WHITESPACE", r"[ \t\r\n]+"),
    ("NUMBER", r"\d+(\.\d+)?"),
    ("STRING", r'"([^"\\]|\\.)*"'),
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP", r"==|!=|<=|>=|&&|\|\||[+\-*/%<>=!;(),{}]"),
]

KEYWORDS = {
    "int", "float", "string", "bool",
    "if", "else", "while", "for", "return", 
    "func", "true", "false", "input", "void"
}

class Lexer:
    """Tokenizes source code into tokens"""
    
    def __init__(self, text: str):
        self.text = text
        self.master_re = re.compile("|".join("(?P<%s>%s)" % pair for pair in TOKEN_SPEC))
    
    def tokenize(self) -> List[Token]:
        """Convert source text to list of tokens"""
        tokens: List[Token] = []
        pos = 0
        
        while pos < len(self.text):
            m = self.master_re.match(self.text, pos)
            if not m:
                raise SyntaxError(f"Unexpected character at pos {pos}: {self.text[pos]!r}")
            
            kind = m.lastgroup
            val = m.group(kind)
            pos = m.end()
            
            # Skip whitespace and comments
            if kind == "WHITESPACE" or kind == "COMMENT":
                continue
            
            # Convert keywords to uppercase token types
            if kind == "ID" and val in KEYWORDS:
                tokens.append((val.upper(), val))
            else:
                tokens.append((kind, val))
        
        tokens.append(("EOF", ""))
        return tokens

def lex(text: str) -> List[Token]:
    """Convenience function for tokenization"""
    lexer = Lexer(text)
    return lexer.tokenize()