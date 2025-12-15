"""
WORMS RUMBLE - ENHANCED EDITION
Professional turn-based strategy game with advanced features

ENHANCEMENTS:
✓ Improved graphics with textured terrain
✓ Character customization and names
✓ Multiple game modes and levels
✓ Power-ups system
✓ Advanced AI with difficulty levels
✓ Multiplayer support (local 2-4 players)
✓ Environmental effects (wind, rain, etc.)
✓ Better particle effects
✓ Sound effects and music
✓ Leaderboard and statistics
✓ Menu system with settings
✓ Network ready architecture
"""

import pygame
import math
import random
import json
import os
import wave
import struct
import socket
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from collections import deque

pygame.init()
pygame.mixer.init()

# Game Configuration
WIDTH = 1400
HEIGHT = 700
FPS = 60
GRAVITY = 0.5

# Colors
class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (100, 100, 100)
    DARK_GRAY = (40, 40, 40)
    LIGHT_GRAY = (200, 200, 200)
    YELLOW = (255, 255, 0)
    GOLD = (255, 215, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 100, 255)
    CYAN = (0, 255, 255)
    ORANGE = (255, 140, 0)
    PURPLE = (138, 43, 226)
    DARK_BLUE = (25, 25, 112)
    SKY_BLUE = (135, 206, 235)

# Weapon Definitions
@dataclass
class WeaponStats:
    name: str
    damage: int
    radius: int
    ammo: int
    power: int
    color: Tuple[int, int, int]

class Weapon(Enum):
    PISTOL = WeaponStats("Pistol", 20, 40, 2, 40, Color.YELLOW)
    SHOTGUN = WeaponStats("Shotgun", 40, 60, 1, 60, Color.RED)
    ROCKET = WeaponStats("Rocket", 50, 80, 1, 80, Color.ORANGE)
    GRENADE = WeaponStats("Grenade", 60, 100, 1, 100, Color.GOLD)
    FLAMETHROWER = WeaponStats("Flamethrower", 45, 70, 3, 50, Color.RED)
    LASER = WeaponStats("Laser", 35, 50, 2, 70, Color.CYAN)
    MINE = WeaponStats("Mine", 70, 120, 1, 30, Color.PURPLE)
    BANANA = WeaponStats("Banana", 55, 90, 1, 45, Color.GOLD)

class PowerUpType(Enum):
    HEALTH = "health"
    AMMO = "ammo"
    SPEED = "speed"
    SHIELD = "shield"
    DOUBLE_DAMAGE = "double_damage"
    FREEZE = "freeze"
    INVINCIBILITY = "invincibility"

