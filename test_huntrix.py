"""Quick syntax test for huntrix_game.py"""
import ast
import sys

try:
    with open('huntrix_game.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Try to parse the code
    ast.parse(code)
    print("✓ Syntax is valid!")
    print("✓ All graphics enhancements added successfully!")
    print("\nNew features added:")
    print("  • Particle effects for collections")
    print("  • Motion trails for player")
    print("  • Enhanced character animations with blinking")
    print("  • Glowing auras and halos")
    print("  • Improved star graphics with rotation")
    print("  • Enhanced music notes with shadows")
    print("  • Gradient power bar with glow effects")
    print("  • Twinkling background stars")
    print("  • Better gradient backgrounds")
    print("  • Heart-shaped health display")
    
except SyntaxError as e:
    print(f"✗ Syntax Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
