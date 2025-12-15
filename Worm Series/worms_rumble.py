import pygame
import math
import random
import json
import os
import wave
import struct
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

pygame.init()

# In-memory placeholder assets (generated at runtime) to avoid external image dependencies
ASSETS = {}

def generate_placeholder_assets():
    # Tile
    tile_size = 20
    tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    tile.fill(Color.GRAY)
    pygame.draw.rect(tile, Color.LIGHT_GRAY, (0, 0, tile_size, int(tile_size * 0.4)))
    pygame.draw.rect(tile, Color.DARK_GRAY, (0, 0, tile_size, tile_size), 1)
    ASSETS['tile'] = tile

    # Worm sprite (simple rounded rectangle with face)
    w = 48
    h = 30
    worm_img = pygame.Surface((w, h), pygame.SRCALPHA)
    body_rect = pygame.Rect(0, 6, w, h - 6)
    pygame.draw.ellipse(worm_img, Color.YELLOW, body_rect)
    pygame.draw.ellipse(worm_img, Color.WHITE, body_rect, 2)
    # eyes
    pygame.draw.circle(worm_img, Color.WHITE, (w//2 - 6, 12), 3)
    pygame.draw.circle(worm_img, Color.WHITE, (w//2 + 6, 12), 3)
    pygame.draw.circle(worm_img, Color.BLACK, (w//2 - 6, 12), 1)
    pygame.draw.circle(worm_img, Color.BLACK, (w//2 + 6, 12), 1)
    ASSETS['worm'] = worm_img

    # Projectile
    p = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.circle(p, Color.ORANGE, (6, 6), 5)
    ASSETS['projectile'] = p

    # Explosion (sprite used as overlay)
    ex = pygame.Surface((64, 64), pygame.SRCALPHA)
    for i in range(5):
        alpha = int(200 * (1 - i / 5))
        rr = 30 - i * 5
        pygame.draw.circle(ex, (255, 120, 0, alpha), (32, 32), rr)
    ASSETS['explosion'] = ex

generate_placeholder_assets()

def save_assets_to_disk():
    # Save generated surfaces to PNG files so they become "real assets" on disk
    try:
        os.makedirs('assets/images', exist_ok=True)
        if 'tile' in ASSETS:
            pygame.image.save(ASSETS['tile'], os.path.join('assets', 'images', 'tile.png'))
        if 'worm' in ASSETS:
            pygame.image.save(ASSETS['worm'], os.path.join('assets', 'images', 'worm.png'))
        if 'projectile' in ASSETS:
            pygame.image.save(ASSETS['projectile'], os.path.join('assets', 'images', 'projectile.png'))
        if 'explosion' in ASSETS:
            pygame.image.save(ASSETS['explosion'], os.path.join('assets', 'images', 'explosion.png'))

        # Also ensure example sounds are present (ensure_sound_file already creates them)
        ensure_sound_file(os.path.join('assets', 'sounds', 'fire.wav'), freq=1200.0, duration=0.08, volume=0.2)
        ensure_sound_file(os.path.join('assets', 'sounds', 'explosion.wav'), freq=200.0, duration=0.35, volume=0.6)
        ensure_sound_file(os.path.join('assets', 'sounds', 'jump.wav'), freq=600.0, duration=0.12, volume=0.2)

        # Try to replace in-memory assets with disk-loaded versions for fidelity
        try:
            tile_path = os.path.join('assets', 'images', 'tile.png')
            if os.path.exists(tile_path):
                ASSETS['tile'] = pygame.image.load(tile_path).convert_alpha()
            worm_path = os.path.join('assets', 'images', 'worm.png')
            if os.path.exists(worm_path):
                ASSETS['worm'] = pygame.image.load(worm_path).convert_alpha()
            proj_path = os.path.join('assets', 'images', 'projectile.png')
            if os.path.exists(proj_path):
                ASSETS['projectile'] = pygame.image.load(proj_path).convert_alpha()
            ex_path = os.path.join('assets', 'images', 'explosion.png')
            if os.path.exists(ex_path):
                ASSETS['explosion'] = pygame.image.load(ex_path).convert_alpha()
        except Exception:
            pass
    except Exception:
        # If saving fails (permissions etc.), ignore and continue using in-memory assets
        pass

# Attempt to write placeholder assets to disk so users get "real" files to edit
save_assets_to_disk()

def ensure_sound_file(path, freq=440.0, duration=0.2, volume=0.3):
    # Create a short sine-wave WAV file at `path` if it doesn't exist
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sample_rate = 44100
    amplitude = int(32767 * volume)
    n_samples = int(sample_rate * duration)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            val = int(amplitude * math.sin(2 * math.pi * freq * t))
            data = struct.pack('<h', val)
            wf.writeframesraw(data)
        wf.writeframes(b'')

WIDTH, HEIGHT = 1280, 800
FPS = 60
GRAVITY = 0.5

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    SETTINGS = 5

class Weapon(Enum):
    PISTOL = {"name": "Pistol", "damage": 25, "ammo": 999, "fire_rate": 0.2}
    SHOTGUN = {"name": "Shotgun", "damage": 60, "ammo": 30, "fire_rate": 0.8}
    ROCKET = {"name": "Rocket", "damage": 100, "ammo": 10, "fire_rate": 1.0}
    GRENADE = {"name": "Grenade", "damage": 80, "ammo": 15, "fire_rate": 0.6}

@dataclass
class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (220, 50, 50)
    GREEN = (50, 200, 50)
    BLUE = (50, 100, 220)
    YELLOW = (255, 255, 0)
    GRAY = (100, 100, 100)
    DARK_GRAY = (40, 40, 40)
    LIGHT_GRAY = (200, 200, 200)
    ORANGE = (255, 165, 0)
    PURPLE = (200, 50, 200)

class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime=30):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = 3

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY * 0.5
        self.lifetime -= 1

    def draw(self, screen):
        # Draw with alpha using a small surface so particles fade nicely
        alpha = int(200 * (self.lifetime / self.max_lifetime))
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        col = (*self.color, alpha)
        pygame.draw.circle(surf, col, (self.size, self.size), self.size)
        screen.blit(surf, (int(self.x - self.size), int(self.y - self.size)))

    def is_alive(self):
        return self.lifetime > 0

class Projectile:
    def __init__(self, x, y, vx, vy, weapon, owner_id):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.weapon = weapon
        self.owner_id = owner_id
        self.radius = 5 if weapon == Weapon.PISTOL else (8 if weapon == Weapon.SHOTGUN else 10)
        self.lifetime = 300
        self.trail_particles = []

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY
        self.lifetime -= 1

        if random.random() < 0.3:
            particle_color = Color.ORANGE if self.weapon == Weapon.ROCKET else Color.YELLOW
            self.trail_particles.append(
                Particle(self.x, self.y, random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), particle_color, 15)
            )

        for particle in self.trail_particles:
            particle.update()
        self.trail_particles = [p for p in self.trail_particles if p.is_alive()]

    def draw(self, screen):
        for particle in self.trail_particles:
            particle.draw(screen)

        colors = {Weapon.PISTOL: Color.YELLOW, Weapon.SHOTGUN: Color.RED, 
                  Weapon.ROCKET: Color.ORANGE, Weapon.GRENADE: Color.GREEN}
        pygame.draw.circle(screen, colors[self.weapon], (int(self.x), int(self.y)), self.radius)

    def is_active(self):
        return self.lifetime > 0 and 0 <= self.x < WIDTH and 0 <= self.y < HEIGHT

class Explosion:
    def __init__(self, x, y, radius, damage):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_radius = radius
        self.damage = damage
        self.lifetime = 30
        self.expanding = True

    def update(self):
        if self.expanding and self.lifetime > 15:
            self.radius = self.max_radius * (1 - (30 - self.lifetime) / 15)
        self.lifetime -= 1

    def draw(self, screen):
        alpha = int(220 * (self.lifetime / 30))
        # Draw expanding translucent filled circle
        surf_size = int(self.max_radius * 2) + 8
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        color = (255, int(160 * (self.lifetime / 30)), 0, alpha)
        pygame.draw.circle(surf, color, (surf_size // 2, surf_size // 2), int(self.radius))
        screen.blit(surf, (int(self.x - surf_size // 2), int(self.y - surf_size // 2)))

    def is_active(self):
        return self.lifetime > 0

class Terrain:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[1 for _ in range(width // 20)] for _ in range(height // 20)]
        self.tile_size = 20
        self.generate_terrain()

    def generate_terrain(self):
        rows = len(self.tiles)
        cols = len(self.tiles[0])
        for i in range(rows):
            for j in range(cols):
                # Keep bottom rows solid to form ground
                if i >= rows - 3:
                    self.tiles[i][j] = 1
                else:
                    # Random scattered terrain with some caves
                    self.tiles[i][j] = 1 if random.random() < 0.55 else 0

    def draw(self, screen):
        rows = len(self.tiles)
        cols = len(self.tiles[0])
        tile_img = ASSETS.get('tile')
        for i in range(rows):
            for j in range(cols):
                if self.tiles[i][j] == 1:
                    x = j * self.tile_size
                    y = i * self.tile_size
                    if tile_img:
                        # scale tile image if tile_size differs
                        if tile_img.get_width() != self.tile_size:
                            scaled = pygame.transform.smoothscale(tile_img, (self.tile_size, self.tile_size))
                            screen.blit(scaled, (x, y))
                        else:
                            screen.blit(tile_img, (x, y))
                    else:
                        rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                        # base tile
                        pygame.draw.rect(screen, Color.GRAY, rect)
                        # subtle top lighting
                        light_rect = rect.copy()
                        light_rect.height = int(self.tile_size * 0.4)
                        pygame.draw.rect(screen, Color.LIGHT_GRAY, light_rect)
                        # border
                        pygame.draw.rect(screen, Color.DARK_GRAY, rect, 1)

    def is_solid(self, x, y):
        if x < 0 or x >= self.width or y >= self.height:
            return True
        if y < 0:
            return False
        i, j = int(y // self.tile_size), int(x // self.tile_size)
        if i < 0 or i >= len(self.tiles) or j < 0 or j >= len(self.tiles[0]):
            return False
        return self.tiles[i][j] == 1

    def damage_terrain(self, x, y, radius):
        tile_x, tile_y = int(x // self.tile_size), int(y // self.tile_size)
        damage_radius_tiles = int(radius // self.tile_size) + 1
        for i in range(max(0, tile_y - damage_radius_tiles), min(len(self.tiles), tile_y + damage_radius_tiles + 1)):
            for j in range(max(0, tile_x - damage_radius_tiles), min(len(self.tiles[0]), tile_x + damage_radius_tiles + 1)):
                dist = math.sqrt((i * self.tile_size - y) ** 2 + (j * self.tile_size - x) ** 2)
                if dist < radius:
                    self.tiles[i][j] = 0

class Worm:
    def __init__(self, x, y, team_id, worm_id, color):
        self.x = x
        self.y = y
        self.team_id = team_id
        self.worm_id = worm_id
        self.color = color
        self.radius = 8
        self.vx = 0
        self.vy = 0
        self.health = 100
        self.max_health = 100
        self.current_weapon = Weapon.PISTOL
        self.ammo = {w: w.value["ammo"] for w in Weapon}
        self.on_ground = False
        self.facing_right = True
        self.power = 50
        self.angle = 45
        self.particles = []
        self.invulnerable_time = 0

    def handle_input(self, keys):
        move_speed = 3
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -move_speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = move_speed
            self.facing_right = True
        else:
            self.vx *= 0.85

        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = -12
            self.on_ground = False

        if keys[pygame.K_q]:
            self.angle = min(self.angle + 1, 90)
        if keys[pygame.K_e]:
            self.angle = max(self.angle - 1, 0)

        if keys[pygame.K_1]:
            self.current_weapon = Weapon.PISTOL
        if keys[pygame.K_2]:
            self.current_weapon = Weapon.SHOTGUN
        if keys[pygame.K_3]:
            self.current_weapon = Weapon.ROCKET
        if keys[pygame.K_4]:
            self.current_weapon = Weapon.GRENADE

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
            self.vx = 0
        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.vx = 0

        if self.y > HEIGHT:
            self.health = 0

        self.invulnerable_time = max(0, self.invulnerable_time - 1)

        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.is_alive()]

    def ai_fire_at(self, target_x, target_y):
        # Simple aiming: set angle towards target and fire with random power
        dx = target_x - self.x
        dy = target_y - self.y
        angle = math.degrees(math.atan2(-dy, dx))
        # Normalize angle to 0-180
        if angle < 0:
            angle = 360 + angle
        self.angle = max(10, min(170, int(angle)))
        self.power = random.randint(30, 80)
        return self.fire()

    def take_damage(self, damage):
        if self.invulnerable_time == 0:
            self.health = max(0, self.health - damage)
            self.invulnerable_time = 30
            for _ in range(10):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                self.particles.append(Particle(self.x, self.y, vx, vy, Color.RED, 20))

    def fire(self):
        if self.ammo[self.current_weapon] <= 0:
            return None

        self.ammo[self.current_weapon] -= 1
        angle_rad = math.radians(self.angle if self.facing_right else 180 - self.angle)
        power_multiplier = self.power / 50

        if self.current_weapon == Weapon.PISTOL:
            vx = math.cos(angle_rad) * 10 * power_multiplier
            vy = -math.sin(angle_rad) * 10 * power_multiplier
            return Projectile(self.x, self.y, vx, vy, self.current_weapon, self.worm_id)

        elif self.current_weapon == Weapon.SHOTGUN:
            projectiles = []
            for spread in [-5, 0, 5]:
                spread_angle = angle_rad + math.radians(spread)
                vx = math.cos(spread_angle) * 8 * power_multiplier
                vy = -math.sin(spread_angle) * 8 * power_multiplier
                projectiles.append(Projectile(self.x, self.y, vx, vy, self.current_weapon, self.worm_id))
            return projectiles

        elif self.current_weapon == Weapon.ROCKET:
            vx = math.cos(angle_rad) * 7 * power_multiplier
            vy = -math.sin(angle_rad) * 7 * power_multiplier
            return Projectile(self.x, self.y, vx, vy, self.current_weapon, self.worm_id)

        elif self.current_weapon == Weapon.GRENADE:
            vx = math.cos(angle_rad) * 6 * power_multiplier
            vy = -math.sin(angle_rad) * 6 * power_multiplier
            return Projectile(self.x, self.y, vx, vy, self.current_weapon, self.worm_id)

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

        # draw optional sprite behind worm for extra polish
        worm_sprite = ASSETS.get('worm')
        if worm_sprite:
            ws = pygame.transform.smoothscale(worm_sprite, (int(self.radius * 3), int(self.radius * 2)))
            screen.blit(ws, (int(self.x - ws.get_width() // 2), int(self.y - ws.get_height() // 2)))
        # Draw body with a small capsule and a hat for personality
        body_w = self.radius * 2
        body_h = int(self.radius * 1.6)
        body_surf = pygame.Surface((body_w, body_h), pygame.SRCALPHA)
        pygame.draw.ellipse(body_surf, self.color, (0, 0, body_w, body_h))
        pygame.draw.ellipse(body_surf, Color.WHITE, (0, 0, body_w, body_h), 2)
        screen.blit(body_surf, (int(self.x - body_w // 2), int(self.y - body_h // 2)))

        # Hat
        hat_w = int(self.radius * 1.8)
        hat_h = int(self.radius * 0.8)
        hat_rect = pygame.Rect(int(self.x - hat_w // 2), int(self.y - body_h // 2 - hat_h), hat_w, hat_h)
        pygame.draw.rect(screen, Color.DARK_GRAY, hat_rect, border_radius=6)

        # Eyes
        eye_y = int(self.y - self.radius * 0.2)
        pygame.draw.circle(screen, Color.WHITE, (int(self.x - 3), eye_y), 3)
        pygame.draw.circle(screen, Color.WHITE, (int(self.x + 3), eye_y), 3)
        pygame.draw.circle(screen, Color.BLACK, (int(self.x - 3), eye_y), 1)
        pygame.draw.circle(screen, Color.BLACK, (int(self.x + 3), eye_y), 1)

        # Health bar
        health_width = 28
        health_bar_y = self.y - self.radius - 12
        pygame.draw.rect(screen, Color.RED, (int(self.x - health_width // 2), int(health_bar_y), health_width, 5))
        pygame.draw.rect(screen, Color.GREEN, (int(self.x - health_width // 2), int(health_bar_y), 
                                               int(health_width * (self.health / self.max_health)), 5))

class Team:
    def __init__(self, team_id, name, color):
        self.team_id = team_id
        self.name = name
        self.color = color
        self.worms: List[Worm] = []
        self.score = 0
        self.current_worm_index = 0

    def add_worm(self, worm):
        self.worms.append(worm)

    def add_boss(self, x, y, worm_id):
        boss = Worm(x, y, self.team_id, worm_id, self.color)
        boss.radius = 16
        boss.health = 300
        boss.max_health = 300
        boss.current_weapon = Weapon.ROCKET
        boss.power = 80
        self.worms.append(boss)

    def get_current_worm(self) -> Optional[Worm]:
        alive_worms = [w for w in self.worms if w.health > 0]
        if not alive_worms:
            return None
        self.current_worm_index = min(self.current_worm_index, len(alive_worms) - 1)
        return alive_worms[self.current_worm_index]

    def switch_worm(self):
        alive_worms = [w for w in self.worms if w.health > 0]
        if alive_worms:
            self.current_worm_index = (self.current_worm_index + 1) % len(alive_worms)

    def all_dead(self):
        return all(w.health <= 0 for w in self.worms)

class Button:
    def __init__(self, x, y, width, height, text, color=Color.BLUE, text_color=Color.WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hovered = False

    def draw(self, screen, font):
        color = tuple(min(c + 30, 255) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, Color.WHITE, self.rect, 2)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Worms Rumble - Battle Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.state = GameState.MENU
        self.running = True
        self.difficulty = "Normal"
        self.num_players = 2
        self.settings_music = True
        self.settings_sfx = True
        
        self.terrain = None
        self.teams: List[Team] = []
        self.projectiles: List[Projectile] = []
        self.explosions: List[Explosion] = []
        self.current_team_index = 0
        self.turn_timer = 60
        self.game_over = False
        self.winner_team = None
        
        self.buttons_menu = []
        self.buttons_settings = []
        self.setup_menu_buttons()
        # Optional sound scaffolding (place .wav files in assets/sounds/)
        self.sounds = {}
        # Ensure we have small example sounds generated if missing
        try:
            ensure_sound_file('assets/sounds/fire.wav', freq=1200.0, duration=0.08, volume=0.2)
            ensure_sound_file('assets/sounds/explosion.wav', freq=200.0, duration=0.35, volume=0.6)
            ensure_sound_file('assets/sounds/jump.wav', freq=600.0, duration=0.12, volume=0.2)
            self.sounds['fire'] = pygame.mixer.Sound('assets/sounds/fire.wav')
            self.sounds['explosion'] = pygame.mixer.Sound('assets/sounds/explosion.wav')
            self.sounds['jump'] = pygame.mixer.Sound('assets/sounds/jump.wav')
        except Exception:
            # If sound fails, keep silent but continue
            self.sounds = {}

    def setup_menu_buttons(self):
        button_y = 250
        self.buttons_menu = [
            Button(WIDTH // 2 - 100, button_y, 200, 50, "Start Game", Color.GREEN),
            Button(WIDTH // 2 - 100, button_y + 80, 200, 50, "Settings", Color.BLUE),
            Button(WIDTH // 2 - 100, button_y + 160, 200, 50, "Quit", Color.RED),
        ]

        self.buttons_settings = [
            Button(WIDTH // 2 - 100, 150, 200, 50, "Music: ON", Color.BLUE),
            Button(WIDTH // 2 - 100, 230, 200, 50, "SFX: ON", Color.BLUE),
            Button(WIDTH // 2 - 100, 310, 200, 50, "Difficulty: Normal", Color.BLUE),
            Button(WIDTH // 2 - 100, 390, 200, 50, "Players: 2", Color.BLUE),
            Button(WIDTH // 2 - 100, 550, 200, 50, "Back", Color.GRAY),
        ]

    def setup_game(self):
        self.terrain = Terrain(WIDTH, HEIGHT)
        self.teams = []
        team_colors = [Color.RED, Color.BLUE, Color.YELLOW, Color.PURPLE]
        
        for i in range(self.num_players):
            team = Team(i, f"Team {i + 1}", team_colors[i])
            for j in range(3):
                x = 50 + i * (WIDTH - 100) // (self.num_players - 1) if self.num_players > 1 else WIDTH // 2
                y = 50 + j * 60
                worm = Worm(x, y, i, j, team.color)
                team.add_worm(worm)
            # Add a boss on higher difficulty for additional challenge
            if self.difficulty == "Hard":
                bx = WIDTH - 120 - i * 100
                by = HEIGHT - 140
                team.add_boss(bx, by, 99 + i)
            self.teams.append(team)
        
        self.current_team_index = 0
        self.projectiles = []
        self.explosions = []
        self.game_over = False
        self.winner_team = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.SETTINGS:
                        self.state = GameState.MENU
                    elif self.state == GameState.MENU:
                        self.running = False

                if event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                    self.fire_weapon()

                if event.key == pygame.K_TAB and self.state == GameState.PLAYING:
                    team = self.teams[self.current_team_index]
                    team.switch_worm()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if self.state == GameState.MENU:
                    self.handle_menu_click(pos)
                elif self.state == GameState.SETTINGS:
                    self.handle_settings_click(pos)

    def handle_menu_click(self, pos):
        for i, button in enumerate(self.buttons_menu):
            if button.is_clicked(pos):
                if i == 0:
                    self.setup_game()
                    self.state = GameState.PLAYING
                elif i == 1:
                    self.state = GameState.SETTINGS
                elif i == 2:
                    self.running = False

    def handle_settings_click(self, pos):
        for i, button in enumerate(self.buttons_settings):
            if button.is_clicked(pos):
                if i == 0:
                    self.settings_music = not self.settings_music
                    self.buttons_settings[0].text = f"Music: {'ON' if self.settings_music else 'OFF'}"
                elif i == 1:
                    self.settings_sfx = not self.settings_sfx
                    self.buttons_settings[1].text = f"SFX: {'ON' if self.settings_sfx else 'OFF'}"
                elif i == 2:
                    difficulties = ["Easy", "Normal", "Hard"]
                    idx = difficulties.index(self.difficulty)
                    self.difficulty = difficulties[(idx + 1) % len(difficulties)]
                    self.buttons_settings[2].text = f"Difficulty: {self.difficulty}"
                elif i == 3:
                    self.num_players = 3 if self.num_players == 2 else 2
                    self.buttons_settings[3].text = f"Players: {self.num_players}"
                elif i == 4:
                    self.state = GameState.MENU

    def fire_weapon(self):
        if self.game_over:
            return
        
        current_team = self.teams[self.current_team_index]
        current_worm = current_team.get_current_worm()
        
        if current_worm:
            fired = current_worm.fire()
            if fired:
                if isinstance(fired, list):
                    self.projectiles.extend(fired)
                else:
                    self.projectiles.append(fired)
                # play sound
                if self.settings_sfx and 'fire' in self.sounds:
                    try:
                        self.sounds['fire'].play()
                    except Exception:
                        pass
            self.next_turn()

    def next_turn(self):
        self.current_team_index = (self.current_team_index + 1) % len(self.teams)
        self.turn_timer = 60

    def update(self):
        if self.state != GameState.PLAYING:
            return

        # Use get_pressed to read held keys (fixed bug)
        keys = pygame.key.get_pressed()
        current_team = self.teams[self.current_team_index]
        current_worm = current_team.get_current_worm()

        if current_worm:
            current_worm.handle_input(keys)
            current_worm.update(self.terrain)

        for worm in [w for team in self.teams for w in team.worms]:
            if worm != current_worm:
                worm.update(self.terrain)
                # Simple AI: occasionally fire at current worm
                if worm.health > 0 and random.random() < (0.002 if self.difficulty == 'Easy' else 0.006 if self.difficulty == 'Normal' else 0.012):
                    target = current_worm
                    if target:
                        fired = worm.ai_fire_at(target.x, target.y)
                        if fired:
                            if isinstance(fired, list):
                                self.projectiles.extend(fired)
                            else:
                                self.projectiles.append(fired)
                            if self.settings_sfx and 'fire' in self.sounds:
                                try:
                                    self.sounds['fire'].play()
                                except Exception:
                                    pass

        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.is_active():
                self.projectiles.remove(projectile)
                if projectile.weapon == Weapon.GRENADE:
                    explosion = Explosion(projectile.x, projectile.y, 60, projectile.weapon.value["damage"])
                    self.explosions.append(explosion)
                    if self.settings_sfx and 'explosion' in self.sounds:
                        try:
                            self.sounds['explosion'].play()
                        except Exception:
                            pass

        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.is_active():
                self.explosions.remove(explosion)
            else:
                for worm in [w for team in self.teams for w in team.worms]:
                    dist = math.sqrt((worm.x - explosion.x) ** 2 + (worm.y - explosion.y) ** 2)
                    if dist < explosion.radius:
                        damage = explosion.damage * (1 - dist / explosion.radius)
                        worm.take_damage(int(damage))
                self.terrain.damage_terrain(explosion.x, explosion.y, explosion.radius)

        for projectile in self.projectiles[:]:
            for worm in [w for team in self.teams for w in team.worms]:
                dist = math.sqrt((worm.x - projectile.x) ** 2 + (worm.y - projectile.y) ** 2)
                if dist < worm.radius + projectile.radius:
                    damage = projectile.weapon.value["damage"]
                    worm.take_damage(damage)
                    
                    explosion = Explosion(projectile.x, projectile.y, 40, damage)
                    self.explosions.append(explosion)
                    self.projectiles.remove(projectile)
                    break

        if any(team.all_dead() for team in self.teams):
            self.game_over = True
            for team in self.teams:
                if not team.all_dead():
                    self.winner_team = team

        self.turn_timer -= 1
        if self.turn_timer <= 0:
            self.next_turn()

    def draw_hud(self):
        current_team = self.teams[self.current_team_index]
        current_worm = current_team.get_current_worm()

        team_text = self.font_small.render(f"Team: {current_team.name}", True, current_team.color)
        self.screen.blit(team_text, (10, 10))

        if current_worm:
            health_text = self.font_small.render(f"Health: {int(current_worm.health)}/{current_worm.max_health}", 
                                                 True, Color.WHITE)
            self.screen.blit(health_text, (10, 40))

            weapon_name = current_worm.current_weapon.value["name"]
            ammo = current_worm.ammo[current_worm.current_weapon]
            weapon_text = self.font_small.render(f"Weapon: {weapon_name} ({ammo})", True, Color.WHITE)
            self.screen.blit(weapon_text, (10, 70))

            power_text = self.font_small.render(f"Power: {int(current_worm.power)}%", True, Color.YELLOW)
            self.screen.blit(power_text, (10, 100))

            angle_text = self.font_small.render(f"Angle: {int(current_worm.angle)}°", True, Color.YELLOW)
            self.screen.blit(angle_text, (10, 130))

        timer_text = self.font_small.render(f"Time: {self.turn_timer}", True, Color.YELLOW)
        self.screen.blit(timer_text, (WIDTH - 150, 10))

        scores_y = 10
        for i, team in enumerate(self.teams):
            score_text = self.font_small.render(f"{team.name}: {team.score}", True, team.color)
            self.screen.blit(score_text, (WIDTH - 250, scores_y + i * 30))

    def draw_menu(self):
        self.screen.fill(Color.DARK_GRAY)

        title = self.font_large.render("WORMS RUMBLE", True, Color.ORANGE)
        title_rect = title.get_rect(center=(WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        subtitle = self.font_medium.render("Battle Edition", True, Color.YELLOW)
        subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)

        pos = pygame.mouse.get_pos()
        for button in self.buttons_menu:
            button.update_hover(pos)
            button.draw(self.screen, self.font_medium)

    def draw_settings(self):
        self.screen.fill(Color.DARK_GRAY)

        title = self.font_large.render("SETTINGS", True, Color.BLUE)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        pos = pygame.mouse.get_pos()
        for button in self.buttons_settings:
            button.update_hover(pos)
            button.draw(self.screen, self.font_medium)

    def draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Color.BLACK)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font_large.render("PAUSED", True, Color.YELLOW)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)

        resume_text = self.font_small.render("Press ESC to Resume", True, Color.WHITE)
        resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        self.screen.blit(resume_text, resume_rect)

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Color.BLACK)
        self.screen.blit(overlay, (0, 0))

        if self.winner_team:
            winner_text = self.font_large.render(f"{self.winner_team.name} WINS!", True, self.winner_team.color)
        else:
            winner_text = self.font_large.render("GAME OVER!", True, Color.RED)
        
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        self.screen.blit(winner_text, winner_rect)

        restart_text = self.font_small.render("Press SPACE to return to menu", True, Color.WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        # nicer background gradient sky
        top = Color.BLUE
        bottom = (20, 20, 30)
        for y in range(HEIGHT):
            t = y / HEIGHT
            r = int(top[0] * (1 - t) + bottom[0] * t)
            g = int(top[1] * (1 - t) + bottom[1] * t)
            b = int(top[2] * (1 - t) + bottom[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.PLAYING:
            # Draw terrain and world objects
            self.terrain.draw(self.screen)

            # Draw explosions behind worms for impact
            for explosion in self.explosions:
                explosion.draw(self.screen)

            # Draw projectiles
            for projectile in self.projectiles:
                # draw projectile sprite if available
                proj_img = ASSETS.get('projectile')
                if proj_img:
                    pimg = pygame.transform.smoothscale(proj_img, (projectile.radius * 2, projectile.radius * 2))
                    self.screen.blit(pimg, (int(projectile.x - projectile.radius), int(projectile.y - projectile.radius)))
                else:
                    projectile.draw(self.screen)

            # Draw worms
            for team in self.teams:
                for worm in team.worms:
                    worm.draw(self.screen)

            # Draw HUD and overlays
            self.draw_hud()

            if self.game_over:
                self.draw_game_over()

        elif self.state == GameState.PAUSED:
            self.terrain.draw(self.screen)
            for team in self.teams:
                for worm in team.worms:
                    worm.draw(self.screen)
            self.draw_hud()
            self.draw_pause()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

            if self.state == GameState.PLAYING and self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.state = GameState.MENU

        pygame.quit()

if __name__ == "__main__":
    # Run the game with exception logging so we can capture errors when it fails to start
    try:
        game = Game()
        game.run()
    except Exception as exc:
        # Ensure logs directory exists
        try:
            os.makedirs(os.path.join('assets', 'logs'), exist_ok=True)
            log_path = os.path.join('assets', 'logs', 'error.txt')
            import traceback
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write('Exception during game run:\n')
                traceback.print_exc(file=f)
            print(f"An error occurred while running the game. See {log_path} for details.")
        except Exception:
            print('An error occurred while running the game and the error could not be logged to disk.')
        raise