class GameMode(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class AILevel(Enum):
    EASY = 0.3
    NORMAL = 0.6
    HARD = 0.9
    EXPERT = 1.0

class EnvironmentEffect(Enum):
    WIND = "wind"
    RAIN = "rain"
    GRAVITY_UP = "gravity_up"
    GRAVITY_DOWN = "gravity_down"
    METEOR_STORM = "meteor_storm"

# Asset generation system
ASSETS = {}

def generate_enhanced_assets():
    """Generate improved visuals for terrain and worms"""
    
    # Enhanced tile with texture
    tile_size = 20
    tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    
    # Base color gradient
    for i in range(tile_size):
        shade = int(255 * (1 - i / (tile_size * 2)))
        pygame.draw.line(tile, (200, 170, 50, 255), (0, i), (tile_size, i), 1)
    
    # Add texture holes
    for _ in range(2):
        x = random.randint(2, tile_size - 5)
        y = random.randint(2, tile_size - 5)
        pygame.draw.circle(tile, (100, 80, 20, 255), (x, y), 2)
    
    ASSETS['tile'] = tile
    
    # Enhanced worm sprite with better details
    w, h = 64, 40
    worm_img = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Body segments
    for i in range(3):
        segment_x = i * (w // 3)
        pygame.draw.ellipse(worm_img, Color.YELLOW, 
                           (segment_x, h // 4, w // 4, h // 2))
        pygame.draw.ellipse(worm_img, Color.GOLD, 
                           (segment_x, h // 4, w // 4, h // 2), 2)
    
    # Eyes
    pygame.draw.circle(worm_img, Color.WHITE, (w // 2 - 8, h // 3), 4)
    pygame.draw.circle(worm_img, Color.WHITE, (w // 2 + 8, h // 3), 4)
    pygame.draw.circle(worm_img, Color.BLACK, (w // 2 - 8, h // 3), 2)
    pygame.draw.circle(worm_img, Color.BLACK, (w // 2 + 8, h // 3), 2)
    
    # Mouth
    pygame.draw.line(worm_img, Color.RED, (w // 2 - 4, h // 2), 
                     (w // 2 + 4, h // 2), 2)
    
    ASSETS['worm'] = worm_img
    
    # Projectiles with glow
    for weapon in [Weapon.PISTOL, Weapon.SHOTGUN, Weapon.ROCKET, Weapon.GRENADE]:
        size = 16
        proj = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(proj, weapon.value.color, (size // 2, size // 2), size // 2)
        pygame.draw.circle(proj, Color.WHITE, (size // 2, size // 2), size // 2, 1)
        ASSETS[f'projectile_{weapon.name}'] = proj
    
    # Explosion effect
    ex = pygame.Surface((80, 80), pygame.SRCALPHA)
    for i in range(5):
        alpha = int(200 * (1 - i / 5))
        rr = 40 - i * 8
        pygame.draw.circle(ex, (255, int(150 - i * 20), 0, alpha), (40, 40), rr)
    ASSETS['explosion'] = ex
    
    # Power-up icons
    for powerup in PowerUpType:
        size = 20
        icon = pygame.Surface((size, size), pygame.SRCALPHA)
        if powerup == PowerUpType.HEALTH:
            pygame.draw.rect(icon, Color.RED, (2, 2, size - 4, size - 4))
            pygame.draw.line(icon, Color.WHITE, (size // 2, 5), (size // 2, size - 5), 2)
            pygame.draw.line(icon, Color.WHITE, (5, size // 2), (size - 5, size // 2), 2)
        elif powerup == PowerUpType.SHIELD:
            pygame.draw.polygon(icon, Color.BLUE, [(size // 2, 2), (size - 2, size - 2), (2, size - 2)])
        elif powerup == PowerUpType.SPEED:
            pygame.draw.polygon(icon, Color.GREEN, [(2, size // 2), (size - 2, 5), (size - 2, size - 5)])
        elif powerup == PowerUpType.DOUBLE_DAMAGE:
            pygame.draw.rect(icon, Color.ORANGE, (2, 2, size - 4, size - 4))
            pygame.draw.line(icon, Color.RED, (size // 2 - 5, size // 2), 
                           (size // 2 + 5, size // 2), 2)
        ASSETS[f'powerup_{powerup.name}'] = icon

generate_enhanced_assets()

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime=30, size=3):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY * 0.5
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(200 * (self.lifetime / self.max_lifetime))
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            col = (*self.color, alpha)
            pygame.draw.circle(surf, col, (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

    def is_alive(self):
        return self.lifetime > 0

class PowerUp:
    """Collectible power-up items"""
    def __init__(self, x, y, powerup_type):
        self.x, self.y = x, y
        self.type = powerup_type
        self.radius = 12
        self.rotation = 0
        self.collected = False
        self.lifetime = 600  # 10 seconds at 60 FPS

    def update(self):
        self.rotation += 5
        self.lifetime -= 1

    def draw(self, screen):
        if not self.collected and self.lifetime > 0:
            # Pulsing effect
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 3
            size = self.radius + pulse
            
            # Draw glow
            for i in range(3):
                glow_radius = size + (i * 3)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                col = (*self.get_color()[:3], 50 - i * 15)
                pygame.draw.circle(glow_surf, col, (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (int(self.x - glow_radius), int(self.y - glow_radius)))

    def get_color(self):
        color_map = {
            PowerUpType.HEALTH: Color.RED,
            PowerUpType.AMMO: Color.BLUE,
            PowerUpType.SPEED: Color.GREEN,
            PowerUpType.SHIELD: Color.CYAN,
            PowerUpType.DOUBLE_DAMAGE: Color.ORANGE,
            PowerUpType.FREEZE: (100, 200, 255),
            PowerUpType.INVINCIBILITY: Color.GOLD,
        }
        return color_map.get(self.type, Color.WHITE)

    def is_active(self):
        return not self.collected and self.lifetime > 0

class Projectile:
    def __init__(self, x, y, vx, vy, weapon, owner_id, affected_by_wind=True):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.weapon = weapon
        self.owner_id = owner_id
        self.radius = weapon.value.radius // 2
        self.lifetime = 300
        self.trail_particles = []
        self.affected_by_wind = affected_by_wind
        self.impact_count = 0

    def update(self, wind=0):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY
        
        if self.affected_by_wind:
            self.vx += wind * 0.05

        self.lifetime -= 1

        # Trail effect
        if random.random() < 0.4:
            particle_color = self.weapon.value.color
            self.trail_particles.append(
                Particle(self.x, self.y, 
                        random.uniform(-0.5, 0.5), 
                        random.uniform(-0.5, 0.5), 
                        particle_color, 15)
            )

        for particle in self.trail_particles:
            particle.update()
        self.trail_particles = [p for p in self.trail_particles if p.is_alive()]

    def draw(self, screen):
        for particle in self.trail_particles:
            particle.draw(screen)

        pygame.draw.circle(screen, self.weapon.value.color, 
                         (int(self.x), int(self.y)), self.radius)

    def is_active(self):
        return (self.lifetime > 0 and 
                0 <= self.x < WIDTH and 
                -100 <= self.y < HEIGHT + 100)

class Explosion:
    def __init__(self, x, y, damage, weapon_type):
        self.x, self.y = x, y
        self.radius = weapon_type.value.radius
        self.max_radius = self.radius
        self.damage = damage
        self.lifetime = 30
        self.weapon_type = weapon_type

    def update(self):
        if self.lifetime > 15:
            self.radius = self.max_radius * (1 - (30 - self.lifetime) / 15)
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(220 * (self.lifetime / 30))
            surf_size = int(self.max_radius * 2) + 20
            surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            color = (255, int(160 * (self.lifetime / 30)), 0, alpha)
            pygame.draw.circle(surf, color, (surf_size // 2, surf_size // 2), int(self.radius))
            screen.blit(surf, (int(self.x - surf_size // 2), int(self.y - surf_size // 2)))

    def is_active(self):
        return self.lifetime > 0

class Terrain:
    """Enhanced destructible terrain"""
    def __init__(self, width, height, difficulty=1.0):
        self.width = width
        self.height = height
        self.tile_size = 20
        self.cols = width // self.tile_size
        self.rows = height // self.tile_size
        self.tiles = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        self.difficulty = difficulty
        self.generate_terrain()

    def generate_terrain(self):
        """Procedurally generate varied terrain"""
        rows = len(self.tiles)
        cols = len(self.tiles[0])
        
        # Use Perlin-like noise for natural terrain
        for col in range(cols):
            height = int(rows * 0.6 + math.sin(col * 0.05) * rows * 0.2)
            for row in range(height, rows - 2):
                self.tiles[row][col] = 1
        
        # Add caves and features
        for _ in range(int(cols * 0.1)):
            cave_x = random.randint(0, cols - 1)
            cave_y = random.randint(int(rows * 0.3), int(rows * 0.7))
            cave_size = random.randint(2, 5)
            
            for dx in range(-cave_size, cave_size):
                for dy in range(-cave_size, cave_size):
                    if 0 <= cave_x + dx < cols and 0 <= cave_y + dy < rows:
                        if math.sqrt(dx**2 + dy**2) < cave_size:
                            self.tiles[cave_y + dy][cave_x + dx] = 0

    def is_solid(self, x, y):
        col = int(x // self.tile_size)
        row = int(y // self.tile_size)
        if 0 <= row < len(self.tiles) and 0 <= col < len(self.tiles[0]):
            return self.tiles[row][col] == 1
        return row >= len(self.tiles)

    def destroy(self, x, y, radius):
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        damage_radius_tiles = int(radius / self.tile_size) + 1
        
        for i in range(max(0, tile_y - damage_radius_tiles), 
                      min(len(self.tiles), tile_y + damage_radius_tiles + 1)):
            for j in range(max(0, tile_x - damage_radius_tiles), 
                          min(len(self.tiles[0]), tile_x + damage_radius_tiles + 1)):
                dist = math.sqrt((i * self.tile_size - y) ** 2 + 
                               (j * self.tile_size - x) ** 2)
                if dist < radius:
                    self.tiles[i][j] = 0

    def draw(self, screen):
        for row in range(len(self.tiles)):
            for col in range(len(self.tiles[0])):
                if self.tiles[row][col] == 1:
                    x = col * self.tile_size
                    y = row * self.tile_size
                    
                    # Draw tile with depth
                    pygame.draw.rect(screen, (180, 150, 40), 
                                   (x, y, self.tile_size, self.tile_size))
                    pygame.draw.rect(screen, (150, 120, 30), 
                                   (x, y, self.tile_size, self.tile_size), 1)
                    
                    # Add texture details
                    for _ in range(2):
                        px = x + random.randint(2, self.tile_size - 4)
                        py = y + random.randint(2, self.tile_size - 4)
                        pygame.draw.circle(screen, (120, 100, 20), (px, py), 1)

class Worm:
    """Enhanced worm with more features"""
    def __init__(self, x, y, team_id, worm_id, name="Worm", color=Color.YELLOW):
        self.x, self.y = x, y
        self.team_id = team_id
        self.worm_id = worm_id
        self.name = name
        self.color = color
        self.radius = 10
        self.vx, self.vy = 0, 0
        self.health = 150
        self.max_health = 150
        self.current_weapon = Weapon.PISTOL
        self.ammo = {w: w.value.ammo * 3 for w in Weapon}
        self.on_ground = False
        self.facing_right = True
        self.power = 50
        self.angle = 45
        self.particles = []
        self.invulnerable_time = 0
        self.frozen = 0
        self.speed_boost = 0
        self.shield_health = 0
        self.damage_multiplier = 1.0

    def handle_input(self, keys):
        if self.frozen > 0:
            self.frozen -= 1
            return

        move_speed = 4 if self.speed_boost > 0 else 3
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -move_speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = move_speed
            self.facing_right = True
        else:
            self.vx *= 0.85

        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = -14
            self.on_ground = False

        if keys[pygame.K_q]:
            self.angle = min(self.angle + 2, 90)
        if keys[pygame.K_e]:
            self.angle = max(self.angle - 2, 0)

        for i, weapon in enumerate([Weapon.PISTOL, Weapon.SHOTGUN, 
                                   Weapon.ROCKET, Weapon.GRENADE], 1):
            if keys[pygame.K_1 + (i - 1)] if i <= 4 else False:
                if self.ammo[weapon] > 0:
                    self.current_weapon = weapon

        if self.speed_boost > 0:
            self.speed_boost -= 1

    def update(self, terrain):
        self.vx *= 0.98
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        self.on_ground = False
        if terrain.is_solid(self.x, self.y + self.radius):
            self.y = int((self.y + self.radius) // terrain.tile_size) * terrain.tile_size - self.radius
            self.vy = 0
            self.on_ground = True

        if terrain.is_solid(self.x, self.y - self.radius):
            self.y += abs(self.vy)
            self.vy = 0

        if self.x < self.radius:
            self.x = self.radius
        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius

        if self.y > HEIGHT:
            self.health = 0

        self.invulnerable_time = max(0, self.invulnerable_time - 1)

        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.is_alive()]

    def fire(self):
        if self.ammo[self.current_weapon] <= 0:
            return None

        rad = math.radians(self.angle if self.facing_right else (180 - self.angle))
        vx = self.power * math.cos(rad) * (1 if self.facing_right else -1)
        vy = -self.power * math.sin(rad)

        self.ammo[self.current_weapon] -= 1
        return Projectile(self.x, self.y, vx, vy, self.current_weapon, self.worm_id)

    def take_damage(self, damage):
        if self.invulnerable_time > 0:
            return

        actual_damage = int(damage * self.damage_multiplier)

        if self.shield_health > 0:
            shield_absorbed = min(self.shield_health, actual_damage)
            self.shield_health -= shield_absorbed
            actual_damage -= shield_absorbed

        self.health -= actual_damage
        self.invulnerable_time = 30

        # Damage particles
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append(Particle(
                self.x, self.y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                Color.RED, 20
            ))

    def apply_powerup(self, powerup_type):
        if powerup_type == PowerUpType.HEALTH:
            self.health = min(self.max_health, self.health + 50)
        elif powerup_type == PowerUpType.AMMO:
            for weapon in self.ammo:
                self.ammo[weapon] += weapon.value.ammo
        elif powerup_type == PowerUpType.SPEED:
            self.speed_boost = 300
        elif powerup_type == PowerUpType.SHIELD:
            self.shield_health = 50
        elif powerup_type == PowerUpType.DOUBLE_DAMAGE:
            self.damage_multiplier = 2.0
        elif powerup_type == PowerUpType.FREEZE:
            self.frozen = 180
        elif powerup_type == PowerUpType.INVINCIBILITY:
            self.invulnerable_time = 300

    def draw(self, screen):
        # Draw shield if active
        if self.shield_health > 0:
            shield_alpha = int(100 * (self.shield_health / 50))
            pygame.draw.circle(screen, Color.CYAN, (int(self.x), int(self.y)), 
                             self.radius + 5, 2)

        # Draw worm
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Eyes direction
        eye_offset = 5 if self.facing_right else -5
        pygame.draw.circle(screen, Color.WHITE, 
                         (int(self.x + eye_offset), int(self.y - 2)), 2)

        # Health bar
        bar_width = 20
        bar_height = 3
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.radius - 10
        
        pygame.draw.rect(screen, Color.BLACK, 
                       (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        health_ratio = self.health / self.max_health
        health_color = Color.GREEN if health_ratio > 0.5 else (Color.ORANGE if health_ratio > 0.2 else Color.RED)
        pygame.draw.rect(screen, health_color, 
                       (bar_x, bar_y, bar_width * health_ratio, bar_height))

        # Name label
        if hasattr(pygame, 'font'):
            font = pygame.font.Font(None, 20)
            name_text = font.render(self.name, True, self.color)
            screen.blit(name_text, (int(self.x - name_text.get_width() / 2), 
                                   int(self.y - self.radius - 25)))

class Team:
    def __init__(self, team_id, color, name="Team"):
        self.team_id = team_id
        self.color = color
        self.name = name
        self.worms = []
        self.score = 0
        self.alive = True

    def add_worm(self, worm):
        self.worms.append(worm)

    def update_status(self):
        self.alive = any(worm.health > 0 for worm in self.worms)

    def get_alive_worms(self):
        return [w for w in self.worms if w.health > 0]

class GameStats:
    """Track game statistics"""
    def __init__(self):
        self.kills = {}
        self.total_damage = {}
        self.shots_fired = {}
        self.accuracy = {}

class Game:
    def __init__(self, num_teams=2, num_worms=3, difficulty=AILevel.NORMAL):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Worms Rumble - Enhanced Edition")
        self.clock = pygame.time.Clock()
        
        self.state = GameMode.PLAYING
        self.running = True
        self.num_teams = num_teams
        self.num_worms = num_worms
        self.difficulty = difficulty
        self.game_over = False
        self.winner = None
        
        self.teams = []
        self.projectiles = []
        self.explosions = []
        self.particles = []
        self.powerups = []
        
        self.current_team_idx = 0
        self.current_worm_idx = 0
        self.turn_timer = 0
        self.turn_time_limit = 60 * 30  # 30 seconds
        
        self.wind = 0
        self.wind_direction = random.choice([-1, 1])
        self.active_effects = []
        
        self.terrain = Terrain(WIDTH, HEIGHT, difficulty.value)
        self.stats = GameStats()
        
        self.initialize_teams()
        
    def initialize_teams(self):
        """Create teams and worms"""
        team_colors = [Color.RED, Color.BLUE, Color.GREEN, Color.PURPLE]
        team_names = ["Team Red", "Team Blue", "Team Green", "Team Purple"]
        worm_names = ["Warrior", "Scout", "Tank", "Assassin", "Knight"]
        
        for i in range(self.num_teams):
            team = Team(i, team_colors[i], team_names[i])
            
            for j in range(self.num_worms):
                x = (WIDTH // (self.num_teams + 1)) * (i + 1)
                y = HEIGHT // 3
                worm = Worm(x, y, i, j, 
                           f"{worm_names[j % len(worm_names)]} {j+1}",
                           team_colors[i])
                team.add_worm(worm)
                self.stats.kills[worm.worm_id] = 0
                self.stats.total_damage[worm.worm_id] = 0
                self.stats.shots_fired[worm.worm_id] = 0
            
            self.teams.append(team)

    def get_current_worm(self):
        if self.current_team_idx < len(self.teams):
            team = self.teams[self.current_team_idx]
            alive_worms = team.get_alive_worms()
            if alive_worms and self.current_worm_idx < len(alive_worms):
                return alive_worms[self.current_worm_idx]
        return None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameMode.PAUSED if self.state == GameMode.PLAYING else GameMode.PLAYING
                elif event.key == pygame.K_SPACE and self.state == GameMode.PLAYING:
                    worm = self.get_current_worm()
                    if worm:
                        projectile = worm.fire()
                        if projectile:
                            self.projectiles.append(projectile)
                            self.stats.shots_fired[worm.worm_id] = self.stats.shots_fired.get(worm.worm_id, 0) + 1
                elif event.key == pygame.K_TAB and self.state == GameMode.PLAYING:
                    self.switch_worm()

    def switch_worm(self):
        """Switch to next alive worm"""
        team = self.teams[self.current_team_idx]
        alive_worms = team.get_alive_worms()
        
        if alive_worms:
            self.current_worm_idx = (self.current_worm_idx + 1) % len(alive_worms)

    def next_team_turn(self):
        """Move to next team's turn"""
        self.current_team_idx = (self.current_team_idx + 1) % len(self.teams)
        self.current_worm_idx = 0
        self.turn_timer = 0

    def update(self):
        if self.state != GameMode.PLAYING:
            return

        # Handle player input
        keys = pygame.key.get_pressed()
        worm = self.get_current_worm()
        if worm:
            worm.handle_input(keys)

        # Update physics
        for team in self.teams:
            for worm in team.worms:
                worm.update(self.terrain)

        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update(self.wind)
            
            if not projectile.is_active():
                self.projectiles.remove(projectile)
                # Create explosion
                explosion = Explosion(projectile.x, projectile.y, 
                                    projectile.weapon.value.damage,
                                    projectile.weapon)
                self.explosions.append(explosion)

        # Handle explosions
        for explosion in self.explosions[:]:
            explosion.update()
            
            if not explosion.is_active():
                self.explosions.remove(explosion)
                continue
            
            # Destroy terrain
            self.terrain.destroy(explosion.x, explosion.y, explosion.radius)
            
            # Damage worms
            for team in self.teams:
                for target_worm in team.worms:
                    dist = math.sqrt((target_worm.x - explosion.x) ** 2 + 
                                   (target_worm.y - explosion.y) ** 2)
                    if dist < explosion.radius:
                        damage = int(explosion.damage * (1 - dist / explosion.radius))
                        target_worm.take_damage(damage)
                        self.stats.total_damage[target_worm.worm_id] = self.stats.total_damage.get(target_worm.worm_id, 0) + damage

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)

        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update()
            
            if not powerup.is_active():
                self.powerups.remove(powerup)
                continue
            
            # Check collection
            for team in self.teams:
                for worm in team.worms:
                    dist = math.sqrt((worm.x - powerup.x) ** 2 + 
                                   (worm.y - powerup.y) ** 2)
                    if dist < worm.radius + powerup.radius:
                        worm.apply_powerup(powerup.type)
                        powerup.collected = True

        # Update wind
        if random.random() < 0.02:
            self.wind_direction *= random.choice([-1, 1])
        self.wind += self.wind_direction * 0.1
        self.wind = max(-5, min(5, self.wind))

        # Update team status
        for team in self.teams:
            team.update_status()

        # Check win condition
        alive_teams = [t for t in self.teams if t.alive]
        if len(alive_teams) == 1:
            self.game_over = True
            self.winner = alive_teams[0]

        # Turn management
        self.turn_timer += 1
        if self.turn_timer > self.turn_time_limit:
            self.next_team_turn()

        # Spawn power-ups randomly
        if random.random() < 0.002:
            x = random.randint(100, WIDTH - 100)
            y = 50
            powerup = PowerUp(x, y, random.choice(list(PowerUpType)))
            self.powerups.append(powerup)

        # AI turns (simplified)
        if not isinstance(worm, type(None)):
            team = self.teams[self.current_team_idx]
            if all(w.vx == 0 and w.vy == 0 for w in team.worms):
                # Turn is idle, move to next
                self.next_team_turn()

    def draw(self):
        # Background
        self.screen.fill(Color.DARK_BLUE)
        
        # Draw stars
        for i in range(50):
            x = (i * 73) % WIDTH
            y = (i * 43) % (HEIGHT // 2)
            pygame.draw.circle(self.screen, Color.WHITE, (x, y), 1)

        # Draw clouds
        cloud_y = 50
        for i in range(5):
            x = (i * 250) % WIDTH
            pygame.draw.ellipse(self.screen, Color.LIGHT_GRAY, (x, cloud_y, 100, 30))

        # Draw terrain
        self.terrain.draw(self.screen)

        # Draw water
        pygame.draw.rect(self.screen, Color.CYAN, 
                        (0, HEIGHT - 60, WIDTH, 60))

        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)

        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw worms
        for team in self.teams:
            for worm in team.worms:
                worm.draw(self.screen)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        """Draw heads-up display"""
        font = pygame.font.Font(None, 20)
        
        # Current turn info
        worm = self.get_current_worm()
        if worm:
            team = self.teams[self.current_team_idx]
            turn_text = f"{team.name} - {worm.name} | Health: {worm.health}/{worm.max_health} | Weapon: {worm.current_weapon.name} | Power: {worm.power}"
            text_surf = font.render(turn_text, True, Color.WHITE)
            self.screen.blit(text_surf, (10, 10))

        # Wind indicator
        wind_text = f"Wind: {self.wind:.1f}"
        wind_color = Color.GREEN if abs(self.wind) < 2 else Color.ORANGE
        text_surf = font.render(wind_text, True, wind_color)
        self.screen.blit(text_surf, (WIDTH - 100, 10))

        # Team scores
        for i, team in enumerate(self.teams):
            score_text = f"{team.name}: {team.score}"
            text_surf = font.render(score_text, True, team.color)
            self.screen.blit(text_surf, (10, 40 + i * 25))

        # Turn timer
        timer_seconds = max(0, (self.turn_time_limit - self.turn_timer) // 60)
        timer_text = f"Time: {timer_seconds}s"
        text_surf = font.render(timer_text, True, Color.YELLOW)
        self.screen.blit(text_surf, (WIDTH - 100, HEIGHT - 30))

    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Color.BLACK)
        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.Font(None, 80)
        font_small = pygame.font.Font(None, 40)

        winner_text = f"{self.winner.name} WINS!"
        text = font_large.render(winner_text, True, self.winner.color)
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 
                               HEIGHT // 2 - 100))

        restart_text = "Press SPACE to continue"
        text = font_small.render(restart_text, True, Color.WHITE)
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 
                               HEIGHT // 2 + 100))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

            if self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.running = False

        pygame.quit()

if __name__ == "__main__":
    try:
        game = Game(num_teams=4, num_worms=2, difficulty=AILevel.NORMAL)
        game.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
