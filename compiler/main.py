#!/usr/bin/env python3
"""
Command-line interface for the compiler
"""
import sys
import argparse
from .compiler import compile_source

EXAMPLE_PROGRAM = r'''
// Example: factorial
func int factorial(int n) {
    int result = 1;
    for (int i = 1; i <= n; i = i + 1) {
        result = result * i;
    }
    return result;
}

func int main() {
    int num = 5;
    int ans = factorial(num);
    print("Factorial is:");
    print(ans);
    return 0;
}
'''

def main():
    """CLI entry point"""
    ap = argparse.ArgumentParser(description="Simple compiler for tiny language -> Python")
    ap.add_argument("source", nargs="?", help="Source file (.my). If omitted, example is compiled")
    ap.add_argument("--emit", "-o", help="Output Python file name (default: out.py)", default="out.py")
    ap.add_argument("--run", action="store_true", help="Run the generated program after compilation")
    args = ap.parse_args()

    if args.source:
        with open(args.source, "r", encoding="utf-8") as f:
            src = f.read()
    else:
        src = EXAMPLE_PROGRAM
        print("No source provided: compiling built-in example program...")

    try:
        pycode = compile_source(src)
    except Exception as e:
        print("Compilation error:", e)
        sys.exit(1)

    with open(args.emit, "w", encoding="utf-8") as f:
        f.write(pycode)
    print(f"Compiled -> {args.emit}")

    if args.run:
        print("Running generated program:")
        import subprocess
        subprocess.run([sys.executable, args.emit])

if __name__ == "__main__":
    main()