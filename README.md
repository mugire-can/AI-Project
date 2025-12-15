# Worms Rumble - Battle Edition

This is a local, turn-based arena inspired by classic artillery/"worms" games. The project includes a playable demo written with pygame.

Quick start (Windows PowerShell):

```powershell
cd 'c:\Users\mugir\OneDrive\Belgeler\btp-projet-ia'
python .\worms_rumble.py
```

Controls
- Move: Left / Right or A / D
- Jump: Up or W
- Aim: Q / E
- Fire: Space
- Switch worm: Tab
- Pause / Menu: ESC

Notes
- The game will generate small example WAV files under `assets/sounds/` if none are present. Replace them with better assets to improve audio.
- To get better visuals, add sprite assets and a tileset and I can integrate them.

Requirements
- Python 3.8+
- pygame

Install dependencies:

```powershell
pip install -r requirements.txt
```

If you want, I can also add placeholder PNG sprite assets and a small sample sound pack to make the demo feel more polished out-of-the-box—tell me and I'll add them.

-- End
# AI Project

Collection of Python projects including games, image downloaders, and marketing content generators.

## Projects Included

### 1. Snake Game (`snake.py`)
Classic Snake game built with Pygame.
- **Controls**: Arrow keys to move
- **Objective**: Eat red food to grow longer
- **Game Over**: Press Q to quit, C to play again

**Requirements**:
```bash
pip install pygame
```

**Run**:
```bash
python snake.py
```

### 2. King Cobra Image Downloader (`download_cobra.py`)
Downloads king cobra images from Unsplash API.

**Requirements**:
```bash
pip install requests
```

**Run**:
```bash
python download_cobra.py
```

### 3. PACA Regional Jingle (`jingle_paca.txt` & `generate_jingle_audio.py`)
Marketing jingle for a French regional application selling fresh fruits and vegetables.
- **Text file**: Contains complete lyrics and production notes
- **Audio generator**: Creates female-voiced MP3 file

**Requirements**:
```bash
pip install gTTS
```

**Run**:
```bash
python generate_jingle_audio.py
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mugire-can/AI-Project.git
cd AI-Project
```

2. Install dependencies:
```bash
pip install pygame requests gTTS
```

## Author

mugire-can

## License

MIT
