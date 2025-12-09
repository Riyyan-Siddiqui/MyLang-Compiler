
import sys
import argparse
import subprocess
from compiler.compiler import compile_source  # Python transpiler
from compiler.native_compiler import compile_to_native  # Native compiler

EXAMPLE_PROGRAM = r'''
// Example: factorial
func int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        int n1 = n - 1;
        int result = factorial(n1);
        return n * result;
    }
}

func int main() {
    int num = 5;
    int ans = factorial(num);
    print(ans);
    return 0;
}
'''

def main():
    """CLI entry point"""
    ap = argparse.ArgumentParser(
        description="MyLang Compiler - Supports Python transpiler and native compilation"
    )
    ap.add_argument("source", nargs="?", help="Source file (.my)")
    
    # Mode selection
    ap.add_argument(
        "--mode", 
        choices=["python", "native"], 
        default="python",
        help="Compilation mode: 'python' for transpiler, 'native' for executable (default: python)"
    )
    
    # Python transpiler options
    ap.add_argument("--emit", "-o", help="Output file name (for Python mode)", default="out.py")
    
    # Native compiler options
    ap.add_argument("--output", help="Output executable name (for native mode)", default="program")
    
    # Common options
    ap.add_argument("--run", action="store_true", help="Run after compilation")
    
    args = ap.parse_args()

    # Read source
    if args.source:
        with open(args.source, "r", encoding="utf-8") as f:
            src = f.read()
    else:
        src = EXAMPLE_PROGRAM
        print("No source provided: compiling built-in example program...")

    try:
        if args.mode == "python":
            # ===== TRANSPILER MODE (Python) =====
            print(f"[Transpiler Mode] Compiling to Python...")
            pycode = compile_source(src)
            
            with open(args.emit, "w", encoding="utf-8") as f:
                f.write(pycode)
            print(f"✓ Compiled to Python: {args.emit}")
            
            if args.run:
                print(f"\n{'='*50}")
                print("Running Python code:")
                print('='*50)
                subprocess.run([sys.executable, args.emit])
        
        else:
            # ===== NATIVE COMPILER MODE =====
            print(f"[Native Compiler Mode] Compiling to executable...")
            exe_file = compile_to_native(src, args.output)
            
            if args.run:
                print(f"\n{'='*50}")
                print("Running native executable:")
                print('='*50)
                subprocess.run([f"./{exe_file}"])
    
    except Exception as e:
        print(f"Compilation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()