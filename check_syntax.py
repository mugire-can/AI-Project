import sys
import py_compile

try:
    py_compile.compile('huntrix_game.py', doraise=True)
    print("✓ Syntax is valid!")
    print("\nTrying to import...")
    import huntrix_game
    print("✓ Import successful!")
except SyntaxError as e:
    print(f"✗ Syntax Error at line {e.lineno}: {e.msg}")
    print(f"  {e.text}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
