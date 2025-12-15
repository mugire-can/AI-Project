# Worms Rumble - Game Analysis & Overview

## 📊 Game Statistics

- **File**: `worms_rumble.py`
- **Lines of Code**: 962 lines
- **Type**: Turn-based artillery/strategy game
- **Players**: Up to 4 teams with multiple worms each
- **Genre**: Inspired by classic "Worms" games

---

## 🎮 Game Features

### Core Gameplay
- **Turn-based combat**: Each worm takes turns to move and attack
- **Physics simulation**: Gravity, terrain destruction, projectile physics
- **Multiple weapons**: Pistol, Shotgun, Rocket, Grenade (each with unique properties)
- **Terrain destruction**: Destructible landscape that changes during gameplay
- **Dynamic difficulty**: AI adjusts strategy based on game state

### Game Mechanics

#### Movement
- **Controls**: Arrow keys or WASD
- **Jump**: Up or W (only when on ground)
- **Friction**: Movement slows naturally
- **Boundaries**: Screen edges bounce/limit movement

#### Combat System
- **Aiming**: Q/E keys to adjust angle (0-90 degrees)
- **Power**: Determines projectile velocity
- **Weapon Types**:
  - **Pistol**: Single shot, low damage, high accuracy
  - **Shotgun**: Wide spread, medium range
  - **Rocket**: Explosive with large AOE damage
  - **Grenade**: Time-delayed explosion
- **Ammo System**: Each weapon has limited ammo

#### Terrain
- **Tile-based**: 20px tiles
- **Destructible**: Explosions remove terrain
- **Procedural generation**: Random terrain each game
- **Collisions**: Affects worm movement and projectiles

#### Team/Worm System
- **Teams**: Up to 4 teams
- **Worms per team**: Multiple worms
- **Health system**: 100 HP per worm
- **Team colors**: Different color per team
- **Switching**: Tab key to switch active worm
- **Victory**: Last team with living worms wins

---

## 🏗️ Code Architecture

### Main Classes

#### 1. **Particle**
```python
class Particle:
    - Handles visual effects (explosions, trail effects)
    - Alpha blending for fading
    - Physics simulation (gravity, velocity)
```

#### 2. **Projectile**
```python
class Projectile:
    - Fired weapons
    - Trail particle effects
    - Weapon type tracking
    - Lifetime management
    - Damage calculation
```

#### 3. **Explosion**
```python
class Explosion:
    - Damage radius effects
    - Expanding animation
    - Terrain destruction
    - Alpha-blended rendering
```

#### 4. **Terrain**
```python
class Terrain:
    - Tile-based map (grid)
    - Procedural generation
    - Collision detection
    - Damage/destruction
    - Solid surface tracking
```

#### 5. **Worm** (Player/AI unit)
```python
class Worm:
    - Position & velocity
    - Health system
    - Current weapon & ammo
    - Aiming (angle/power)
    - Input handling
    - Physics (gravity, jumping)
    - Particle effects
    - AI firing logic
```

#### 6. **Team** (Group of worms)
```python
class Team:
    - Multiple worms
    - Team color
    - Score tracking
    - Victory/defeat status
```

#### 7. **Game** (Main logic)
```python
class Game:
    - Game state management
    - Turn system
    - Physics updates
    - Collision handling
    - AI turns
    - Rendering
    - Input processing
```

---

## 🎯 Game Loop Flow

```
1. Initialize → Create terrain, teams, worms
2. Main Loop:
   a. Event handling (quit, ESC menu)
   b. Input processing (movement, aiming, firing)
   c. Update physics (gravity, collisions)
   d. Update projectiles & explosions
   e. Check win conditions
   f. Handle turn rotation
   g. AI execution (if AI worm's turn)
   h. Render frame
3. End → Display winner
```

---

## 🤖 AI System

### AI Features
- **Target selection**: Chooses nearest enemy
- **Pathfinding**: Moves toward target when possible
- **Aiming**: Calculates angle to hit target
- **Power adjustment**: Random power for unpredictability
- **Weapon selection**: Chooses appropriate weapon

