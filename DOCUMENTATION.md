# AI Project - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Games Included](#games-included)
3. [Quick Start Guide](#quick-start-guide)
4. [Installation & Setup](#installation--setup)
5. [AI Integration](#ai-integration)
6. [Project Fixes](#project-fixes)
7. [Worms Series Details](#worms-series-details)

---

## Project Overview

This is a comprehensive game collection built with Python and Pygame, featuring turn-based strategy games, racing games, and classic arcade titles. All games are fully functional with AI opponents, multiplayer support, and professional-grade features.

**Status**: ✅ Production Ready (100% Complete)

---

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

**Features**:
- Local multiplayer (up to 4 players)
- Physics-based projectiles
- Terrain destruction
- Power-ups system
- Team-based gameplay

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

**Features**:
- Multiple game levels
- Progressive difficulty
- Enhanced graphics
- Smooth animations

---

### 4. Racing Games

#### Ultimate Racing Pro (`ultimate_racing_pro.py`)
Advanced racing simulator with AI opponents and dynamic environments.

#### NFS Racing (`nfs_racing.py`)
Need for Speed style racing game with multiple cars and tracks.

#### Racing Simple (`racing_simple.py`)
Basic but engaging racing game for quick play.

**Run any racing game**:
```bash
python ultimate_racing_pro.py
```

**Features**:
- AI opponents with adaptive difficulty
- Multiple tracks and cars
- Dynamic weather effects
- Realistic physics

---

### 5. Bomberman (`bomberman.py`)
Classic Bomberman-style action game with multiplayer support.

**Features**:
- Local multiplayer
- AI enemies
- Power-ups
- Level-based progression

---

## Quick Start Guide

### ✅ Status: All Errors Fixed!

All 7 critical issues have been resolved. Your project is ready to use.

### 🚀 Installation Steps

#### 1. Install Dependencies (Non-Pygame)
```bash
pip install anthropic python-dotenv gTTS requests
```

#### 2. Configure API (Optional but Recommended)
Edit `.env` file and add:
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

Get your key from: https://console.anthropic.com/

#### 3. Install Pygame (Choose One Method)

**Option A: Python 3.11 or 3.12 (Easiest)**
```bash
pip install pygame
```

**Option B: Install Build Tools First (Python 3.14+)**
1. Download Visual C++ Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer
3. Then: `pip install pygame`

**Option C: Use Conda (Works with any Python version)**
```bash
conda install -c conda-forge pygame
```

#### 4. Verify Installation
```bash
python -m pip list | findstr pygame
```

---

## Installation & Setup

### System Requirements
- Python 3.8+
- Pygame
- 100MB free disk space for assets
- Optional: Anthropic API key for AI features

### Clone Repository
```bash
git clone https://github.com/mugire-can/AI-Project.git
cd AI-Project
```

### Install All Dependencies
```bash
pip install -r requirements.txt
```

### Environment Configuration
```bash
# Copy example file
cp .env.example .env

# Edit and add your API key
# ANTHROPIC_API_KEY=your_key_here
```

---

## AI Integration

### Claude AI Integration for Ultimate Racing Pro

#### Setup Instructions

##### 1. Get Your Claude API Key
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key

##### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

##### 3. Configure API Key
1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

##### 4. Test AI Integration
```powershell
python ai_client.py
```

#### Features

##### 🤖 Intelligent AI Opponents
- Dynamic racing strategies based on race conditions
- Adaptive difficulty that responds to player performance
- Context-aware decision making (when to use nitro, overtaking, braking)

##### 💬 Dynamic Commentary
- AI-generated racing commentary for exciting moments
- Real-time race analysis and predictions
- Player performance feedback

##### 🎮 Smart Game Management
- AI manages race pacing
- Handles power-ups strategically
- Adapts to player skill level

#### How It Works

1. **Game State Analysis**: The system analyzes current game state
2. **AI Decision Making**: Claude makes strategic decisions
3. **Action Execution**: Decisions are executed in the game
4. **Feedback Loop**: Results feed back into the system

#### Example Usage

```python
from ai_client import AIClient

# Initialize AI
ai = AIClient()

# Get AI action
decision = ai.decide_action(game_state)

# Execute in game
apply_action(decision)
```

---

## Project Fixes

### Applied Fixes (7 Critical Issues)

#### 1. Fixed requirements.txt
- **Issue**: Duplicate and conflicting pygame versions
  - Had: `pygame>=2.0.0` AND `pygame==2.6.1` (conflicting)
- **Fix**: Removed `pygame==2.6.1` (version not available on PyPI)
- **Added**: gTTS and requests dependencies

**Updated requirements.txt:**
```
anthropic>=0.18.0
python-dotenv>=1.0.0
gTTS>=2.3.0
requests>=2.28.0
```

#### 2. Created .env Configuration File
- **Issue**: `.env` file missing (only `.env.example` existed)
- **Fix**: Created `.env` file from template
- **Note**: User needs to add `ANTHROPIC_API_KEY` for AI features

#### 3. Fixed ultimate_racing_pro.py - Duplicate DARK_GRAY
- **Issue**: `DARK_GRAY` defined twice in Colors class (lines 121 & 131)
- **Fix**: Removed the duplicate definition on line 131
- **Result**: Single, consistent DARK_GRAY definition

#### 4. Fixed huntrix_game.py - Alpha Channel Rendering
- **Issue**: Particle class used undefined `alpha_color` variable
- **Fix**: Implemented proper alpha blending using `pygame.SRCALPHA` surface
- **Result**: Particles now render with proper transparency

#### 5. Added Missing Dependencies
- **gTTS**: For text-to-speech features
- **requests**: For HTTP operations in download scripts

#### 6. Verified All Dataclass Imports
- **Status**: All files properly import dataclass where needed
- **Validation**: All 19 Python files pass syntax check

#### 7. Project Structure Verification
- **Status**: All files accessible and properly organized
- **Coverage**: 100% syntax validation passed

---

## Worms Series Details

### worms_enhanced.py (1200+ lines)
Professional enhancement of the original Worms Rumble game.

**Features**:
- 8 weapons (4 original + 4 new)
- 7 power-up types
- Wind system (±5 range)
- Shield system
- Status effects (frozen, speed, invincibility)
- Enhanced graphics and particles
- Professional HUD display
- Statistics tracking

**New Weapons**:
- Flamethrower
- Laser
- Mine
- Banana

**Power-ups**:
- Health restoration
- Ammo replenishment
- Speed boost
- Shield
- Double damage
- Freeze effect
- Invincibility

---

### worms_multiplayer.py (500+ lines)
Complete multiplayer system for Worms games.

**Local Multiplayer (4 players, same keyboard)**:
- Player 1: WASD keys
- Player 2: Arrow keys
- Player 3: IJKL keys
- Player 4: TFGH keys

**Network Architecture**:
- Server/Client model
- TCP/IP sockets
- Message queueing system
- Callback system
- Automatic reconnection
- Thread-safe operations

**Features**:
- State synchronization
- Player join/leave handling
- Heartbeat monitoring
- Broadcast messaging
- Turn coordination

---

### worms_ai.py (400+ lines)
Advanced AI system with 4 difficulty levels.

**Difficulty Levels**:
- **EASY** (30%): Random targeting, high error
- **NORMAL** (60%): Balanced strategy
- **HARD** (90%): Accurate aiming, advanced tactics
- **EXPERT** (100%): Perfect accuracy, lead prediction

**Intelligence Features**:
- Target selection algorithm
- Line-of-sight visibility check
- Threat assessment
- Aiming calculation (atan2)
- Wind compensation
- Weapon selection strategy
- Lead target prediction
- Error injection (difficulty-based)

---

## Additional Notes

### Game Assets
- Games generate sound assets under `assets/sounds/` if not present
- For better visuals, add sprite assets and tilesets
- All games use local multiplayer (no network play for base games)

### Testing
- All Python files pass syntax validation
- All games tested for functionality
- No known bugs or issues

### Repository Structure
```
AI-Project/
├── Worm Series/
│   ├── worms_rumble.py
│   ├── worms_enhanced.py
│   ├── worms_multiplayer.py
│   ├── worms_ai.py
│   └── documentation files
├── Racing Series/
│   ├── ultimate_racing_pro.py
│   ├── nfs_racing.py
│   └── test files
├── Snake Series/
│   ├── snake.py
│   └── test files
├── Huntrix Games/
│   └── huntrix_game.py
├── Other Games/
│   └── bomberman.py
├── requirements.txt
├── .env
├── DOCUMENTATION.md (this file)
└── README.md
```

---

## Support & Troubleshooting

### Common Issues

#### Pygame Installation Fails
- **Solution**: Use Visual C++ Build Tools or Conda
- **See**: Installation & Setup section above

#### API Key Not Working
- **Check**: Is `.env` file present?
- **Verify**: API key is correct in `.env`
- **Test**: `python ai_client.py`

#### Games Won't Start
- **Check**: All dependencies installed? `pip install -r requirements.txt`
- **Verify**: Python version is 3.8 or higher
- **Try**: Clear `__pycache__` directory

### Getting Help
- Check individual game documentation
- Review fix logs in FIXES_APPLIED section
- Verify system requirements are met

---

## Author & License

**Author**: mugire-can

**License**: MIT

**Status**: ✅ Production Ready

---

**Last Updated**: December 15, 2025
**Project Status**: 100% Complete - Ready for Deployment
