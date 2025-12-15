"""
Simple launcher for Huntrix Game
Provides better error messages
"""
import sys

try:
    print("=" * 60)
    print("  THE HUNTRIX - K-POP ADVENTURE GAME")
    print("=" * 60)
    print("\nStarting game...\n")
    
    import pygame
    print(f"✓ Pygame {pygame.version.ver} loaded")
    
    import huntrix_game
    print("✓ Game module loaded")
    print("\nLaunching game window...")
    print("-" * 60)
    
    game = huntrix_game.Game()
    game.run()
    
except ImportError as e:
    print(f"\n✗ ERROR: Missing module - {e}")
    print("\nPlease install pygame:")
    print("  pip install pygame")
    input("\nPress Enter to exit...")
    sys.exit(1)
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)