### AI Firing Logic
```python
def ai_fire_at(target_x, target_y):
    - Calculate angle using atan2
    - Adjust to valid range (10-170°)
    - Set random power (30-80)
    - Fire projectile
```

---

## 🎨 Visual Features

### Rendering System
- **Particle effects**: 
  - Explosion trails
  - Projectile trails
  - Impact effects
- **Terrain visualization**: Tile-based with different colors
- **Alpha blending**: Smooth fading effects
- **Health bars**: Visual health display per worm
- **HUD**: Current weapon, ammo, angle, power display

### Asset Generation
- **Runtime asset creation**: Generates sprites in code (no external files needed)
- **Placeholder sprites**:
  - Tiles (terrain)
  - Worms (player units)
  - Projectiles (weapons)
  - Explosions (visual effects)
- **Dynamic asset saving**: Exports generated assets to disk

### Sound System
- **Procedural audio**: Generates WAV files at runtime
- **Sounds**: Fire, explosion, jump
- **Synthesis**: Sine-wave based audio generation

---

## ⚙️ Key Game Constants

```python
WIDTH = 1200          # Screen width
HEIGHT = 600          # Screen height
FPS = 60              # Frame rate
GRAVITY = 0.4         # Gravity acceleration
TILE_SIZE = 20        # Terrain tile size

Weapons:
- PISTOL: 2 ammo, 20 damage, 40 power
- SHOTGUN: 1 ammo, 40 damage, 60 power
- ROCKET: 1 ammo, 50 damage, 80 power
- GRENADE: 1 ammo, 60 damage, 100 power
```

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| **Arrow Keys / WASD** | Move worm |
| **Up / W** | Jump |
| **Q / E** | Aim angle (up/down) |
| **Space** | Fire weapon |
| **Tab** | Switch to next worm |
| **1-4** | Select weapon |
| **ESC** | Pause / Menu |

---

## 🏆 Victory Conditions

- Last team with living worms wins
- Teams eliminated when all worms destroyed
- Health reaches 0 = worm dead
- Falling off map = instant death

---

## 🐛 Potential Improvements

1. **Networking**: Multiplayer over network
2. **More weapons**: Add more weapon types
3. **Power-ups**: Health, ammo, shield pickups
4. **Terrain features**: Hills, water, obstacles
5. **Better graphics**: Animated sprites, effects
6. **Sound effects**: Better audio variety
7. **Campaign mode**: Level progression
8. **Customization**: Worm skins, team colors

---

## 📝 Code Highlights

### Physics Implementation
```python
def update(self, terrain):
    # Apply gravity
    self.vy += GRAVITY
    
    # Update position
    self.x += self.vx
    self.y += self.vy
    
    # Terrain collision
    if terrain.is_solid(self.x, self.y + self.radius):
        self.on_ground = True
        self.vy = 0
```

### Damage Calculation
```python
def apply_damage(self, damage):
    if self.invulnerable_time > 0:
        return
    self.health -= damage
    if self.health <= 0:
        self.health = 0
```

### Projectile Firing
```python
def fire(self):
    # Calculate velocity from angle and power
    rad = math.radians(self.angle)
    vx = self.power * math.cos(rad)
    vy = -self.power * math.sin(rad)
    
    # Create projectile
    projectile = Projectile(self.x, self.y, vx, vy, 
                           self.current_weapon, self.worm_id)
    return projectile
```

---

## 🚀 How to Run

```bash
python worms_rumble.py
```

**Requirements**:
- pygame (for graphics & input)
- Python 3.8+

---

## 📚 Related Files

- `run_worms.py` - Alternative launcher script
- `assets/images/` - Terrain and sprite assets
- `assets/sounds/` - Game sounds

---

## ✨ Summary

Worms Rumble is a fully functional turn-based strategy game with:
- ✅ Complete physics engine
- ✅ Destructible terrain
- ✅ Multiple weapons
- ✅ AI opponents
- ✅ Team system
- ✅ Dynamic asset generation
- ✅ Particle effects
- ✅ Sound synthesis

**Status**: FULLY FUNCTIONAL & ERROR-FREE ✅
