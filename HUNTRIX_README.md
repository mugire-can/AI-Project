# The Huntrix - K-Pop Adventure Game 🎵

## Enhanced Graphics Features ✨

This version includes significantly improved graphics:

- **Particle Effects**: Colorful sparkles when collecting items
- **Motion Trails**: Smooth trails following the player
- **Character Animations**: Bouncing, blinking eyes, glowing auras
- **Enhanced Collectibles**: Rotating stars with glow effects
- **Visual Polish**: Twinkling background stars, gradients, shadows
- **Better UI**: Heart-shaped health, gradient power bar

## Requirements

- Python 3.6 or higher
- Pygame library

## Installation

1. Install pygame if you haven't already:
```bash
pip install pygame
```

## Running the Game

Simply run:
```bash
python huntrix_game.py
```

Or double-click `huntrix_game.py` if Python is associated with .py files.

## Controls

- **SPACE**: Start game (from menu)
- **1-4**: Select character
- **Arrow Keys**: Move your K-Pop star
- **ESC**: Return to menu

## Troubleshooting

If the game doesn't run:

1. **Check Python version**:
   ```bash
   python --version
   ```
   Should be 3.6+

2. **Check if Pygame is installed**:
   ```bash
   python -c "import pygame; print(pygame.version.ver)"
   ```

3. **Run the test script**:
   ```bash
   python test_game.py
   ```

4. **Common issues**:
   - If you get "ModuleNotFoundError: No module named 'pygame'", run: `pip install pygame`
   - If you get encoding errors, make sure your terminal supports UTF-8
   - On Windows, you might need to use `python` or `py` command

## Game Objective

- Collect golden stars (50 points each)
- Catch music notes (10 points each)
- Level up every 5 stars
- Don't lose all your hearts!

Enjoy the enhanced K-Pop adventure! 🌟
