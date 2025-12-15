#!/usr/bin/env python
"""Quick syntax check for snake.py"""

try:
    import snake
    print("✓ snake.py imports successfully - no syntax errors!")
except SyntaxError as e:
    print(f"✗ Syntax Error: {e}")
    print(f"  Line {e.lineno}: {e.text}")
except Exception as e:
    print(f"✓ File parsed OK (runtime error expected without pygame running)")
    print(f"  Note: {type(e).__name__}: {e}")
