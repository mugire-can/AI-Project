# Game Collection - Games Branch

This branch contains all game projects built with Python and Pygame, including turn-based strategy games, racing games, and classic arcade titles.

## Games Included

### 1. Worms Rumble - Battle Edition (`worms_rumble.py`)
A local, turn-based arena inspired by classic artillery/"worms" games with playable demo.

**Controls**:
- Move: Left / Right or A / D
- Jump: Up or W
- Aim: Q / E
- Fire: Space
- Switch worm: Tab
- Pause / Menu: ESC

**Quick Start**:
```powershell
python worms_rumble.py
```

**Requirements**: Python 3.8+, pygame

---

### 2. Snake Game (`snake.py`)
Classic Snake game built with Pygame.
- **Controls**: Arrow keys to move
- **Objective**: Eat red food to grow longer
- **Game Over**: Press Q to quit, C to play again

**Run**:
```bash
python snake.py
```

---

### 3. Huntrix Game (`huntrix_game.py`)
An engaging puzzle/adventure game with multiple levels.

**Run**:
```bash
python huntrix_game.py
```

---

### 4. Racing Games
- **Ultimate Racing Pro** (`ultimate_racing_pro.py`) - Advanced racing simulator
- **NFS Racing** (`nfs_racing.py`) - Need for Speed style game
- **Racing Simple** (`racing_simple.py`) - Basic racing game

**Run any racing game**:
```bash
python ultimate_racing_pro.py
```

---

### 5. Bomberman (`bomberman.py`)
Classic Bomberman-style action game with multiplayer support.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mugire-can/AI-Project.git
cd AI-Project
```

2. Switch to Games branch:
```bash
git checkout Games
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## System Requirements
- Python 3.8+
- Pygame
- 100MB free disk space for assets

## Notes
- Games will generate sound assets under `assets/sounds/` if not present
- For better visuals, add sprite assets and tilesets
- All games use local multiplayer (no network play)

## Author

mugire-can

## License

MIT
