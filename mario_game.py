"""
ULTIMATE SUPER MARIO PRO - Advanced Platformer Game
Features: Multiple levels, characters, power-ups, enemies, boss fights,
particle effects, animated graphics, power-up system, and much more!
"""

import pygame
import sys
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    SKY_BLUE = (135, 206, 250)
    DEEP_SKY = (0, 191, 255)
    GREEN = (34, 139, 34)
    DARK_GREEN = (0, 100, 0)
    LIGHT_GREEN = (144, 238, 144)
    RED = (255, 0, 0)
    DARK_RED = (139, 0, 0)
    ORANGE = (255, 140, 0)
    BROWN = (139, 69, 19)
    DARK_BROWN = (101, 67, 33)
    YELLOW = (255, 215, 0)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    PURPLE = (138, 43, 226)
    PINK = (255, 192, 203)
    CYAN = (0, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (50, 50, 50)

# Game variables
GRAVITY = 0.8
JUMP_STRENGTH = -16
DOUBLE_JUMP_STRENGTH = -14

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
    CHARACTER_SELECT = "character_select"
    INSTRUCTIONS = "instructions"

class PowerUpType(Enum):
    MUSHROOM = "mushroom"
    FIRE_FLOWER = "fire_flower"
    STAR = "star"
    COIN = "coin"
    LIFE = "life"

class CharacterType(Enum):
    MARIO = "mario"
    LUIGI = "luigi"
    PEACH = "peach"
    TOAD = "toad"

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    lifetime: int
    size: int

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color,
                random.randint(20, 40),
                random.randint(3, 8)
            ))
    
    def update(self):
        for particle in self.particles[:]:
            particle.x += particle.vx
            particle.y += particle.vy
            particle.vy += 0.3  # Gravity
            particle.lifetime -= 1
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            size = int((particle.lifetime / 40) * particle.size)
            if size > 0:
                pygame.draw.circle(screen, particle.color, 
                                 (int(particle.x), int(particle.y)), size)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, character_type=CharacterType.MARIO):
        super().__init__()
        self.character = character_type
        self.width = 40
        self.height = 50
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.speed = 6
        self.direction = 1  # 1 for right, -1 for left
        
        # Power-up states
        self.is_big = False
        self.has_fire = False
        self.is_invincible = False
        self.invincible_timer = 0
        
        # Animation
        self.animation_frame = 0
        self.jump_count = 0
        self.max_jumps = 1
        
        # Stats
        self.lives = 3
        self.coins = 0
        
        # Character colors
        self.colors = {
            CharacterType.MARIO: (Colors.RED, Colors.DARK_RED, Colors.BROWN),
            CharacterType.LUIGI: ((0, 200, 0), Colors.DARK_GREEN, Colors.BROWN),
            CharacterType.PEACH: (Colors.PINK, (255, 105, 180), Colors.GOLD),
            CharacterType.TOAD: (Colors.RED, Colors.WHITE, Colors.BROWN)
        }
        self.update_appearance()

    def update_appearance(self):
        self.image.fill((0, 0, 0, 0))
        color1, color2, color3 = self.colors[self.character]
        
        # Scale based on power-up
        height = self.height if not self.is_big else int(self.height * 1.4)
        # Preserve horizontal position when recreating the image surface
        old_bottom = self.rect.bottom
        old_x = self.rect.x
        self.image = pygame.Surface((self.width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.bottom = old_bottom
        self.rect.x = old_x
        
        # Body
        body_rect = pygame.Rect(8, height // 3, 24, height // 2)
        pygame.draw.rect(self.image, color1, body_rect, border_radius=5)
        
        # Head
        head_size = 20 if not self.is_big else 24
        pygame.draw.circle(self.image, color3, (self.width // 2, height // 4), head_size // 2)
        
        # Hat
        hat_color = color1 if self.has_fire else color1
        pygame.draw.rect(self.image, hat_color, 
                        (self.width // 2 - 12, height // 4 - 12, 24, 8))
        pygame.draw.circle(self.image, hat_color, 
                          (self.width // 2, height // 4 - 8), 8)
        
        # Eyes
        eye_y = height // 4
        pygame.draw.circle(self.image, Colors.BLACK, (self.width // 2 - 5, eye_y), 2)
        pygame.draw.circle(self.image, Colors.BLACK, (self.width // 2 + 5, eye_y), 2)
        
        # Legs
        leg_y = height - 10
        pygame.draw.rect(self.image, color2, (10, leg_y, 8, 10))
        pygame.draw.rect(self.image, color2, (22, leg_y, 8, 10))
        
        # Invincible rainbow effect
        if self.is_invincible:
            rainbow_colors = [Colors.RED, Colors.ORANGE, Colors.YELLOW, 
                            Colors.GREEN, Colors.CYAN, Colors.PURPLE]
            frame_color = rainbow_colors[int(self.animation_frame / 3) % len(rainbow_colors)]
            # Draw effect relative to image rect
            pygame.draw.rect(self.image, frame_color, pygame.Rect(0, 0, self.rect.width, self.rect.height).inflate(4, 4), 3)

    def update(self, platforms, camera_offset=0):
        # Get keys
        keys = pygame.key.get_pressed()
        
        # Horizontal movement with acceleration
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.direction = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
            self.direction = 1
        else:
            self.vel_x *= 0.8  # Friction
        
        # Apply gravity
        self.vel_y += GRAVITY
        
        # Terminal velocity
        self.vel_y = min(self.vel_y, 20)
        
        # Animation
        if abs(self.vel_x) > 0.5:
            self.animation_frame += 0.2
        
        # Update invincibility
        if self.is_invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.is_invincible = False
        
        # Update position (separate horizontal and vertical movement for robust collisions)
        # Move horizontally
        move_x = int(self.vel_x)
        if move_x != 0:
            self.rect.x += move_x
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    if move_x > 0:
                        self.rect.right = platform.rect.left
                    elif move_x < 0:
                        self.rect.left = platform.rect.right

        # Move vertically
        move_y = int(self.vel_y)
        if move_y != 0:
            self.rect.y += move_y

        # Vertical collision
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if move_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                elif move_y < 0:  # Jumping
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0
        
        # Screen boundaries (adjusted for camera)
        if self.rect.left < camera_offset:
            self.rect.left = camera_offset
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.on_ground = True
        
        self.update_appearance()

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.jump_count = 1
        elif self.jump_count < self.max_jumps:
            self.vel_y = DOUBLE_JUMP_STRENGTH
            self.jump_count += 1
    
    def power_up(self, power_type):
        if power_type == PowerUpType.MUSHROOM:
            self.is_big = True
            self.max_jumps = 2
        elif power_type == PowerUpType.FIRE_FLOWER:
            self.is_big = True
            self.has_fire = True
        elif power_type == PowerUpType.STAR:
            self.is_invincible = True
            self.invincible_timer = 300  # 5 seconds
        elif power_type == PowerUpType.LIFE:
            self.lives += 1
    
    def take_damage(self):
        if self.is_invincible:
            return False
        
        if self.has_fire:
            self.has_fire = False
            return False
        elif self.is_big:
            self.is_big = False
            self.max_jumps = 1
            return False
        else:
            self.lives -= 1
            return True  # Lost a life

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="grass"):
        super().__init__()
        self.width = width
        self.height = height
        self.platform_type = platform_type
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.draw_platform()
    
    def draw_platform(self):
        if self.platform_type == "grass":
            # Grass platform with texture
            pygame.draw.rect(self.image, Colors.BROWN, (0, 0, self.width, self.height))
            pygame.draw.rect(self.image, Colors.GREEN, (0, 0, self.width, self.height // 3))
            # Add grass details
            for i in range(0, self.width, 10):
                pygame.draw.line(self.image, Colors.DARK_GREEN, 
                               (i, 0), (i + 5, self.height // 3), 2)
        elif self.platform_type == "brick":
            # Brick pattern
            brick_color = (180, 90, 0)
            mortar_color = (200, 200, 200)
            self.image.fill(mortar_color)
            brick_width = 30
            brick_height = 15
            for row in range(0, self.height, brick_height):
                offset = (brick_width // 2) if (row // brick_height) % 2 else 0
                for col in range(-brick_width // 2, self.width + brick_width, brick_width):
                    pygame.draw.rect(self.image, brick_color, 
                                   (col + offset, row, brick_width - 2, brick_height - 2))
        elif self.platform_type == "stone":
            # Stone blocks
            pygame.draw.rect(self.image, Colors.GRAY, (0, 0, self.width, self.height))
            pygame.draw.rect(self.image, Colors.DARK_GRAY, (2, 2, self.width - 4, self.height - 4))
        elif self.platform_type == "cloud":
            # Cloud platform
            self.image.fill((0, 0, 0, 0))
            pygame.draw.ellipse(self.image, Colors.WHITE, (0, 5, self.width, self.height - 5))
            pygame.draw.ellipse(self.image, (220, 220, 255), (5, 8, self.width - 10, self.height - 12))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 24
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rotation = 0
        self.pulse = 0
        self.collected = False
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        self.pulse += 0.1
        pulse_size = 2 + math.sin(self.pulse) * 2
        
        # Outer glow
        pygame.draw.circle(self.image, Colors.GOLD, 
                          (self.size // 2, self.size // 2), 
                          int(self.size // 2 + pulse_size))
        
        # Inner coin
        pygame.draw.circle(self.image, Colors.YELLOW, 
                          (self.size // 2, self.size // 2), 
                          self.size // 3)
        
        # Highlight
        pygame.draw.circle(self.image, Colors.WHITE, 
                          (self.size // 2 - 3, self.size // 2 - 3), 
                          self.size // 6)
        
        # Symbol
        font = pygame.font.Font(None, 18)
        text = font.render("$", True, Colors.GOLD)
        text_rect = text.get_rect(center=(self.size // 2, self.size // 2))
        self.image.blit(text, text_rect)
    
    def update(self):
        if not self.collected:
            self.update_image()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type):
        super().__init__()
        self.power_type = power_type
        self.size = 30
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.pulse = 0
        self.update_image()
    
    def update_image(self):
        self.image.fill((0, 0, 0, 0))
        self.pulse += 0.1
        
        if self.power_type == PowerUpType.MUSHROOM:
            # Red mushroom with white spots
            pygame.draw.circle(self.image, Colors.RED, 
                             (self.size // 2, self.size // 2 + 5), self.size // 2)
            pygame.draw.rect(self.image, (255, 220, 180), 
                           (self.size // 2 - 6, self.size // 2 + 5, 12, 12))
            # White spots
            pygame.draw.circle(self.image, Colors.WHITE, (10, 12), 4)
            pygame.draw.circle(self.image, Colors.WHITE, (20, 12), 4)
            pygame.draw.circle(self.image, Colors.WHITE, (15, 18), 3)
            
        elif self.power_type == PowerUpType.FIRE_FLOWER:
            # Fire flower
            center = self.size // 2
            for i in range(5):
                angle = (self.pulse + i * (2 * math.pi / 5))
                x = center + math.cos(angle) * 8
                y = center + math.sin(angle) * 8
                pygame.draw.circle(self.image, Colors.ORANGE, (int(x), int(y)), 5)
            pygame.draw.circle(self.image, Colors.YELLOW, (center, center), 6)
            pygame.draw.circle(self.image, Colors.RED, (center, center), 4)
            
        elif self.power_type == PowerUpType.STAR:
            # Star
            center = self.size // 2
            points = []
            for i in range(10):
                angle = (self.pulse + i * (2 * math.pi / 10))
                radius = 12 if i % 2 == 0 else 6
                x = center + math.cos(angle) * radius
                y = center + math.sin(angle) * radius
                points.append((int(x), int(y)))
            rainbow_colors = [Colors.RED, Colors.ORANGE, Colors.YELLOW, 
                            Colors.GREEN, Colors.CYAN]
            color = rainbow_colors[int(self.pulse * 10) % len(rainbow_colors)]
            pygame.draw.polygon(self.image, color, points)
        
        elif self.power_type == PowerUpType.LIFE:
            # 1-UP mushroom (green)
            pygame.draw.circle(self.image, Colors.GREEN, 
                             (self.size // 2, self.size // 2 + 5), self.size // 2)
            pygame.draw.rect(self.image, (255, 220, 180), 
                           (self.size // 2 - 6, self.size // 2 + 5, 12, 12))
            # White spots
            font = pygame.font.Font(None, 20)
            text = font.render("1UP", True, Colors.WHITE)
            self.image.blit(text, (5, 8))
    
    def update(self, platforms):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
        
        self.update_image()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, left_bound, right_bound, enemy_type="goomba"):
        super().__init__()
        self.enemy_type = enemy_type
        self.width = 35
        self.height = 35 if enemy_type == "goomba" else 45
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 2
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.animation_frame = 0
        self.stomped = False
        # Health depending on enemy type
        if self.enemy_type == "koopa":
            self.health = 2
        else:
            self.health = 1
        self.draw_enemy()

    def draw_enemy(self):
        self.image.fill((0, 0, 0, 0))
        
        if self.enemy_type == "goomba":
            # Goomba (mushroom enemy)
            body_color = Colors.BROWN
            pygame.draw.circle(self.image, body_color, 
                             (self.width // 2, self.height // 2), self.width // 2)
            # Angry eyes
            eye_y = self.height // 2 - 5
            pygame.draw.circle(self.image, Colors.WHITE, (12, eye_y), 4)
            pygame.draw.circle(self.image, Colors.WHITE, (23, eye_y), 4)
            pygame.draw.circle(self.image, Colors.BLACK, (12, eye_y), 2)
            pygame.draw.circle(self.image, Colors.BLACK, (23, eye_y), 2)
            # Frown
            pygame.draw.arc(self.image, Colors.BLACK, 
                          (8, eye_y + 5, 19, 10), 3.14, 0, 2)
            # Feet
            foot_y = self.height - 5
            pygame.draw.ellipse(self.image, Colors.DARK_BROWN, 
                              (5, foot_y - 5, 10, 8))
            pygame.draw.ellipse(self.image, Colors.DARK_BROWN, 
                              (20, foot_y - 5, 10, 8))
        
        elif self.enemy_type == "koopa":
            # Koopa Troopa (turtle)
            # Shell
            pygame.draw.ellipse(self.image, Colors.GREEN, 
                              (2, 10, self.width - 4, self.height - 15))
            pygame.draw.ellipse(self.image, Colors.YELLOW, 
                              (6, 14, self.width - 12, self.height - 23))
            # Head
            pygame.draw.circle(self.image, Colors.YELLOW, 
                             (self.width // 2, 8), 6)
            # Eyes
            pygame.draw.circle(self.image, Colors.WHITE, (15, 7), 2)
            pygame.draw.circle(self.image, Colors.WHITE, (20, 7), 2)
            pygame.draw.circle(self.image, Colors.BLACK, (15, 7), 1)
            pygame.draw.circle(self.image, Colors.BLACK, (20, 7), 1)

    def update(self, player=None):
        if self.stomped:
            return

        # Basic patrol movement
        if self.enemy_type in ("goomba", "koopa", "chaser"):
            # Chaser moves faster and will home slightly if player given
            if self.enemy_type == "chaser" and player is not None:
                # Small homing behavior
                if player.rect.x > self.rect.x:
                    self.vel_x = abs(self.vel_x) if abs(self.vel_x) < 6 else self.vel_x
                    self.rect.x += min(4, player.rect.x - self.rect.x)
                else:
                    self.rect.x -= min(4, self.rect.x - player.rect.x)
            else:
                self.rect.x += self.vel_x

            if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
                self.vel_x *= -1

        elif self.enemy_type == "fly":
            # Fly in sinusoidal path
            self.rect.x += self.vel_x
            self.rect.y += math.sin(pygame.time.get_ticks() / 300 + self.rect.x / 50) * 2
            if self.rect.left <= self.left_bound or self.rect.right >= self.right_bound:
                self.vel_x *= -1

        # Simple animation frame update
        self.animation_frame += 0.1
        self.draw_enemy()

    def take_damage(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            self.stomped = True
            self.image.fill((0, 0, 0, 0))
            pygame.draw.ellipse(self.image, Colors.BROWN, (0, self.height - 10, self.width, 10))
            return True
        return False
    
    def stomp(self):
        self.stomped = True
        self.image.fill((0, 0, 0, 0))
        # Draw squished enemy
        pygame.draw.ellipse(self.image, Colors.BROWN, 
                          (0, self.height - 10, self.width, 10))

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 80
        self.height = 100
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 10
        self.max_health = 10
        self.vel_x = 3
        self.vel_y = 0
        self.attack_timer = 0
        self.animation_frame = 0
        self.draw_boss()
    
    def draw_boss(self):
        self.image.fill((0, 0, 0, 0))
        
        # Large spiky shell
        pygame.draw.ellipse(self.image, Colors.DARK_GREEN, 
                          (5, 20, self.width - 10, self.height - 30))
        
        # Spikes
        for i in range(5):
            x = 15 + i * 15
            points = [(x, 20), (x - 8, 10), (x + 8, 10)]
            pygame.draw.polygon(self.image, Colors.RED, points)
        
        # Head
        pygame.draw.circle(self.image, Colors.YELLOW, (self.width // 2, 15), 18)
        
        # Angry eyes
        pygame.draw.circle(self.image, Colors.RED, (self.width // 2 - 8, 12), 6)
        pygame.draw.circle(self.image, Colors.RED, (self.width // 2 + 8, 12), 6)
        pygame.draw.circle(self.image, Colors.BLACK, (self.width // 2 - 8, 12), 3)
        pygame.draw.circle(self.image, Colors.BLACK, (self.width // 2 + 8, 12), 3)
        
        # Fangs
        pygame.draw.polygon(self.image, Colors.WHITE, 
                          [(self.width // 2 - 5, 20), (self.width // 2 - 8, 26), (self.width // 2 - 2, 26)])
        pygame.draw.polygon(self.image, Colors.WHITE, 
                          [(self.width // 2 + 5, 20), (self.width // 2 + 2, 26), (self.width // 2 + 8, 26)])
    
    def update(self, platforms, screen_width):
        self.animation_frame += 0.1
        self.attack_timer += 1
        
        # Move
        self.rect.x += self.vel_x
        if self.rect.left <= 0 or self.rect.right >= screen_width:
            self.vel_x *= -1
        
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
        
        self.draw_boss()
    
    def take_damage(self):
        self.health -= 1
        return self.health <= 0


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction=1, speed=10, owner="player"):
        super().__init__()
        self.owner = owner
        self.speed = speed * direction
        self.size = 8
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        color = Colors.CYAN if owner == "player" else Colors.RED
        pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.vx = self.speed

    def update(self, platforms=None):
        self.rect.x += int(self.vx)
        # Remove if offscreen far
        if self.rect.right < -2000 or self.rect.left > 20000:
            self.kill()

class Level:
    def __init__(self, level_number):
        self.level_number = level_number
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.boss = None
        self.goal_x = 0
        self.background_color = Colors.SKY_BLUE
        self.create_level()
    
    def create_level(self):
        if self.level_number == 1:
            # Level 1: Grassland
            self.background_color = Colors.SKY_BLUE
            
            # Ground
            self.platforms.add(Platform(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH * 3, 60, "grass"))
            
            # Platforms
            for i in range(8):
                self.platforms.add(Platform(200 + i * 250, 500, 120, 20, "grass"))
            
            # Floating platforms
            self.platforms.add(Platform(150, 350, 100, 20, "cloud"))
            self.platforms.add(Platform(400, 250, 100, 20, "cloud"))
            self.platforms.add(Platform(650, 350, 100, 20, "cloud"))
            self.platforms.add(Platform(900, 200, 120, 20, "cloud"))
            self.platforms.add(Platform(1200, 300, 100, 20, "cloud"))
            self.platforms.add(Platform(1500, 400, 100, 20, "grass"))
            self.platforms.add(Platform(1800, 350, 150, 20, "grass"))
            self.platforms.add(Platform(2100, 250, 150, 20, "brick"))
            
            # Coins
            for i in range(10):
                self.coins.add(Coin(250 + i * 200, 450))
                self.coins.add(Coin(200 + i * 180, 300))
            
            # Power-ups
            self.powerups.add(PowerUp(300, 300, PowerUpType.MUSHROOM))
            self.powerups.add(PowerUp(700, 150, PowerUpType.FIRE_FLOWER))
            self.powerups.add(PowerUp(1300, 250, PowerUpType.STAR))
            self.powerups.add(PowerUp(1900, 300, PowerUpType.LIFE))
            
            # Enemies
            self.enemies.add(Enemy(350, 480, 200, 500, "goomba"))
            self.enemies.add(Enemy(650, 480, 550, 800, "goomba"))
            self.enemies.add(Enemy(1000, 480, 900, 1200, "koopa"))
            self.enemies.add(Enemy(1400, 350, 1350, 1650, "goomba"))
            self.enemies.add(Enemy(1800, 480, 1700, 2000, "koopa"))
            
            self.goal_x = 2400
        
        elif self.level_number == 2:
            # Level 2: Underground
            self.background_color = (20, 20, 40)
            
            # Ground
            self.platforms.add(Platform(0, SCREEN_HEIGHT - 60, SCREEN_WIDTH * 4, 60, "stone"))
            
            # Stone platforms
            for i in range(12):
                height = 450 + (i % 3) * 100
                self.platforms.add(Platform(150 + i * 280, height, 140, 25, "stone"))
            
            # Brick platforms
            self.platforms.add(Platform(500, 300, 200, 20, "brick"))
            self.platforms.add(Platform(1000, 250, 180, 20, "brick"))
            self.platforms.add(Platform(1500, 350, 200, 20, "brick"))
            self.platforms.add(Platform(2000, 200, 150, 20, "brick"))
            self.platforms.add(Platform(2500, 300, 180, 20, "brick"))
            
            # Coins (more valuable underground)
            for i in range(15):
                self.coins.add(Coin(200 + i * 200, 400))
                self.coins.add(Coin(250 + i * 190, 250))
            
            # Power-ups
            self.powerups.add(PowerUp(400, 250, PowerUpType.MUSHROOM))
            self.powerups.add(PowerUp(900, 180, PowerUpType.FIRE_FLOWER))
            self.powerups.add(PowerUp(1600, 280, PowerUpType.STAR))
            self.powerups.add(PowerUp(2200, 130, PowerUpType.LIFE))
            
            # More enemies
            for i in range(8):
                x_pos = 400 + i * 350
                self.enemies.add(Enemy(x_pos, 480, x_pos - 50, x_pos + 200, "goomba"))
            
            self.enemies.add(Enemy(1200, 480, 1100, 1400, "koopa"))
            self.enemies.add(Enemy(2000, 480, 1900, 2200, "koopa"))
            
            self.goal_x = 3200
        
        elif self.level_number == 3:
            # Level 3: Castle + Boss
            self.background_color = (60, 20, 20)
            
            # Ground
            self.platforms.add(Platform(0, SCREEN_HEIGHT - 60, 2000, 60, "brick"))
            
            # Castle platforms
            for i in range(6):
                self.platforms.add(Platform(200 + i * 200, 500 - i * 40, 150, 25, "brick"))
            
            self.platforms.add(Platform(1400, 300, 200, 30, "brick"))
            
            # Power-ups
            self.powerups.add(PowerUp(300, 420, PowerUpType.MUSHROOM))
            self.powerups.add(PowerUp(700, 300, PowerUpType.FIRE_FLOWER))
            self.powerups.add(PowerUp(1100, 200, PowerUpType.STAR))
            
            # Enemies
            for i in range(5):
                self.enemies.add(Enemy(300 + i * 200, 480, 250 + i * 200, 450 + i * 200, "koopa"))
            
            # Boss
            self.boss = Boss(1600, 250)
            
            self.goal_x = 1900
        elif 4 <= self.level_number <= 15:
            # Procedurally generate varied levels for level_number 4..15
            seed = self.level_number
            random.seed(seed)
            difficulty = (self.level_number - 3)
            width_multiplier = 2 + difficulty // 3
            total_width = SCREEN_WIDTH * width_multiplier
            self.background_color = (
                max(10, 200 - difficulty * 10),
                max(10, 220 - difficulty * 8),
                max(20, 240 - difficulty * 6)
            )

            # Ground
            self.platforms.add(Platform(0, SCREEN_HEIGHT - 60, total_width, 60, random.choice(["grass", "stone", "brick"])))

            # Create varied platforms
            num_platforms = 8 + difficulty * 3
            for i in range(num_platforms):
                x = 200 + i * (150 + random.randint(0, 180))
                y = random.randint(200, SCREEN_HEIGHT - 200 - (difficulty * 5))
                ptype = random.choice(["grass", "cloud", "brick", "stone"])
                w = random.randint(80, 220)
                self.platforms.add(Platform(x, y, w, 20, ptype))

            # Coins scattered
            for i in range(20 + difficulty * 5):
                cx = random.randint(100, total_width - 100)
                cy = random.randint(150, SCREEN_HEIGHT - 150)
                self.coins.add(Coin(cx, cy))

            # Power-ups
            for i in range(max(1, difficulty // 2)):
                px = random.randint(200, total_width - 200)
                py = random.randint(150, SCREEN_HEIGHT - 200)
                pu = random.choice([PowerUpType.MUSHROOM, PowerUpType.FIRE_FLOWER, PowerUpType.STAR])
                self.powerups.add(PowerUp(px, py, pu))

            # Enemies: mix types and scale with difficulty
            enemy_types = ["goomba", "koopa", "fly", "chaser"]
            num_enemies = 6 + difficulty * 4
            for i in range(num_enemies):
                ex = random.randint(200, total_width - 200)
                ey = random.choice([SCREEN_HEIGHT - 80, SCREEN_HEIGHT - 120, random.randint(200, SCREEN_HEIGHT - 200)])
                et = random.choice(enemy_types)
                left_b = max(0, ex - random.randint(50, 250))
                right_b = min(total_width, ex + random.randint(150, 400))
                self.enemies.add(Enemy(ex, ey, left_b, right_b, et))

            # Occasional boss on higher levels
            if self.level_number >= 12:
                self.boss = Boss(total_width - 400, SCREEN_HEIGHT - 200)

            self.goal_x = total_width - 200

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ULTIMATE SUPER MARIO PRO")
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.current_level = 1
        self.character_type = CharacterType.MARIO
        self.player = None
        self.level = None
        self.camera_x = 0
        self.particle_system = ParticleSystem()
        self.score = 0
        self.time_left = 300  # 5 minutes per level
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'large': pygame.font.Font(None, 48),
            'medium': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }
        # Projectiles (player and enemy)
        self.projectiles = pygame.sprite.Group()

        # Sound assets (optional). Place wav files in assets/sounds/ to enable.
        self.sounds = {}
        try:
            self.sounds['jump'] = pygame.mixer.Sound('assets/sounds/jump.wav')
            self.sounds['coin'] = pygame.mixer.Sound('assets/sounds/coin.wav')
            self.sounds['powerup'] = pygame.mixer.Sound('assets/sounds/powerup.wav')
            self.sounds['stomp'] = pygame.mixer.Sound('assets/sounds/stomp.wav')
            self.sounds['fire'] = pygame.mixer.Sound('assets/sounds/fire.wav')
        except Exception:
            # Sounds are optional; ignore load errors
            self.sounds = {}
    
    def draw_menu(self):
        self.screen.fill(Colors.SKY_BLUE)
        
        # Animated title
        pulse = math.sin(pygame.time.get_ticks() / 300) * 10
        
        # Title glow
        for i in range(5, 0, -1):
            glow_color = (255 - i * 40, 0, 0)
            title_glow = self.fonts['title'].render("SUPER MARIO PRO", True, glow_color)
            rect = title_glow.get_rect(center=(SCREEN_WIDTH // 2 + i, 100 + pulse + i))
            self.screen.blit(title_glow, rect)
        
        title = self.fonts['title'].render("SUPER MARIO PRO", True, Colors.RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100 + pulse))
        self.screen.blit(title, title_rect)
        
        subtitle = self.fonts['medium'].render("Ultimate Edition", True, Colors.GOLD)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        options = [
            ("1 - Start Game", 300),
            ("2 - Character Select", 360),
            ("3 - Instructions", 420),
            ("Q - Quit", 520)
        ]
        
        for text, y in options:
            option_text = self.fonts['medium'].render(text, True, Colors.WHITE)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y))
            
            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            if option_rect.collidepoint(mouse_pos):
                option_text = self.fonts['medium'].render(text, True, Colors.YELLOW)
                pygame.draw.rect(self.screen, Colors.WHITE, option_rect.inflate(20, 10), 3, border_radius=10)
            
            self.screen.blit(option_text, option_rect)
        
        pygame.display.flip()
    
    def draw_character_select(self):
        self.screen.fill(Colors.DEEP_SKY)
        
        title = self.fonts['large'].render("Choose Your Character", True, Colors.WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        characters = [
            (CharacterType.MARIO, "Mario", "Balanced", 200),
            (CharacterType.LUIGI, "Luigi", "High Jump", 400),
            (CharacterType.PEACH, "Peach", "Slow Fall", 600),
            (CharacterType.TOAD, "Toad", "Fast Speed", 800)
        ]
        
        for i, (char_type, name, ability, x) in enumerate(characters):
            # Draw character preview
            preview_rect = pygame.Rect(x - 60, 200, 120, 150)
            
            if self.character_type == char_type:
                pygame.draw.rect(self.screen, Colors.YELLOW, preview_rect.inflate(10, 10), 5, border_radius=10)
            else:
                pygame.draw.rect(self.screen, Colors.WHITE, preview_rect, 3, border_radius=10)
            
            # Character name
            name_text = self.fonts['medium'].render(name, True, Colors.WHITE)
            name_rect = name_text.get_rect(center=(x, 380))
            self.screen.blit(name_text, name_rect)
            
            # Ability
            ability_text = self.fonts['small'].render(ability, True, Colors.GOLD)
            ability_rect = ability_text.get_rect(center=(x, 410))
            self.screen.blit(ability_text, ability_rect)
            
            # Number key
            key_text = self.fonts['small'].render(f"Press {i + 1}", True, Colors.WHITE)
            key_rect = key_text.get_rect(center=(x, 450))
            self.screen.blit(key_text, key_rect)
        
        back_text = self.fonts['small'].render("Press ESC to go back", True, Colors.WHITE)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 600))
        self.screen.blit(back_text, back_rect)
        
        pygame.display.flip()

    def draw_instructions(self):
        self.screen.fill(Colors.DEEP_SKY)
        title = self.fonts['large'].render("Instructions", True, Colors.WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        lines = [
            "Move: Arrow Keys or A/D",
            "Jump: Space, W or Up Arrow (double-jump if powered up)",
            "Pause: ESC",
            "Collect coins and power-ups, stomp enemies to score",
            "Press ESC to return to menu"
        ]

        for i, line in enumerate(lines):
            txt = self.fonts['medium'].render(line, True, Colors.WHITE)
            rect = txt.get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 50))
            self.screen.blit(txt, rect)

        pygame.display.flip()
    
    def start_level(self):
        self.level = Level(self.current_level)
        self.player = Player(50, SCREEN_HEIGHT - 150, self.character_type)
        self.camera_x = 0
        self.time_left = 300
        # Clear projectiles when starting a level
        self.projectiles.empty()
        self.state = GameState.PLAYING
    
    def update_game(self):
        # Update camera to follow player
        target_camera_x = self.player.rect.x - SCREEN_WIDTH // 3
        self.camera_x = max(0, target_camera_x)
        
        # Update player
        self.player.update(self.level.platforms, self.camera_x)
        
        # Update enemies
        for enemy in list(self.level.enemies):
            enemy.update(self.player)
            # Check stomping
            if self.player.rect.colliderect(enemy.rect) and not enemy.stomped:
                if self.player.vel_y > 0 and self.player.rect.bottom < enemy.rect.centery:
                    enemy.stomp()
                    self.player.vel_y = JUMP_STRENGTH // 2
                    self.score += 100
                    self.particle_system.emit(enemy.rect.centerx, enemy.rect.centery, Colors.BROWN, 15)
                elif not self.player.is_invincible:
                    if self.player.take_damage():
                        self.state = GameState.GAME_OVER
                    self.particle_system.emit(self.player.rect.centerx, self.player.rect.centery, Colors.RED, 20)
        
        # Update powerups
        for powerup in self.level.powerups:
            powerup.update(self.level.platforms)
            if self.player.rect.colliderect(powerup.rect):
                self.player.power_up(powerup.power_type)
                powerup.kill()
                self.score += 200
                self.particle_system.emit(powerup.rect.centerx, powerup.rect.centery, Colors.GOLD, 20)
        
        # Update coins
        for coin in self.level.coins:
            coin.update()
            if self.player.rect.colliderect(coin.rect) and not coin.collected:
                coin.collected = True
                coin.kill()
                self.player.coins += 1
                self.score += 50
                self.particle_system.emit(coin.rect.centerx, coin.rect.centery, Colors.GOLD, 10)
        
        # Update boss
        if self.level.boss:
            self.level.boss.update(self.level.platforms, self.level.goal_x + 200)
            if self.player.rect.colliderect(self.level.boss.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom < self.level.boss.rect.centery:
                    if self.level.boss.take_damage():
                        self.level.boss = None
                        self.score += 1000
                    else:
                        self.player.vel_y = JUMP_STRENGTH // 2
                        self.score += 200
                    self.particle_system.emit(self.level.boss.rect.centerx, 
                                            self.level.boss.rect.centery, Colors.RED, 25)
                elif not self.player.is_invincible:
                    if self.player.take_damage():
                        self.state = GameState.GAME_OVER
        
        # Update particles
        self.particle_system.update()

        # Update projectiles and check collisions
        for proj in list(self.projectiles):
            proj.update(self.level.platforms)
            # Adjust for camera when checking collision positions - use world coords
            # Check collisions with enemies
            for enemy in list(self.level.enemies):
                if proj.owner == "player" and proj.rect.colliderect(enemy.rect) and not enemy.stomped:
                    enemy_dead = enemy.take_damage(1)
                    proj.kill()
                    if enemy_dead:
                        self.score += 150
                        self.particle_system.emit(enemy.rect.centerx, enemy.rect.centery, Colors.BROWN, 12)
                    break

            # Check collisions with boss
            if proj.owner == "player" and self.level.boss and proj.rect.colliderect(self.level.boss.rect):
                if self.level.boss.take_damage():
                    self.level.boss = None
                    self.score += 500
                else:
                    self.score += 100
                proj.kill()
        
        # Check level completion
        if self.player.rect.x > self.level.goal_x:
            self.state = GameState.LEVEL_COMPLETE
        
        # Check fall off
        if self.player.rect.top > SCREEN_HEIGHT:
            if self.player.take_damage():
                self.state = GameState.GAME_OVER
            else:
                self.player.rect.x = 50
                self.player.rect.y = SCREEN_HEIGHT - 150
        
        # Update timer
        self.time_left -= 1 / FPS
        if self.time_left <= 0:
            self.state = GameState.GAME_OVER
    
    def draw_game(self):
        # Background
        self.screen.fill(self.level.background_color)
        
        # Draw clouds
        for i in range(5):
            x = (i * 300 - self.camera_x * 0.3) % (SCREEN_WIDTH + 200)
            pygame.draw.ellipse(self.screen, Colors.WHITE, (int(x), 100 + i * 40, 80, 40))
            pygame.draw.ellipse(self.screen, Colors.WHITE, (int(x) + 30, 90 + i * 40, 60, 50))
            pygame.draw.ellipse(self.screen, Colors.WHITE, (int(x) + 60, 100 + i * 40, 70, 40))
        
        # Draw level objects (adjusted for camera)
        for platform in self.level.platforms:
            adjusted_rect = platform.rect.copy()
            adjusted_rect.x -= self.camera_x
            self.screen.blit(platform.image, adjusted_rect)
        
        for coin in self.level.coins:
            adjusted_rect = coin.rect.copy()
            adjusted_rect.x -= self.camera_x
            self.screen.blit(coin.image, adjusted_rect)
        
        for powerup in self.level.powerups:
            adjusted_rect = powerup.rect.copy()
            adjusted_rect.x -= self.camera_x
            self.screen.blit(powerup.image, adjusted_rect)
        
        for enemy in self.level.enemies:
            adjusted_rect = enemy.rect.copy()
            adjusted_rect.x -= self.camera_x
            self.screen.blit(enemy.image, adjusted_rect)

        # Draw projectiles
        for proj in self.projectiles:
            adjusted_rect = proj.rect.copy()
            adjusted_rect.x -= self.camera_x
            self.screen.blit(proj.image, adjusted_rect)
        
        if self.level.boss:
            adjusted_rect = self.level.boss.rect.copy()
            adjusted_rect.x -= self.camera_x
            self.screen.blit(self.level.boss.image, adjusted_rect)
            # Boss health bar
            if adjusted_rect.x > -100 and adjusted_rect.x < SCREEN_WIDTH + 100:
                health_percent = self.level.boss.health / self.level.boss.max_health
                pygame.draw.rect(self.screen, Colors.RED, 
                               (adjusted_rect.x, adjusted_rect.y - 20, 80, 10))
                pygame.draw.rect(self.screen, Colors.GREEN, 
                               (adjusted_rect.x, adjusted_rect.y - 20, int(80 * health_percent), 10))
        
        # Draw player
        adjusted_player_rect = self.player.rect.copy()
        adjusted_player_rect.x -= self.camera_x
        self.screen.blit(self.player.image, adjusted_player_rect)
        
        # Draw particles
        for particle in self.particle_system.particles:
            adjusted_x = int(particle.x - self.camera_x)
            adjusted_y = int(particle.y)
            size = int((particle.lifetime / 40) * particle.size)
            if size > 0 and adjusted_x > -50 and adjusted_x < SCREEN_WIDTH + 50:
                pygame.draw.circle(self.screen, particle.color, (adjusted_x, adjusted_y), size)
        
        # Draw HUD
        self.draw_hud()
        
        pygame.display.flip()
    
    def draw_hud(self):
        # Score
        score_text = self.fonts['medium'].render(f"Score: {self.score}", True, Colors.WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Coins
        coin_text = self.fonts['medium'].render(f"Coins: {self.player.coins}", True, Colors.GOLD)
        self.screen.blit(coin_text, (20, 60))
        
        # Lives
        lives_text = self.fonts['medium'].render(f"Lives: {self.player.lives}", True, Colors.RED)
        self.screen.blit(lives_text, (20, 100))
        
        # Time
        time_color = Colors.RED if self.time_left < 30 else Colors.WHITE
        time_text = self.fonts['medium'].render(f"Time: {int(self.time_left)}", True, time_color)
        time_rect = time_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        self.screen.blit(time_text, time_rect)
        
        # Level
        level_text = self.fonts['medium'].render(f"Level {self.current_level}", True, Colors.WHITE)
        level_rect = level_text.get_rect(topright=(SCREEN_WIDTH - 20, 60))
        self.screen.blit(level_text, level_rect)

        # --- Debug info (shows velocity and key states) ---
        try:
            keys = pygame.key.get_pressed()
            left_on = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right_on = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            vel_text = self.fonts['small'].render(f"vel_x={self.player.vel_x:.2f} vel_y={self.player.vel_y:.2f}", True, Colors.WHITE)
            keys_text = self.fonts['small'].render(f"Left={int(left_on)} Right={int(right_on)}", True, Colors.WHITE)
            self.screen.blit(vel_text, (20, SCREEN_HEIGHT - 60))
            self.screen.blit(keys_text, (20, SCREEN_HEIGHT - 35))
        except Exception:
            # If player or fonts are not available yet, skip debug overlay
            pass
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.state == GameState.MENU:
                        if event.key == pygame.K_1:
                            self.start_level()
                        elif event.key == pygame.K_2:
                            self.state = GameState.CHARACTER_SELECT
                        elif event.key == pygame.K_3:
                            self.state = GameState.INSTRUCTIONS
                        elif event.key == pygame.K_q:
                            running = False
                    
                    elif self.state == GameState.CHARACTER_SELECT:
                        if event.key == pygame.K_1:
                            self.character_type = CharacterType.MARIO
                        elif event.key == pygame.K_2:
                            self.character_type = CharacterType.LUIGI
                        elif event.key == pygame.K_3:
                            self.character_type = CharacterType.PEACH
                        elif event.key == pygame.K_4:
                            self.character_type = CharacterType.TOAD
                        elif event.key == pygame.K_ESCAPE:
                            self.state = GameState.MENU
                        elif event.key == pygame.K_RETURN:
                            self.start_level()
                    
                    elif self.state == GameState.PLAYING:
                        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                            self.player.jump()
                            if 'jump' in self.sounds:
                                try:
                                    self.sounds['jump'].play()
                                except Exception:
                                    pass
                        elif event.key in (pygame.K_f, pygame.K_z, pygame.K_LCTRL):
                            # Fire projectile if player has fire power-up
                            if self.player.has_fire:
                                direction = self.player.direction
                                px = self.player.rect.centerx
                                py = self.player.rect.centery - 10
                                proj = Projectile(px, py, direction, speed=12, owner="player")
                                self.projectiles.add(proj)
                                if 'fire' in self.sounds:
                                    try:
                                        self.sounds['fire'].play()
                                    except Exception:
                                        pass
                        elif event.key == pygame.K_ESCAPE:
                            self.state = GameState.PAUSED
                    
                    elif self.state == GameState.PAUSED:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.PLAYING
                        elif event.key == pygame.K_q:
                            self.state = GameState.MENU
                    
                    elif self.state == GameState.LEVEL_COMPLETE:
                        if event.key == pygame.K_RETURN:
                            self.current_level += 1
                            if self.current_level > 15:
                                self.current_level = 1
                            self.start_level()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = GameState.MENU
                    
                    elif self.state == GameState.GAME_OVER:
                        if event.key == pygame.K_RETURN:
                            self.score = 0
                            self.current_level = 1
                            self.start_level()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = GameState.MENU
                    elif self.state == GameState.INSTRUCTIONS:
                        if event.key == pygame.K_ESCAPE:
                            self.state = GameState.MENU
            
            # Game logic
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.CHARACTER_SELECT:
                self.draw_character_select()
            elif self.state == GameState.INSTRUCTIONS:
                self.draw_instructions()
            elif self.state == GameState.PLAYING:
                self.update_game()
                self.draw_game()
            elif self.state == GameState.PAUSED:
                self.draw_game()
                # Pause overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                self.screen.blit(overlay, (0, 0))
                pause_text = self.fonts['large'].render("PAUSED", True, Colors.WHITE)
                pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(pause_text, pause_rect)
                inst_text = self.fonts['small'].render("ESC - Resume | Q - Quit to Menu", True, Colors.WHITE)
                inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                self.screen.blit(inst_text, inst_rect)
                pygame.display.flip()
            elif self.state == GameState.LEVEL_COMPLETE:
                self.screen.fill(Colors.SKY_BLUE)
                complete_text = self.fonts['large'].render("LEVEL COMPLETE!", True, Colors.GOLD)
                complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
                self.screen.blit(complete_text, complete_rect)
                
                score_text = self.fonts['medium'].render(f"Score: {self.score}", True, Colors.WHITE)
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(score_text, score_rect)
                
                coins_text = self.fonts['medium'].render(f"Coins: {self.player.coins}", True, Colors.GOLD)
                coins_rect = coins_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
                self.screen.blit(coins_text, coins_rect)
                
                continue_text = self.fonts['small'].render("ENTER - Next Level | ESC - Menu", True, Colors.WHITE)
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
                self.screen.blit(continue_text, continue_rect)
                pygame.display.flip()
            elif self.state == GameState.GAME_OVER:
                self.screen.fill(Colors.DARK_RED)
                over_text = self.fonts['large'].render("GAME OVER", True, Colors.WHITE)
                over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
                self.screen.blit(over_text, over_rect)
                
                final_score_text = self.fonts['medium'].render(f"Final Score: {self.score}", True, Colors.GOLD)
                final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(final_score_text, final_score_rect)
                
                retry_text = self.fonts['small'].render("ENTER - Try Again | ESC - Menu", True, Colors.WHITE)
                retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                self.screen.blit(retry_text, retry_rect)
                pygame.display.flip()
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
