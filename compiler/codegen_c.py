"""
Code generator: converts AST to C code (native compilation)
"""
from typing import List

try:
    from .ast_nodes import *
except ImportError:
    from ast_nodes import *

class CCodeGen:
    """Generates C code from AST for native compilation"""
    
    def __init__(self, program: Program):
        self.program = program
        self.out_lines: List[str] = []
        self.indent_level = 0
        self.func_names = {f.name for f in program.funcs}

    def emit(self, line: str = ""):
        """Emit a line of code with proper indentation"""
        self.out_lines.append("    " * self.indent_level + line)

    def generate(self) -> str:
        """Generate complete C program"""
        # Headers
        self.emit("#include <stdio.h>")
        self.emit("#include <stdlib.h>")
        self.emit("#include <string.h>")
        self.emit("#include <stdbool.h>")
        self.emit("")
        
        # Forward declarations for all functions
        for f in self.program.funcs:
            ret_type = self.map_type(f.return_type)
            if f.params:
                params = ", ".join(f"{self.map_type(ptype)} {pname}" 
                                 for ptype, pname in f.params)
            else:
                params = "void"
            self.emit(f"{ret_type} {f.name}({params});")
        self.emit("")
        
        # Generate all functions
        for f in self.program.funcs:
            self.gen_function(f)
            self.emit("")
        
        return "\n".join(self.out_lines)

    def map_type(self, typ: str) -> str:
        """Map language types to C types"""
        type_map = {
            "int": "int",
            "float": "double",
            "string": "char*",
            "bool": "bool",
            "void": "void"
        }
        return type_map.get(typ, "int")

    def gen_function(self, f: FuncDecl):
        """Generate C function definition"""
        ret_type = self.map_type(f.return_type)
        
        # Parameters
        if f.params:
            params = ", ".join(f"{self.map_type(ptype)} {pname}" 
                             for ptype, pname in f.params)
        else:
            params = "void"
        
        self.emit(f"{ret_type} {f.name}({params}) {{")
        self.indent_level += 1
        
        for stmt in f.body:
            self.gen_stmt(stmt)
        
        # Ensure return for non-void functions
        if f.return_type != "void" and not any(isinstance(s, ReturnStmt) for s in f.body):
            self.emit("return 0;")
        
        self.indent_level -= 1
        self.emit("}")

    def gen_stmt(self, s: Stmt):
        """Generate C code for a statement"""
        if isinstance(s, VarDecl):
            c_type = self.map_type(s.vtype)
            for name, init in s.names:
                if init is None:
                    self.emit(f"{c_type} {name};")
                else:
                    expr = self.gen_expr(init)
                    self.emit(f"{c_type} {name} = {expr};")
            return
        
        if isinstance(s, ExprStmt):
            self.emit(self.gen_expr(s.expr) + ";")
            return
        
        if isinstance(s, IfStmt):
            cond = self.gen_expr(s.cond)
            self.emit(f"if ({cond}) {{")
            self.indent_level += 1
            for st in s.then_block:
                self.gen_stmt(st)
            self.indent_level -= 1
            
            if s.else_block is not None:
                self.emit("} else {")
                self.indent_level += 1
                for st in s.else_block:
                    self.gen_stmt(st)
                self.indent_level -= 1
            
            self.emit("}")
            return
        
        if isinstance(s, WhileStmt):
            cond = self.gen_expr(s.cond)
            self.emit(f"while ({cond}) {{")
            self.indent_level += 1
            for st in s.body:
                self.gen_stmt(st)
            self.indent_level -= 1
            self.emit("}")
            return
        
        if isinstance(s, ForStmt):
            # C89-compatible: declare variables BEFORE the loop
            init_vars = []
            
            if s.init and isinstance(s.init, VarDecl):
                # Declare variables before loop
                c_type = self.map_type(s.init.vtype)
                for name, init_expr in s.init.names:
                    self.emit(f"{c_type} {name};")
                    if init_expr:
                        init_vars.append(f"{name} = {self.gen_expr(init_expr)}")
            
            # Build for statement
            if init_vars:
                init_str = "; ".join(init_vars)
            elif s.init and isinstance(s.init, ExprStmt):
                init_str = self.gen_expr(s.init.expr)
            else:
                init_str = ""
            
            cond_str = self.gen_expr(s.cond) if s.cond else "1"
            post_str = self.gen_expr(s.post) if s.post else ""
            
            self.emit(f"for ({init_str}; {cond_str}; {post_str}) {{")
            self.indent_level += 1
            for st in s.body:
                self.gen_stmt(st)
            self.indent_level -= 1
            self.emit("}")
            return
        
        if isinstance(s, ReturnStmt):
            if s.expr is None:
                self.emit("return;")
            else:
                self.emit(f"return {self.gen_expr(s.expr)};")
            return

    def gen_expr(self, e: Expr) -> str:
        """Generate C expression string"""
        if isinstance(e, Literal):
            if isinstance(e.value, str):
                # Escape string for C
                v = e.value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
                return f'"{v}"'
            if isinstance(e.value, bool):
                return "true" if e.value else "false"
            return str(e.value)
        
        if isinstance(e, VarRef):
            return e.name
        
        if isinstance(e, AssignExpr):
            val = self.gen_expr(e.value)
            return f"{e.name} = {val}"
        
        if isinstance(e, BinaryExpr):
            left = self.gen_expr(e.left)
            right = self.gen_expr(e.right)
            op = e.op
            return f"({left} {op} {right})"
        
        if isinstance(e, UnaryExpr):
            expr = self.gen_expr(e.expr)
            op = e.op
            return f"({op}{expr})"
        
        if isinstance(e, FuncCall):
            if e.name == "print":
                # Map to printf
                if len(e.args) == 0:
                    return 'printf("\\n")'
                
                arg = e.args[0]
                arg_str = self.gen_expr(arg)
                
                # Determine format based on argument type
                if isinstance(arg, Literal):
                    if isinstance(arg.value, str):
                        return f'printf("%s\\n", {arg_str})'
                    elif isinstance(arg.value, float):
                        return f'printf("%f\\n", {arg_str})'
                    elif isinstance(arg.value, bool):
                        return f'printf("%s\\n", {arg_str} ? "true" : "false")'
                    else:
                        return f'printf("%d\\n", {arg_str})'
                else:
                    # Default to integer format
                    return f'printf("%d\\n", {arg_str})'
            
            if e.name == "input":
                return "getchar()"
            
            args = ", ".join(self.gen_expr(a) for a in e.args)
            return f"{e.name}({args})"