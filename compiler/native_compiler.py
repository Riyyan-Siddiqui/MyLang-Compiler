import subprocess
import sys
import os
from pathlib import Path

try:
    from .lexer import lex
    from .parser import Parser
    from .codegen_c import CCodeGen
except ImportError:
    from lexer import lex
    from parser import Parser
    from codegen_c import CCodeGen

def compile_to_native(source_text: str, output_name: str = "a.out"):
    """
    Compile source code to native executable
    
    Args:
        source_text: Source code string
        output_name: Name of output executable
        
    Returns:
        Path to generated executable
    """
    # Lexical analysis
    tokens = lex(source_text)
    
    # Syntax analysis
    parser = Parser(tokens)
    program = parser.parse()
    
    # Code generation to C
    codegen = CCodeGen(program)
    c_code = codegen.generate()
    
    # Write C file
    c_file = output_name + ".c"
    with open(c_file, "w") as f:
        f.write(c_code)
        f.write("\n")
    
    print(f"✓ Generated C code: {c_file}")
    
    # Compile with GCC
    exe_file = output_name + (".exe" if sys.platform == "win32" else "")
    
    # Different compile commands based on platform
    if sys.platform == "win32":
        # Windows with MinGW - add workaround flags
        gcc_cmd = [
            "gcc", 
            "-std=c99",
            "-static-libgcc",  # Static linking
            c_file, 
            "-o", exe_file,
            "-lmingw32"  # Link against mingw32
        ]
    else:
        # Linux/Mac - standard compilation
        gcc_cmd = ["gcc", "-std=c99", c_file, "-o", exe_file]
    
    try:
        result = subprocess.run(
            gcc_cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("GCC compilation failed:")
            print(result.stderr)
            
            # Try alternative compilation method
            print("\nTrying alternative compilation...")
            alt_cmd = ["gcc", "-std=c99", "-m32", c_file, "-o", exe_file]
            result2 = subprocess.run(alt_cmd, capture_output=True, text=True)
            
            if result2.returncode != 0:
                print("Alternative compilation also failed:")
                print(result2.stderr)
                sys.exit(1)
        
        print(f"✓ Compiled to native executable: {exe_file}")
        return exe_file
        
    except FileNotFoundError:
        print("ERROR: GCC not found!")
        print("Please install GCC:")
        print("  Windows: Install TDM-GCC (recommended) or MinGW-w64")
        print("  Linux: sudo apt install gcc")
        print("  Mac: xcode-select --install")
        sys.exit(1)