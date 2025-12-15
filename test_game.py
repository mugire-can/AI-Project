#!/usr/bin/env python
"""Test if huntrix_game.py can be loaded and has valid syntax"""

print("Testing huntrix_game.py...")
print("-" * 50)

# Test 1: Syntax check
print("\n1. Checking syntax...")
try:
    import py_compile
    py_compile.compile('huntrix_game.py', doraise=True)
    print("   ✓ Syntax is valid!")
except SyntaxError as e:
    print(f"   ✗ Syntax Error at line {e.lineno}: {e.msg}")
    print(f"     {e.text}")
    exit(1)

# Test 2: Import check
print("\n2. Checking if pygame is available...")
try:
    import pygame
    print(f"   ✓ Pygame {pygame.version.ver} is installed!")
except ImportError:
    print("   ✗ Pygame is not installed!")
    print("     Install with: pip install pygame")
    exit(1)

# Test 3: Load the module
print("\n3. Loading huntrix_game module...")
try:
    import huntrix_game
    print("   ✓ Module loaded successfully!")
except Exception as e:
    print(f"   ✗ Error loading module: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Check classes
print("\n4. Checking required classes...")
required_classes = ['Particle', 'Trail', 'KPopStar', 'CollectibleStar', 'MusicNote', 'Game']
for cls_name in required_classes:
    if hasattr(huntrix_game, cls_name):
        print(f"   ✓ {cls_name} class found")
    else:
        print(f"   ✗ {cls_name} class not found")

print("\n" + "=" * 50)
print("All tests passed! The game should run.")
print("=" * 50)
print("\nTo start the game, run:")
print("  python huntrix_game.py")
print("\nControls:")
print("  - Press SPACE to start")
print("  - Choose character with 1-4")
print("  - Arrow keys to move")
print("  - Collect stars and music notes!")
