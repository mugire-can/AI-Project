"""
Test runner for snake.py - shows detailed error messages
"""
import sys
import traceback

print("=" * 60)
print("Testing ULTIMATE SNAKE PRO")
print("=" * 60)

try:
    print("\n1. Checking Python syntax...")
    with open('snake.py', 'r', encoding='utf-8') as f:
        code = f.read()
    compile(code, 'snake.py', 'exec')
    print("   ✓ Syntax OK")
    
    print("\n2. Checking imports...")
    import pygame
    print("   ✓ pygame found")
    
    print("\n3. Loading snake module...")
    import snake
    print("   ✓ Module loaded")
    
    print("\n4. Attempting to start game...")
    print("   (Press ESC or close window to exit)\n")
    snake.main()
    
except SyntaxError as e:
    print(f"\n✗ SYNTAX ERROR:")
    print(f"   File: {e.filename}")
    print(f"   Line {e.lineno}: {e.text}")
    print(f"   {' ' * (e.offset - 1)}^")
    print(f"   {e.msg}")
    
except ImportError as e:
    print(f"\n✗ IMPORT ERROR: {e}")
    print("   Make sure pygame is installed: pip install pygame")
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}")
    print(f"   {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
