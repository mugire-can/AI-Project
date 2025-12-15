"""
ULTIMATE RACING PRO - AAA Quality Racing Game
Features: Advanced 3D rendering, multiple game modes, car customization,
weather effects, day/night cycle, multiplayer AI, power-ups, and more!
"""

import pygame
import math
import random
import sys
import json
import argparse
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
import os
from enum import Enum
try:
    import numpy as np
except Exception:
    np = None

# Import AI client for intelligent features
try:
    from ai_client import ClaudeAIClient
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI client not available. Running with standard AI.")

pygame.init()
pygame.mixer.init()

class TrackDecoration:
    def __init__(self, x: float, y: float, decoration_type: str):
        self.x = x
        self.y = y
        self.type = decoration_type
        self.height = random.randint(100, 300) if decoration_type == "building" else random.randint(50, 150)
        self.width = random.randint(80, 200) if decoration_type == "building" else random.randint(40, 80)
        self.color = self._get_color()
        self.details = self._generate_details()
        
    def _get_color(self) -> Tuple[int, int, int]:
        if self.type == "building":
            return random.choice([
                (100, 100, 100),  # Gray
                (120, 80, 80),    # Brown
                (80, 100, 120)    # Blue-gray
            ])
        elif self.type == "tree":
            return random.choice([
                (34, 139, 34),    # Forest green
                (0, 100, 0),      # Dark green
                (50, 205, 50)     # Lime green
            ])
        elif self.type == "barrier":
            return (200, 200, 200)  # Light gray
        else:  # billboard
            return random.choice([Colors.RED, Colors.BLUE, Colors.YELLOW, Colors.CYAN])
            
    def _generate_details(self) -> dict:
        details = {}
        if self.type == "building":
            details["windows"] = []
            window_rows = random.randint(3, 8)
            window_cols = random.randint(2, 5)
            for row in range(window_rows):
                for col in range(window_cols):
                    lit = random.random() > 0.3
                    details["windows"].append({
                        "x": col * (self.width / (window_cols + 1)),
                        "y": row * (self.height / (window_rows + 1)),
                        "lit": lit
                    })
        elif self.type == "billboard":
            details["text"] = random.choice([
                "SPEED", "NITRO", "DRIFT KING", "RACE!", "TURBO"
            ])
        return details

class LightSource:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], intensity: float, radius: float):
        self.x = x
        self.y = y
        self.color = color
        self.intensity = intensity
        self.radius = radius
        self.flicker = 0
        
    def update(self):
        # Add subtle flickering effect
        self.flicker = random.uniform(-0.1, 0.1)
        
    def get_illumination(self, target_x: float, target_y: float) -> float:
        distance = math.hypot(target_x - self.x, target_y - self.y)
        if distance > self.radius:
            return 0
        return self.intensity * (1 - distance/self.radius) * (1 + self.flicker)

# Screen settings - Compatible with most displays
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Advanced color palette
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (220, 20, 60)
    BLUE = (30, 144, 255)
    GREEN = (50, 205, 50)
    YELLOW = (255, 215, 0)
    ORANGE = (255, 140, 0)
    PURPLE = (138, 43, 226)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    GRAY = (128, 128, 128)
    DARK_GRAY = (50, 50, 50)
    
    # Environment
    SKY_DAY = (135, 206, 235)
    SKY_SUNSET = (255, 99, 71)
    SKY_NIGHT = (25, 25, 112)
    ROAD = (50, 50, 50)
    GRASS = (34, 139, 34)
    SAND = (194, 178, 128)
    WATER = (0, 119, 190)
    
    # Weather
    RAIN = (150, 150, 200)
    SNOW = (255, 255, 255)
    FOG = (200, 200, 200)

class GameMode(Enum):
    MENU = "menu"
    RACE = "race"
    TIME_TRIAL = "time_trial"
    DRIFT = "drift"
    GARAGE = "garage"
    SETTINGS = "settings"
    LEADERBOARD = "leaderboard"

class Weather(Enum):
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"
    FOG = "fog"
    STORM = "storm"

class TimeOfDay(Enum):
    DAY = "day"
    SUNSET = "sunset"
    NIGHT = "night"

@dataclass
class CarStats:
    name: str
    max_speed: float
    acceleration: float
    handling: float
    drift_factor: float
    weight: int
    nitro_capacity: float
    price: int
    color: Tuple[int, int, int]

class PowerUp:
    def __init__(self, x, y, type_name):
        self.x = x
        self.y = y
        self.type = type_name  # speed, shield, nitro, coins
        self.collected = False
        self.radius = 20
        self.rotation = 0
        self.pulse = 0
        
    def update(self):
        self.rotation += 5
        self.pulse = math.sin(pygame.time.get_ticks() * 0.005) * 5
        
    def draw(self, screen, camera_y):
        if not self.collected:
            y = self.y - camera_y
            if -50 < y < SCREEN_HEIGHT + 50:
                color_map = {
                    'speed': Colors.CYAN,
                    'shield': Colors.GREEN,
                    'nitro': Colors.ORANGE,
                    'coins': Colors.GOLD
                }
                color = color_map.get(self.type, Colors.WHITE)
                
                # Glow effect
                for i in range(3):
                    glow_radius = self.radius + self.pulse + (i * 10)
                    glow_surface = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
                    alpha = 50 - (i * 15)
                    pygame.draw.circle(glow_surface, (*color, alpha), 
                                     (glow_radius * 2, glow_radius * 2), glow_radius)
                    screen.blit(glow_surface, (int(self.x - glow_radius * 2), int(y - glow_radius * 2)))
                
                # Main powerup
                pygame.draw.circle(screen, color, (int(self.x), int(y)), int(self.radius + self.pulse))
                pygame.draw.circle(screen, Colors.WHITE, (int(self.x), int(y)), 
                                 int(self.radius + self.pulse - 3), 2)

    def on_collect(self, car, game):
        """Called when a car collects this powerup. Spawn particles and apply extra effects."""
        # Burst of particles
        for _ in range(20):
            game.particles.append(Particle(
                self.x + random.uniform(-10, 10),
                self.y + random.uniform(-10, 10),
                random.uniform(-3, 3),
                random.uniform(-3, 3),
                Colors.GOLD if self.type == 'coins' else Colors.CYAN,
                random.randint(2, 6),
                random.randint(15, 40),
                'spark'
            ))

        # Small healing effect for shield or coins
        if self.type == 'shield':
            car.shield_active = True
        if self.type == 'coins':
            car.coins += 50
        if self.type == 'nitro':
            car.nitro = min(car.stats.nitro_capacity, car.nitro + 100)

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime, particle_type="normal"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.2
        self.type = particle_type
        self.rotation = random.uniform(0, 360)
        self.angular_velocity = random.uniform(-5, 5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        if self.type == "spark":
            self.vy += self.gravity * 0.5
            self.lifetime -= 2
        elif self.type == "smoke":
            self.vy -= 0.1  # Smoke rises
            self.vx += random.uniform(-0.1, 0.1)  # Smoke wavers
            self.lifetime -= 0.5
        elif self.type == "nitro":
            self.lifetime -= 3
            self.rotation += self.angular_velocity
        elif self.type == "raindrop":
            # Fast falling raindrop
            self.vy += self.gravity * 5
            self.lifetime -= 1
            # When lifetime ends, create small splash by returning flag (handled externally)
        else:  # normal particles
            self.vy += self.gravity
            self.lifetime -= 1
            
        self.vx *= 0.98
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
            
            if self.type == "spark":
                # Draw elongated spark
                spark_surface = pygame.Surface((size * 4, size * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(spark_surface, (*self.color[:3], alpha), (0, 0, size * 4, size * 2))
                rotated = pygame.transform.rotate(spark_surface, math.degrees(math.atan2(self.vy, self.vx)))
                screen.blit(rotated, (int(self.x - rotated.get_width()/2), 
                                    int(self.y - rotated.get_height()/2)))
                
                # Add glow effect
                glow_size = size * 6
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                glow_color = (*self.color[:3], alpha // 4)
                pygame.draw.circle(glow_surface, glow_color, (glow_size//2, glow_size//2), glow_size//2)
                screen.blit(glow_surface, (int(self.x - glow_size/2), int(self.y - glow_size/2)))
                
            elif self.type == "smoke":
                # Draw billowing smoke with gradient
                smoke_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                for r in range(3):
                    radius = size * (3-r) / 3
                    smoke_alpha = alpha * (3-r) / 5
                    pygame.draw.circle(smoke_surface, (*self.color[:3], int(smoke_alpha)),
                                    (size * 1.5, size * 1.5), radius)
                screen.blit(smoke_surface, (int(self.x - size * 1.5), int(self.y - size * 1.5)))
                
            elif self.type == "nitro":
                # Draw flame-like nitro particles
                flame_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                points = []
                num_points = 8
                for i in range(num_points):
                    angle = self.rotation + (i * 360 / num_points)
                    rad = math.radians(angle)
                    radius = size * (1 + math.sin(angle * 3) * 0.3)
                    px = size * 2 + math.cos(rad) * radius
                    py = size * 2 + math.sin(rad) * radius
                    points.append((px, py))
                
                if len(points) >= 3:
                    pygame.draw.polygon(flame_surface, (*self.color[:3], alpha), points)
                screen.blit(flame_surface, (int(self.x - size * 2), int(self.y - size * 2)))
                
                # Add glow
                glow_radius = size * 3
                glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                glow_color = (*self.color[:3], alpha // 3)
                pygame.draw.circle(glow_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surface, (int(self.x - glow_radius), int(self.y - glow_radius)))
            elif self.type == "raindrop":
                # Draw a quick streak
                length = max(2, int(self.size * 4))
                end_x = int(self.x + self.vx * 2)
                end_y = int(self.y + self.vy * 0.5)
                pygame.draw.line(screen, (*self.color[:3], alpha), (int(self.x), int(self.y)), (end_x, end_y), max(1, int(self.size/2)))
            
            
            else:  # normal particles
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color[:3], alpha), (size, size), size)
                screen.blit(s, (int(self.x - size), int(self.y - size)))

class AdvancedCar:
    def __init__(self, x, y, stats: CarStats, is_player=False):
        self.x = x
        self.y = y
        self.stats = stats
        self.is_player = is_player
        
        # Physics
        self.velocity = 0
        self.angle = 0
        self.drift_angle = 0
        self.angular_velocity = 0
        
        # Power-ups
        self.nitro = stats.nitro_capacity
        self.nitro_active = False
        self.shield_active = False
        self.speed_boost = 1.0
        self.coins = 0
        
        # Rendering
        self.width = 60
        self.height = 100
        self.trail_points = []
        
        # Race stats
        self.lap = 0
        self.checkpoint_index = 0
        self.race_time = 0
        self.best_lap = float('inf')
        self.drift_score = 0
        self.combo_multiplier = 1

        # Damage/health
        self.health = 100
        self.damage_level = 0  # 0..100

    def apply_powerup(self, powerup_type):
        if powerup_type == 'speed':
            self.speed_boost = 1.5
        elif powerup_type == 'shield':
            self.shield_active = True
            # small heal
            self.health = min(100, self.health + 15)
        elif powerup_type == 'nitro':
            self.nitro = min(self.stats.nitro_capacity, self.nitro + 50)
        elif powerup_type == 'coins':
            self.coins += 100

    def take_damage(self, amount):
        if self.shield_active:
            # shield absorbs half
            amount *= 0.5
        self.health = max(0, self.health - amount)
        # Increase damage level and reduce performance slightly
        self.damage_level = min(100, self.damage_level + int(amount))
        # Reduce max_speed slightly based on damage
        self.stats.max_speed = max(5, self.stats.max_speed * (1 - self.damage_level / 600.0))
            
    def update_physics(self, dt, keys=None):
        # Ensure dt is reasonable
        if dt <= 0 or dt > 0.1:
            dt = 0.016  # Default to ~60 FPS
            
        if self.is_player and keys:
            # Acceleration
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                target_speed = self.stats.max_speed * self.speed_boost
                self.velocity += self.stats.acceleration
                self.velocity = min(self.velocity, target_speed)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.velocity -= self.stats.acceleration * 1.5
                self.velocity = max(self.velocity, -self.stats.max_speed * 0.5)
            else:
                # Natural deceleration
                if self.velocity > 0:
                    self.velocity -= 0.3
                    self.velocity = max(0, self.velocity)
                elif self.velocity < 0:
                    self.velocity += 0.3
                    self.velocity = min(0, self.velocity)
            
            # Steering
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                turn_amount = self.stats.handling * (1.0 - abs(self.velocity) / self.stats.max_speed * 0.5)
                self.angular_velocity -= turn_amount
                if abs(self.velocity) > self.stats.max_speed * 0.5:
                    self.drift_angle = -15
                    self.drift_score += abs(self.velocity) * 0.1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                turn_amount = self.stats.handling * (1.0 - abs(self.velocity) / self.stats.max_speed * 0.5)
                self.angular_velocity += turn_amount
                if abs(self.velocity) > self.stats.max_speed * 0.5:
                    self.drift_angle = 15
                    self.drift_score += abs(self.velocity) * 0.1
            else:
                self.drift_angle *= 0.9
                if abs(self.drift_score) > 100:
                    self.combo_multiplier += 1
                self.drift_score *= 0.95
            
            # Nitro
            if (keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]) and self.nitro > 0:
                self.nitro_active = True
                self.nitro -= 1
                self.velocity += self.stats.acceleration * 2
            else:
                self.nitro_active = False
                self.nitro = min(self.stats.nitro_capacity, self.nitro + 0.2)
        
        # Apply physics
        self.angular_velocity *= 0.85  # Angular damping
        self.angle += self.angular_velocity
        
        # Update position
        rad_angle = math.radians(self.angle)
        self.x += math.sin(rad_angle) * self.velocity
        self.y -= math.cos(rad_angle) * self.velocity
        
        # Update trail
        if len(self.trail_points) > 20:
            self.trail_points.pop(0)
        if abs(self.velocity) > 1:
            self.trail_points.append((self.x, self.y, self.velocity))
        
        # Speed boost decay
        if self.speed_boost > 1.0:
            self.speed_boost -= 0.01
            self.speed_boost = max(1.0, self.speed_boost)
    
    def draw(self, screen, camera_x, camera_y, particles):
        draw_x = self.x - camera_x
        draw_y = self.y - camera_y
        
        # Ground shadow with perspective
        shadow_stretch = 1.0 + (abs(self.velocity) / self.stats.max_speed) * 0.5
        shadow_surface = pygame.Surface((self.width * 2 * shadow_stretch, self.height * 2), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(
            self.width // 2, 
            self.height // 2 + 10 * (1 + abs(self.velocity) / 20),
            self.width * shadow_stretch, 
            self.height * 0.8
        )
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), shadow_rect)
        rotated_shadow = pygame.transform.rotate(shadow_surface, -self.angle + self.drift_angle)
        shadow_rect = rotated_shadow.get_rect(center=(draw_x, draw_y + 5))
        screen.blit(rotated_shadow, shadow_rect)
        
        # Draw drift marks
        if abs(self.drift_angle) > 10 and abs(self.velocity) > 5:
            drift_intensity = min(1.0, abs(self.drift_angle) / 45.0)
            for _ in range(3):
                # Smoke particles
                particles.append(Particle(
                    self.x + random.uniform(-20, 20),
                    self.y + random.uniform(-20, 20),
                    random.uniform(-1, 1) * drift_intensity,
                    random.uniform(-1, 1) * drift_intensity,
                    (100, 100, 100),
                    random.randint(8, 12),
                    60,
                    "smoke"
                ))
                # Sparks during intense drifting
                if abs(self.drift_angle) > 30:
                    particles.append(Particle(
                        self.x + random.uniform(-15, 15),
                        self.y + random.uniform(-15, 15),
                        random.uniform(-3, 3),
                        random.uniform(-2, 2),
                        Colors.ORANGE,
                        random.randint(2, 4),
                        15,
                        "spark"
                    ))
        
        # Draw nitro trail
        if self.nitro_active:
            nitro_colors = [Colors.CYAN, Colors.BLUE, Colors.MAGENTA]
            for _ in range(4):
                # Main flame
                particles.append(Particle(
                    self.x + random.uniform(-15, 15),
                    self.y + 50,
                    random.uniform(-2, 2),
                    random.uniform(2, 5),
                    random.choice([Colors.ORANGE, Colors.YELLOW, Colors.RED]),
                    random.randint(6, 10),
                    25,
                    "nitro"
                ))
                # Energy particles
                particles.append(Particle(
                    self.x + random.uniform(-20, 20),
                    self.y + random.uniform(40, 60),
                    random.uniform(-3, 3),
                    random.uniform(1, 4),
                    random.choice(nitro_colors),
                    random.randint(3, 6),
                    20,
                    "spark"
                ))
        
        # Create rotated car surface
        car_surface = pygame.Surface((self.width * 2, self.height * 2), pygame.SRCALPHA)
        
        # Car shadow
        shadow_rect = pygame.Rect(self.width // 2, self.height // 2 + 5, 
                                  self.width, self.height)
        pygame.draw.rect(car_surface, (0, 0, 0, 100), shadow_rect, border_radius=15)
        
        # Main body
        body_rect = pygame.Rect(self.width // 2, self.height // 2, 
                               self.width, self.height)
        pygame.draw.rect(car_surface, self.stats.color, body_rect, border_radius=15)
        
        # Glass/Cockpit
        glass_rect = pygame.Rect(self.width // 2 + 10, self.height // 2 + 20, 
                                self.width - 20, 30)
        glass_color = (100, 150, 200, 200)
        pygame.draw.rect(car_surface, glass_color, glass_rect, border_radius=8)
        
        # Headlights
        light_color = Colors.CYAN if self.nitro_active else Colors.YELLOW
        pygame.draw.circle(car_surface, light_color, 
                         (self.width // 2 + 15, self.height // 2 + self.height - 10), 6)
        pygame.draw.circle(car_surface, light_color,
                         (self.width // 2 + self.width - 15, self.height // 2 + self.height - 10), 6)
        
        # Spoiler
        spoiler_rect = pygame.Rect(self.width // 2 + 5, self.height // 2, 
                                   self.width - 10, 12)
        pygame.draw.rect(car_surface, Colors.BLACK, spoiler_rect, border_radius=3)
        
        # Racing stripes
        stripe_rect = pygame.Rect(self.width // 2 + self.width // 2 - 3, 
                                 self.height // 2, 6, self.height)
        pygame.draw.rect(car_surface, Colors.WHITE, stripe_rect)
        
        # Wheels
        wheel_positions = [
            (self.width // 2 - 5, self.height // 2 + 20),
            (self.width // 2 + self.width + 5, self.height // 2 + 20),
            (self.width // 2 - 5, self.height // 2 + self.height - 30),
            (self.width // 2 + self.width + 5, self.height // 2 + self.height - 30)
        ]
        for wx, wy in wheel_positions:
            pygame.draw.rect(car_surface, Colors.BLACK, (wx - 6, wy, 12, 25), border_radius=4)
            pygame.draw.rect(car_surface, (80, 80, 80), (wx - 4, wy + 2, 8, 21), border_radius=2)
        
        # Shield effect
        if self.shield_active:
            shield_surface = pygame.Surface((self.width * 3, self.height * 3), pygame.SRCALPHA)
            shield_radius = max(self.width, self.height)
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 10
            pygame.draw.circle(shield_surface, (0, 255, 255, 50), 
                             (self.width * 1.5, self.height * 1.5), 
                             int(shield_radius + pulse))
            pygame.draw.circle(shield_surface, (0, 255, 255, 100),
                             (self.width * 1.5, self.height * 1.5),
                             int(shield_radius + pulse), 3)
            rotated_shield = pygame.transform.rotate(shield_surface, -self.angle + self.drift_angle)
            shield_rect = rotated_shield.get_rect(center=(draw_x, draw_y))
            screen.blit(rotated_shield, shield_rect)
        
        # Rotate and blit car
        rotated_car = pygame.transform.rotate(car_surface, -self.angle + self.drift_angle)
        car_rect = rotated_car.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated_car, car_rect)

class Track:
    def __init__(self, name, length, difficulty):
        self.name = name
        self.length = length
        self.difficulty = difficulty
        self.checkpoints = []
        self.width = 800
        self.segments = []
        self.decorations = []
        self.lights = []
        self.light_grid = {}  # Cache for light calculations
        self.light_update_interval = 5  # Update lighting every N segments
        self.generate_track()
        
    def generate_track(self):
        """Generate procedural track with curves, straights, elevation, and decorations"""
        num_segments = self.length // 100
        last_decoration_side = "left"
        building_cluster = 0
        
        for i in range(num_segments):
            curve = math.sin(i * 0.05) * 200 * self.difficulty
            elevation = math.cos(i * 0.03) * 100
            width = self.width + math.sin(i * 0.1) * 100
            
            segment = {
                'y': i * 100,
                'curve': curve,
                'elevation': elevation,
                'width': width,
                'has_powerup': random.random() < 0.05
            }
            self.segments.append(segment)
            
            # Add checkpoints
            if i % 20 == 0:
                self.checkpoints.append(i * 100)
            
            # Add track decorations
            if i % 3 == 0:  # Space out decorations
                # Alternate sides for variety
                side_multiplier = 1 if last_decoration_side == "left" else -1
                base_x = SCREEN_WIDTH // 2 + (width // 2 + 50) * side_multiplier
                
                # Decide decoration type
                if building_cluster > 0:
                    decoration_type = "building"
                    building_cluster -= 1
                else:
                    if random.random() < 0.3:
                        decoration_type = "building"
                        building_cluster = random.randint(2, 4)
                    else:
                        decoration_type = random.choice(["tree", "tree", "barrier", "billboard"])
                
                # Add decoration
                decoration = TrackDecoration(
                    base_x + curve + random.uniform(-20, 20),
                    i * 100 + random.uniform(-10, 10),
                    decoration_type
                )
                self.decorations.append(decoration)
                
                # Add lights for buildings and billboards
                if decoration_type in ["building", "billboard"]:
                    light_color = (255, 220, 100)  # Warm light
                    light = LightSource(
                        decoration.x,
                        decoration.y,
                        light_color,
                        0.7,
                        300
                    )
                    self.lights.append(light)
                
                last_decoration_side = "right" if last_decoration_side == "left" else "left"
            
            # Add street lights periodically
            if i % 8 == 0:
                for side in [-1, 1]:
                    light = LightSource(
                        SCREEN_WIDTH // 2 + (width // 2 - 20) * side + curve,
                        i * 100,
                        (200, 200, 255),  # Cool white light
                        0.8,
                        250
                    )
                    self.lights.append(light)
    
    def get_lighting_at(self, x: float, y: float, time_of_day: TimeOfDay) -> float:
        """Calculate lighting intensity at a given point"""
        # Cache key for the general area
        grid_x = int(x / 100)
        grid_y = int(y / 100)
        cache_key = (grid_x, grid_y)
        
        if cache_key in self.light_grid:
            return self.light_grid[cache_key]
        
        # Base ambient light depends on time of day
        if time_of_day == TimeOfDay.DAY:
            ambient = 1.0
        elif time_of_day == TimeOfDay.SUNSET:
            ambient = 0.7
        else:  # NIGHT
            ambient = 0.2
        
        # Accumulate light from nearby sources
        light_level = ambient
        for light in self.lights:
            if abs(light.y - y) < light.radius * 1.5:  # Only check nearby lights
                light_level = min(1.0, light_level + light.get_illumination(x, y))
        
        # Cache the result
        self.light_grid[cache_key] = light_level
        return light_level
    
    def update_lights(self):
        """Update light sources and clear cache periodically"""
        for light in self.lights:
            light.update()
        
        # Clear lighting cache periodically
        if random.random() < 0.1:  # 10% chance each update
            self.light_grid.clear()

class AIDriver:
    def __init__(self, car: AdvancedCar, difficulty=0.7, ai_client=None):
        self.car = car
        self.difficulty = difficulty
        self.target_x = 0
        self.target_y = 0
        self.reaction_time = 0
        self.ai_client = ai_client
        self.ai_strategy_cooldown = 0  # Frames until next AI strategy query
        self.current_strategy = None
        
    def update(self, track, player_y, dt):
        # AI-powered strategy (if available)
        if self.ai_client and self.ai_client.is_available() and self.ai_strategy_cooldown <= 0:
            # Build race context
            segment_index = int(abs(self.car.y) / 100) % len(track.segments)
            segment = track.segments[segment_index]
            next_segment_index = (segment_index + 5) % len(track.segments)
            next_segment = track.segments[next_segment_index]
            
            race_context = {
                'position': self._estimate_position(player_y),
                'speed': int(abs(self.car.velocity) * 10),
                'distance_to_leader': abs(self.car.y - player_y),
                'nitro_percent': int((self.car.nitro / self.car.stats.nitro_capacity) * 100),
                'track_condition': 'normal',
                'weather': 'clear',
                'curve_ahead': int(abs(next_segment['curve']) / 4)
            }
            
            self.current_strategy = self.ai_client.generate_ai_opponent_strategy(race_context)
            self.ai_strategy_cooldown = 60  # Query AI every 60 frames (~1 second)
        
        self.ai_strategy_cooldown -= 1
        
        # Apply AI strategy if available
        if self.current_strategy:
            # Use AI-determined target speed
            target_speed_percent = self.current_strategy.get('target_speed_percent', 80) / 100.0
            self.car.velocity = self.car.stats.max_speed * self.difficulty * target_speed_percent
            
            # AI-controlled nitro usage
            if self.current_strategy.get('use_nitro', False) and self.car.nitro > 50:
                self.car.nitro_active = True
                self.car.nitro -= 1
            else:
                self.car.nitro_active = False
        else:
            # Fallback to standard AI
            self.car.velocity = self.car.stats.max_speed * self.difficulty
            
            # Occasional nitro
            if random.random() < 0.01 * self.difficulty and self.car.nitro > 50:
                self.car.nitro_active = True
                self.car.nitro -= 20
            else:
                self.car.nitro_active = False
        
        # Calculate ideal position
        center_x = SCREEN_WIDTH // 2
        segment_index = int(abs(self.car.y) / 100) % len(track.segments)
        segment = track.segments[segment_index]
        
        ideal_x = center_x + segment['curve'] * 0.5
        
        # Apply overtake strategy if available
        if self.current_strategy and self.current_strategy.get('overtake_side') == 'left':
            ideal_x -= 100
        elif self.current_strategy and self.current_strategy.get('overtake_side') == 'right':
            ideal_x += 100
        
        # Smooth steering
        dx = ideal_x - self.car.x
        self.car.angular_velocity = dx * 0.01 * self.difficulty
        
        # Update physics
        rad_angle = math.radians(self.car.angle)
        self.car.x += math.sin(rad_angle) * self.car.velocity
        self.car.y -= math.cos(rad_angle) * self.car.velocity
    
    def _estimate_position(self, player_y):
        """Estimate race position (simplified)"""
        if self.car.y < player_y - 500:
            return 1
        elif self.car.y < player_y - 200:
            return 2
        elif self.car.y < player_y + 200:
            return 3
        elif self.car.y < player_y + 500:
            return 4
        else:
            return 5

class UltimateRacingGame:
    def __init__(self, fullscreen: bool = False):
        # Display setup - Default to windowed mode for development, fullscreen optional
        flags = pygame.HWSURFACE | pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Ultimate Racing Pro - AAA Edition")
        self.clock = pygame.time.Clock()
        
        # Initialize AI client
        self.ai_client = None
        if AI_AVAILABLE:
            self.ai_client = ClaudeAIClient()
            if self.ai_client.is_available():
                print("✓ AI-powered features enabled!")
            else:
                print("⚠ AI client initialized but not configured (missing API key)")
        
        # AI commentary system
        self.commentary_text = ""
        self.commentary_timer = 0
        self.commentary_events = []  # Queue of events to commentate
        
        # Visual effects
        self.motion_blur = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.prev_frame = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Fonts
        self.fonts = {
            'huge': pygame.font.Font(None, 120),
            'large': pygame.font.Font(None, 72),
            'medium': pygame.font.Font(None, 48),
            'small': pygame.font.Font(None, 32),
            'tiny': pygame.font.Font(None, 24)
        }
        
        # Game state
        self.mode = GameMode.MENU
        self.paused = False
        self.weather = Weather.CLEAR
        self.time_of_day = TimeOfDay.DAY
        
        # Car catalog
        self.car_catalog = [
            CarStats("LIGHTNING", 25, 1.2, 8, 1.5, 1200, 100, 0, Colors.RED),
            CarStats("STORM", 28, 1.0, 7, 1.3, 1400, 120, 5000, Colors.BLUE),
            CarStats("PHANTOM", 30, 0.9, 6, 1.2, 1600, 150, 10000, Colors.PURPLE),
            CarStats("INFERNO", 32, 0.8, 5, 1.1, 1800, 180, 20000, Colors.ORANGE),
            CarStats("TITAN", 27, 1.1, 9, 1.6, 1300, 130, 15000, Colors.GREEN),
            CarStats("VIPER", 35, 0.7, 4, 1.0, 2000, 200, 50000, Colors.GOLD),
        ]
        
        # Player
        self.player_car_index = 0
        self.player = AdvancedCar(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200, 
                                 self.car_catalog[0], True)
        self.player_money = 10000
        
        # AI opponents
        self.ai_drivers = []
        for i in range(7):
            car_stats = random.choice(self.car_catalog[:3])
            ai_car = AdvancedCar(
                SCREEN_WIDTH // 2 + random.randint(-200, 200),
                -random.randint(200, 1000),
                car_stats,
                False
            )
            # Pass AI client to drivers for intelligent behavior
            self.ai_drivers.append(AIDriver(ai_car, random.uniform(0.6, 0.9), self.ai_client))
        
        # Track
        self.track = Track("Midnight City Circuit", 5000, 1.0)
        
        # Visual effects
        self.particles = []
        self.powerups = []
        self.generate_powerups()
        
        # Camera
        self.camera_x = 0
        self.camera_y = 0
        self.camera_shake = 0
        
        # UI
        self.menu_selection = 0
        self.menu_options = ["START RACE", "TIME TRIAL", "DRIFT MODE", "GARAGE", "SETTINGS", "EXIT"]
        
        # Performance
        self.show_fps = True
        self.dt = 0
        # Weather intensity (0.0 - 1.0)
        self.weather_intensity = 0.6
        # Snow accumulation [0..1]
        self.snow_accumulation = 0.0
        # Debug flags
        self.debug_mode = False

        # Sound assets (optional)
        self.sounds = {}
        sounds_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
        def load_sound(name):
            path = os.path.join(sounds_dir, name)
            if os.path.exists(path):
                try:
                    return pygame.mixer.Sound(path)
                except Exception:
                    return None
            return None

        # Try to load common sounds; fallback to synthesized beep if numpy is available
        self.sounds['rain_splash'] = load_sound('rain_splash.wav')
        self.sounds['collision'] = load_sound('collision.wav')
        self.sounds['pickup'] = load_sound('pickup.wav')
        self.sounds['repair'] = load_sound('repair.wav')
        # synthesize short sounds if not present and numpy available
        if np is not None:
            def synth(freq=600, dur_ms=80, volume=0.2):
                sr = 22050
                t = np.linspace(0, dur_ms/1000.0, int(sr * (dur_ms/1000.0)), False)
                wave = (np.sin(2 * np.pi * freq * t) * 32767 * volume).astype(np.int16)
                try:
                    return pygame.sndarray.make_sound(wave)
                except Exception:
                    return None
            if self.sounds['rain_splash'] is None:
                self.sounds['rain_splash'] = synth(1200, 40, 0.1)
            if self.sounds['collision'] is None:
                self.sounds['collision'] = synth(250, 120, 0.4)
            if self.sounds['pickup'] is None:
                self.sounds['pickup'] = synth(1200, 60, 0.2)
        
    def generate_powerups(self):
        """Generate powerups along the track"""
        self.powerups = []
        for segment in self.track.segments:
            if segment['has_powerup']:
                powerup_type = random.choice(['speed', 'shield', 'nitro', 'coins'])
                x = SCREEN_WIDTH // 2 + segment['curve'] + random.randint(-200, 200)
                y = segment['y']
                self.powerups.append(PowerUp(x, y, powerup_type))
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.mode == GameMode.MENU:
                        return False
                    else:
                        self.mode = GameMode.MENU
                        
                if self.mode == GameMode.MENU:
                    if event.key == pygame.K_UP:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.handle_menu_selection()
                        
                if self.mode == GameMode.GARAGE:
                    if event.key == pygame.K_LEFT:
                        self.player_car_index = (self.player_car_index - 1) % len(self.car_catalog)
                    elif event.key == pygame.K_RIGHT:
                        self.player_car_index = (self.player_car_index + 1) % len(self.car_catalog)
                    elif event.key == pygame.K_RETURN:
                        if self.player_money >= self.car_catalog[self.player_car_index].price:
                            self.player_money -= self.car_catalog[self.player_car_index].price
                            self.player.stats = self.car_catalog[self.player_car_index]
                            
                if event.key == pygame.K_F1:
                    self.show_fps = not self.show_fps
                if event.key == pygame.K_F2:
                    w_list = list(Weather)
                    self.weather = w_list[(w_list.index(self.weather) + 1) % len(w_list)]
                if event.key == pygame.K_F3:
                    t_list = list(TimeOfDay)
                    self.time_of_day = t_list[(t_list.index(self.time_of_day) + 1) % len(t_list)]
        
        return True
    
    def handle_menu_selection(self):
        option = self.menu_options[self.menu_selection]
        if option == "START RACE":
            self.mode = GameMode.RACE
            self.reset_race()
        elif option == "TIME TRIAL":
            self.mode = GameMode.TIME_TRIAL
            self.reset_race()
        elif option == "DRIFT MODE":
            self.mode = GameMode.DRIFT
            self.reset_race()
        elif option == "GARAGE":
            self.mode = GameMode.GARAGE
        elif option == "EXIT":
            pygame.quit()
            sys.exit()
    
    def reset_race(self):
        """Reset race state"""
        self.player = AdvancedCar(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200,
                                 self.car_catalog[self.player_car_index], True)
        self.particles = []
        self.generate_powerups()
        self.camera_x = 0
        self.camera_y = 0
        
    def update(self):
        if self.mode in [GameMode.RACE, GameMode.TIME_TRIAL, GameMode.DRIFT]:
            keys = pygame.key.get_pressed()
            
            # Update player
            self.player.update_physics(self.dt, keys)
            
            # Update AI
            for ai_driver in self.ai_drivers:
                ai_driver.update(self.track, self.player.y, self.dt)
            
            # Update camera
            self.camera_x = self.player.x - SCREEN_WIDTH // 2
            self.camera_y = self.player.y - SCREEN_HEIGHT + 400
            
            # Camera shake from speed
            if abs(self.player.velocity) > 20:
                self.camera_shake = random.uniform(-2, 2)
            else:
                self.camera_shake *= 0.9
            
            # Update powerups
            for powerup in self.powerups:
                powerup.update()
                if not powerup.collected:
                    dist = math.hypot(self.player.x - powerup.x, self.player.y - powerup.y)
                    if dist < 50:
                        powerup.collected = True
                        self.player.apply_powerup(powerup.type)
                        # trigger visual/sound effect
                        try:
                            powerup.on_collect(self.player, self)
                        except Exception:
                            pass
                        
                        # Generate AI commentary for powerup collection
                        self._generate_commentary('powerup', {
                            'type': powerup.type,
                            'speed': int(abs(self.player.velocity) * 10)
                        })
            
            # Update particles
            self.particles = [p for p in self.particles if p.lifetime > 0]
            for particle in self.particles:
                particle.update()

            # Weather effects: spawn raindrops or snow particles
            if self.weather == Weather.RAIN:
                for _ in range(8):
                    rx = random.randint(0, SCREEN_WIDTH)
                    ry = random.randint(-50, SCREEN_HEIGHT)
                    self.particles.append(Particle(rx, ry, random.uniform(-1, 1), random.uniform(8, 14), (150,150,255), 2, 30, 'raindrop'))
            elif self.weather == Weather.SNOW:
                # increase accumulation
                self.snow_accumulation = min(1.0, getattr(self, 'snow_accumulation', 0.0) + 0.0005)
                for _ in range(3):
                    rx = random.randint(0, SCREEN_WIDTH)
                    ry = random.randint(-50, SCREEN_HEIGHT)
                    self.particles.append(Particle(rx, ry, random.uniform(-0.5, 0.5), random.uniform(1, 3), Colors.WHITE, random.randint(2,4), 80, 'smoke'))
            else:
                # decay accumulation
                if hasattr(self, 'snow_accumulation'):
                    self.snow_accumulation = max(0.0, self.snow_accumulation - 0.0002)
            
            # Boundaries
            self.player.x = max(100, min(self.player.x, SCREEN_WIDTH - 100))

            # Collision with barriers -> damage
            for deco in self.track.decorations:
                if deco.type == 'barrier':
                    dist = math.hypot(self.player.x - deco.x, self.player.y - deco.y)
                    if dist < 60 and abs(self.player.velocity) > 8:
                        dmg = min(30, int(abs(self.player.velocity) * 0.5))
                        self.player.take_damage(dmg)
                        # spawn sparks
                        for _ in range(10):
                            self.particles.append(Particle(self.player.x + random.uniform(-10,10),
                                                           self.player.y + random.uniform(-10,10),
                                                           random.uniform(-4,4), random.uniform(-3,3), Colors.ORANGE, random.randint(2,5), 20, 'spark'))
                        
                        # Generate AI commentary for crash
                        self._generate_commentary('crash', {
                            'damage': dmg,
                            'health_remaining': self.player.health
                        })
    
    def draw_environment(self):
        """Draw sky, weather, and background with parallax scrolling"""
        # Sky gradient based on time of day
        if self.time_of_day == TimeOfDay.DAY:
            top_color = Colors.SKY_DAY
            bottom_color = (180, 220, 255)
            sun_color = (255, 240, 200)
        elif self.time_of_day == TimeOfDay.SUNSET:
            top_color = Colors.SKY_SUNSET
            bottom_color = (255, 160, 122)
            sun_color = (255, 150, 50)
        else:
            top_color = Colors.SKY_NIGHT
            bottom_color = (50, 50, 100)
            sun_color = (200, 200, 255)  # Moon
        
        # Draw gradient sky
        for y in range(SCREEN_HEIGHT // 2):
            ratio = y / (SCREEN_HEIGHT // 2)
            color = tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * ratio) for i in range(3))
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
            
        # Draw sun/moon with glow
        sun_x = SCREEN_WIDTH * 0.8
        sun_y = SCREEN_HEIGHT * 0.2
        sun_radius = 40
        
        # Glow effect
        for r in range(3):
            glow_radius = sun_radius * (3 - r)
            glow_alpha = 100 - (r * 30)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*sun_color, glow_alpha), 
                             (glow_radius, glow_radius), glow_radius)
            self.screen.blit(glow_surface, 
                           (sun_x - glow_radius, sun_y - glow_radius))
        
        # Main sun/moon
        pygame.draw.circle(self.screen, sun_color, (int(sun_x), int(sun_y)), sun_radius)
        
        # Parallax mountains (3 layers)
        mountain_colors = [(100, 100, 120), (80, 80, 100), (60, 60, 80)]
        for layer, color in enumerate(mountain_colors):
            parallax = (layer + 1) * 0.2
            offset = int(self.camera_x * parallax) % SCREEN_WIDTH
            
            points = [(0, SCREEN_HEIGHT//2)]
            for x in range(0, SCREEN_WIDTH + 100, 100):
                # Use noise to generate mountain heights
                height = math.sin(x * 0.02 + layer * 10) * 50 + \
                        math.sin(x * 0.01 + layer * 5) * 30 + \
                        random.randint(-10, 10)
                points.append((x, SCREEN_HEIGHT//2 - 100 - height * (3-layer)))
            points.append((SCREEN_WIDTH, SCREEN_HEIGHT//2))
            
            # Draw mountains twice for seamless scrolling
            for x_offset in [-offset, SCREEN_WIDTH-offset]:
                mountain_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                shifted_points = [(x + x_offset, y) for x, y in points]
                pygame.draw.polygon(mountain_surface, (*color, 200), shifted_points)
                self.screen.blit(mountain_surface, (0, 0))
        
        # Stars at night
        if self.time_of_day == TimeOfDay.NIGHT:
            random.seed(42)
            for _ in range(200):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT // 2)
                brightness = random.randint(100, 255)
                size = random.randint(1, 3)
                pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), size)
        
        # Weather effects
        if self.weather == Weather.RAIN:
            for _ in range(100):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.line(self.screen, Colors.RAIN[:3], (x, y), (x - 5, y + 20), 2)
        elif self.weather == Weather.SNOW:
            for _ in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.screen, Colors.WHITE, (x, y), random.randint(2, 5))
    
    def draw_track(self):
        """Draw racing track with 3D perspective, decorations, and lighting"""
        # Update track lights
        self.track.update_lights()
        
        # Draw ground
        ground_color = Colors.GRASS
        if self.time_of_day == TimeOfDay.NIGHT:
            ground_color = (20, 40, 20)  # Darker grass at night
        pygame.draw.rect(self.screen, ground_color, 
                        (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        
        # Sort decorations and track segments for proper depth rendering
        render_objects = []
        
        # Add track segments
        for i, segment in enumerate(self.track.segments):
            screen_y = segment['y'] - self.camera_y
            if -200 < screen_y < SCREEN_HEIGHT + 200:
                render_objects.append(('segment', segment, i, screen_y))
        
        # Add decorations
        for decoration in self.track.decorations:
            screen_y = decoration.y - self.camera_y
            if -200 < screen_y < SCREEN_HEIGHT + 200:
                render_objects.append(('decoration', decoration, None, screen_y))
        
        # Sort by Y position for proper overlap
        render_objects.sort(key=lambda x: x[3])
        
        # Draw all objects in order
        for obj_type, obj, index, screen_y in render_objects:
            if obj_type == 'segment':
                segment = obj
                # Perspective calculation
                z = max(0.1, (screen_y / SCREEN_HEIGHT))
                width = int(segment['width'] / z)
                
                # Road position
                road_x = SCREEN_WIDTH // 2 - width // 2 + int(segment['curve'])
                
                # Get lighting for this segment
                light_level = self.track.get_lighting_at(
                    SCREEN_WIDTH // 2 + segment['curve'],
                    segment['y'],
                    self.time_of_day
                )
                
                # Adjust road color based on lighting
                road_color = Colors.ROAD if index % 2 == 0 else (60, 60, 60)
                if self.time_of_day == TimeOfDay.NIGHT:
                    road_color = tuple(int(c * light_level) for c in road_color)
                
                # Draw road
                pygame.draw.rect(self.screen, road_color,
                               (road_x, int(screen_y), width, int(100 / z)))
                
                # Road markings
                if index % 5 == 0:
                    line_x = SCREEN_WIDTH // 2 + int(segment['curve'])
                    line_color = tuple(int(c * light_level) for c in Colors.YELLOW)
                    pygame.draw.rect(self.screen, line_color,
                                   (line_x - 3, int(screen_y), 6, int(80 / z)))
                
                # Side lines
                line_color = tuple(int(c * light_level) for c in Colors.WHITE)
                pygame.draw.rect(self.screen, line_color,
                               (road_x - 5, int(screen_y), 5, int(100 / z)))
                pygame.draw.rect(self.screen, line_color,
                               (road_x + width, int(screen_y), 5, int(100 / z)))
                
            else:  # decoration
                decoration = obj
                # Perspective calculations
                z = max(0.1, (screen_y / SCREEN_HEIGHT))
                scaled_height = int(decoration.height / z)
                scaled_width = int(decoration.width / z)
                
                # Position with perspective
                draw_x = int(decoration.x - self.camera_x - scaled_width/2)
                draw_y = int(screen_y - scaled_height)
                
                # Get lighting for decoration
                light_level = self.track.get_lighting_at(
                    decoration.x, decoration.y, self.time_of_day
                )
                
                if decoration.type == "building":
                    # Main building
                    color = tuple(int(c * light_level) for c in decoration.color)
                    pygame.draw.rect(self.screen, color,
                                   (draw_x, draw_y, scaled_width, scaled_height))
                    
                    # Windows
                    window_width = max(4, scaled_width // 8)
                    window_height = max(4, scaled_height // 12)
                    
                    for window in decoration.details["windows"]:
                        wx = draw_x + int(window["x"] / z)
                        wy = draw_y + int(window["y"] / z)
                        if window["lit"]:
                            # Glowing window
                            glow_surface = pygame.Surface(
                                (window_width * 3, window_height * 3),
                                pygame.SRCALPHA
                            )
                            pygame.draw.rect(glow_surface,
                                           (255, 255, 200, 50),
                                           (window_width, window_height,
                                            window_width, window_height))
                            self.screen.blit(glow_surface,
                                           (wx - window_width, wy - window_height))
                        pygame.draw.rect(self.screen,
                                       (255, 255, 200) if window["lit"] else (40, 40, 40),
                                       (wx, wy, window_width, window_height))
                
                elif decoration.type == "tree":
                    # Tree trunk
                    trunk_color = (83, 53, 10)
                    trunk_width = max(4, scaled_width // 3)
                    pygame.draw.rect(self.screen,
                                   tuple(int(c * light_level) for c in trunk_color),
                                   (draw_x + scaled_width//3, draw_y + scaled_height//2,
                                    trunk_width, scaled_height//2))
                    
                    # Tree foliage (triangular)
                    color = tuple(int(c * light_level) for c in decoration.color)
                    points = [
                        (draw_x + scaled_width//2, draw_y),
                        (draw_x, draw_y + scaled_height//2),
                        (draw_x + scaled_width, draw_y + scaled_height//2)
                    ]
                    pygame.draw.polygon(self.screen, color, points)
                
                elif decoration.type == "barrier":
                    # Draw barrier with reflective strips
                    color = tuple(int(c * light_level) for c in decoration.color)
                    pygame.draw.rect(self.screen, color,
                                   (draw_x, draw_y + scaled_height//2,
                                    scaled_width, scaled_height//4))
                    
                    # Reflective strips
                    strip_color = (255, 0, 0) if light_level < 0.5 else (200, 200, 200)
                    for i in range(0, scaled_width, max(10, scaled_width//5)):
                        pygame.draw.rect(self.screen, strip_color,
                                       (draw_x + i, draw_y + scaled_height//2,
                                        5, scaled_height//4))
                
                elif decoration.type == "billboard":
                    # Billboard background
                    color = tuple(int(c * light_level) for c in decoration.color)
                    pygame.draw.rect(self.screen, color,
                                   (draw_x, draw_y, scaled_width, scaled_height))
                    
                    # Billboard text
                    if scaled_width > 30:  # Only if billboard is big enough
                        font_size = max(14, min(32, scaled_width // 5))
                        font = pygame.font.Font(None, font_size)
                        text = font.render(decoration.details["text"], True, Colors.WHITE)
                        text_rect = text.get_rect(center=(draw_x + scaled_width//2,
                                                        draw_y + scaled_height//2))
                        self.screen.blit(text, text_rect)
                        
                        # Add glow effect at night
                        if self.time_of_day == TimeOfDay.NIGHT:
                            glow_surface = pygame.Surface((scaled_width, scaled_height),
                                                        pygame.SRCALPHA)
                            pygame.draw.rect(glow_surface, (*color[:3], 30),
                                           (0, 0, scaled_width, scaled_height))
    
    def draw_hud(self):
        """Draw comprehensive HUD"""
        # Speed
        speed_kmh = int(abs(self.player.velocity) * 10)
        speed_text = self.fonts['huge'].render(str(speed_kmh), True, Colors.WHITE)
        speed_label = self.fonts['small'].render("km/h", True, Colors.WHITE)
        self.screen.blit(speed_text, (50, SCREEN_HEIGHT - 200))
        self.screen.blit(speed_label, (50, SCREEN_HEIGHT - 120))
        
        # Speedometer arc
        center = (200, SCREEN_HEIGHT - 120)
        max_angle = 270
        current_angle = (speed_kmh / (self.player.stats.max_speed * 10)) * max_angle
        pygame.draw.arc(self.screen, Colors.RED, (center[0] - 80, center[1] - 80, 160, 160),
                       math.radians(135), math.radians(135 + max_angle), 8)
        pygame.draw.arc(self.screen, Colors.GREEN, (center[0] - 80, center[1] - 80, 160, 160),
                       math.radians(135), math.radians(135 + current_angle), 8)
        
        # Nitro bar
        nitro_percent = self.player.nitro / self.player.stats.nitro_capacity
        bar_width = 300
        bar_height = 40
        bar_x = SCREEN_WIDTH - bar_width - 50
        bar_y = SCREEN_HEIGHT - 100
        
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        nitro_color = Colors.CYAN if nitro_percent > 0.3 else Colors.RED
        pygame.draw.rect(self.screen, nitro_color, 
                        (bar_x + 5, bar_y + 5, int((bar_width - 10) * nitro_percent), bar_height - 10),
                        border_radius=8)
        
        nitro_text = self.fonts['medium'].render("NITRO", True, Colors.WHITE)
        self.screen.blit(nitro_text, (bar_x + 10, bar_y + 5))
        
        # Position and lap
        position_text = self.fonts['medium'].render(f"Position: 1/{len(self.ai_drivers) + 1}", True, Colors.GOLD)
        self.screen.blit(position_text, (50, 50))
        
        lap_text = self.fonts['medium'].render(f"Lap: {self.player.lap}/3", True, Colors.WHITE)
        self.screen.blit(lap_text, (50, 100))
        
        # Drift score
        if abs(self.player.drift_score) > 50:
            drift_text = self.fonts['large'].render(f"DRIFT! x{self.player.combo_multiplier}", True, Colors.ORANGE)
            text_rect = drift_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
            self.screen.blit(drift_text, text_rect)
        
        # AI Commentary display
        if self.commentary_timer > 0:
            self.commentary_timer -= 1
            # Display commentary at top center with fade effect
            alpha = min(255, self.commentary_timer * 3)
            commentary_surface = pygame.Surface((SCREEN_WIDTH - 100, 100), pygame.SRCALPHA)
            commentary_bg = pygame.Surface((SCREEN_WIDTH - 100, 100), pygame.SRCALPHA)
            pygame.draw.rect(commentary_bg, (0, 0, 0, min(180, alpha)), (0, 0, SCREEN_WIDTH - 100, 100), border_radius=10)
            commentary_surface.blit(commentary_bg, (0, 0))
            
            # Render commentary text
            font = self.fonts['medium']
            words = self.commentary_text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if font.size(test_line)[0] < SCREEN_WIDTH - 140:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            y_offset = 20
            for line in lines:
                text = font.render(line, True, (*Colors.CYAN, min(255, alpha)))
                text_rect = text.get_rect(center=((SCREEN_WIDTH - 100) // 2, y_offset))
                commentary_surface.blit(text, text_rect)
                y_offset += 35
            
            self.screen.blit(commentary_surface, (50, 150))
        
        # Coins
        coins_text = self.fonts['medium'].render(f"${self.player.coins}", True, Colors.GOLD)
        self.screen.blit(coins_text, (SCREEN_WIDTH - 200, 50))

        # Health bar
        health_x = 50
        health_y = SCREEN_HEIGHT - 160
        health_w = 300
        health_h = 30
        pygame.draw.rect(self.screen, (30,30,30), (health_x, health_y, health_w, health_h), border_radius=6)
        health_percent = max(0.0, self.player.health / 100.0)
        health_color = (int(255 * (1-health_percent)), int(255 * health_percent), 50)
        pygame.draw.rect(self.screen, health_color, (health_x+4, health_y+4, int((health_w-8)*health_percent), health_h-8), border_radius=6)
        health_text = self.fonts['small'].render(f"Health: {int(self.player.health)}%", True, Colors.WHITE)
        self.screen.blit(health_text, (health_x + 10, health_y + 2))
        
        # Mini map
        map_size = 200
        map_x = SCREEN_WIDTH - map_size - 50
        map_y = 150
        pygame.draw.rect(self.screen, (20, 20, 20, 200),
                        (map_x, map_y, map_size, map_size), border_radius=10)
        
        # Player on map
        pygame.draw.circle(self.screen, Colors.RED, (map_x + map_size // 2, map_y + map_size // 2), 8)
        
        # AI on map
        for ai_driver in self.ai_drivers:
            y_diff = (ai_driver.car.y - self.player.y) * 0.05
            if -map_size // 2 < y_diff < map_size // 2:
                map_pos = (map_x + map_size // 2, map_y + map_size // 2 + int(y_diff))
                pygame.draw.circle(self.screen, ai_driver.car.stats.color, map_pos, 5)
        
        # FPS counter
        if self.show_fps:
            fps_text = self.fonts['tiny'].render(f"FPS: {int(self.clock.get_fps())}", True, Colors.GREEN)
            self.screen.blit(fps_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))
        
        # Weather and time indicator
        info_text = self.fonts['tiny'].render(
            f"Weather: {self.weather.value.upper()} | Time: {self.time_of_day.value.upper()}", 
            True, Colors.WHITE
        )
        self.screen.blit(info_text, (50, SCREEN_HEIGHT - 40))
    
    def draw_menu(self):
        """Draw main menu"""
        # Background
        self.screen.fill(Colors.BLACK)
        
        # Title with glow effect
        title = "ULTIMATE RACING PRO"
        for offset in range(5, 0, -1):
            glow_color = tuple(int(c * (offset / 5)) for c in Colors.CYAN)
            glow_text = self.fonts['huge'].render(title, True, glow_color)
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH // 2 + offset, 150 + offset))
            self.screen.blit(glow_text, glow_rect)
        
        title_text = self.fonts['huge'].render(title, True, Colors.GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle = self.fonts['medium'].render("AAA EDITION - THE ULTIMATE RACING EXPERIENCE", True, Colors.WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        y_start = 400
        for i, option in enumerate(self.menu_options):
            color = Colors.CYAN if i == self.menu_selection else Colors.WHITE
            option_text = self.fonts['large'].render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 80))
            
            if i == self.menu_selection:
                # Selection highlight
                pygame.draw.rect(self.screen, Colors.CYAN,
                               (option_rect.left - 20, option_rect.top - 10,
                                option_rect.width + 40, option_rect.height + 20),
                               3, border_radius=10)
            
            self.screen.blit(option_text, option_rect)
        
        # Controls hint
        controls = [
            "CONTROLS: Arrow Keys/WASD - Drive | SPACE/SHIFT - Nitro",
            "F1 - Toggle FPS | F2 - Change Weather | F3 - Change Time"
        ]
        for i, control in enumerate(controls):
            control_text = self.fonts['tiny'].render(control, True, Colors.GRAY)
            control_rect = control_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 30))
            self.screen.blit(control_text, control_rect)
    
    def draw_garage(self):
        """Draw car selection garage"""
        self.screen.fill((30, 30, 30))
        
        # Title
        title = self.fonts['large'].render("GARAGE - SELECT YOUR CAR", True, Colors.GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Current car display
        current_car = self.car_catalog[self.player_car_index]
        
        # Car preview (enlarged visualization)
        preview_x = SCREEN_WIDTH // 2
        preview_y = SCREEN_HEIGHT // 2 - 100
        
        # Car body
        car_width = 200
        car_height = 300
        pygame.draw.rect(self.screen, current_car.color,
                        (preview_x - car_width // 2, preview_y - car_height // 2,
                         car_width, car_height), border_radius=30)
        pygame.draw.rect(self.screen, Colors.WHITE,
                        (preview_x - car_width // 2, preview_y - car_height // 2,
                         car_width, car_height), 5, border_radius=30)
        
        # Car name
        name_text = self.fonts['huge'].render(current_car.name, True, Colors.CYAN)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, preview_y + 200))
        self.screen.blit(name_text, name_rect)
        
        # Stats bars
        stats_x = SCREEN_WIDTH // 2 - 300
        stats_y = SCREEN_HEIGHT - 400
        stat_names = ["Speed", "Acceleration", "Handling", "Nitro"]
        stat_values = [
            current_car.max_speed / 35,
            current_car.acceleration / 1.5,
            current_car.handling / 10,
            current_car.nitro_capacity / 200
        ]
        
        for i, (name, value) in enumerate(zip(stat_names, stat_values)):
            y = stats_y + i * 60
            
            # Stat name
            stat_text = self.fonts['medium'].render(name, True, Colors.WHITE)
            self.screen.blit(stat_text, (stats_x, y))
            
            # Stat bar
            bar_x = stats_x + 250
            bar_width = 400
            pygame.draw.rect(self.screen, Colors.DARK_GRAY,
                           (bar_x, y, bar_width, 30), border_radius=5)
            pygame.draw.rect(self.screen, Colors.GREEN,
                           (bar_x, y, int(bar_width * value), 30), border_radius=5)
        
        # Price
        price_color = Colors.GREEN if self.player_money >= current_car.price else Colors.RED
        price_text = self.fonts['large'].render(
            f"Price: ${current_car.price}" if current_car.price > 0 else "OWNED",
            True, price_color
        )
        price_rect = price_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
        self.screen.blit(price_text, price_rect)
        
        # Player money
        money_text = self.fonts['medium'].render(f"Your Money: ${self.player_money}", True, Colors.GOLD)
        money_rect = money_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.screen.blit(money_text, money_rect)
        
        # Navigation hints
        nav_text = self.fonts['small'].render("← → Navigate | ENTER Purchase | ESC Back", True, Colors.WHITE)
        nav_rect = nav_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(nav_text, nav_rect)
    
    def _generate_commentary(self, event_type: str, context: dict):
        """Generate AI-powered commentary for racing events"""
        if not self.ai_client or not self.ai_client.is_available():
            return
        
        # Only generate new commentary if timer expired
        if self.commentary_timer <= 0:
            try:
                self.commentary_text = self.ai_client.generate_dynamic_track_commentary(event_type, context)
                self.commentary_timer = 180  # Display for ~3 seconds
            except Exception as e:
                # Silent fallback
                pass
    
    def apply_motion_blur(self):
        """Apply motion blur based on speed"""
        if self.mode in [GameMode.RACE, GameMode.TIME_TRIAL, GameMode.DRIFT]:
            # Scale blur amount with speed
            blur_amount = min(0.8, abs(self.player.velocity) / self.player.stats.max_speed)
            if blur_amount > 0.1:
                # Store current frame
                self.prev_frame = self.screen.copy()
                
                # Apply motion blur
                self.motion_blur.fill((0, 0, 0, int(255 * (1 - blur_amount))))
                self.screen.blit(self.motion_blur, (0, 0))
                
                # Add speed lines at high speeds
                if blur_amount > 0.5:
                    angle = math.degrees(math.atan2(self.player.velocity, 5))
                    for _ in range(int(blur_amount * 20)):
                        start_x = random.randint(0, SCREEN_WIDTH)
                        start_y = random.randint(0, SCREEN_HEIGHT)
                        length = random.randint(20, 100) * blur_amount
                        end_x = start_x + math.cos(math.radians(angle)) * length
                        end_y = start_y + math.sin(math.radians(angle)) * length
                        pygame.draw.line(self.screen, (255, 255, 255, 50),
                                       (start_x, start_y), (end_x, end_y), 1)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Get delta time
            dt = self.clock.tick(FPS) / 1000.0
            self.dt = max(0.001, min(dt, 0.1))  # Clamp dt
            
            running = self.handle_input()
            
            if self.mode in [GameMode.RACE, GameMode.TIME_TRIAL, GameMode.DRIFT]:
                self.update()
                self.draw_environment()
                self.draw_track()
                
                # Draw powerups
                for powerup in self.powerups:
                    powerup.draw(self.screen, self.camera_y)
                
                # Draw AI cars
                for ai_driver in self.ai_drivers:
                    ai_driver.car.draw(self.screen, self.camera_x, self.camera_y, self.particles)
                
                # Draw player
                self.player.draw(self.screen, self.camera_x, self.camera_y, self.particles)
                
                # Draw particles
                for particle in self.particles:
                    particle.draw(self.screen)
                
                self.draw_hud()
                
                # Apply motion blur and speed effects
                self.apply_motion_blur()
                
            elif self.mode == GameMode.MENU:
                self.draw_menu()
                
            elif self.mode == GameMode.GARAGE:
                self.draw_garage()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

def run_smoke_test():
    """Quick smoke test to verify basic game functionality"""
    print("Running smoke test...")
    
    # Initialize game
    game = UltimateRacingGame(fullscreen=False)
    
    # Test basic game state
    assert game.mode == GameMode.MENU, "Game should start in menu mode"
    assert len(game.car_catalog) == 6, "Should have 6 cars in catalog"
    assert game.player is not None, "Player should be initialized"
    
    # Test one update cycle
    game.dt = 1/60  # Simulate 60 FPS
    game.update()
    
    # Create a mock key dictionary (all keys default to False)
    keys = {}
    for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d,
                pygame.K_SPACE, pygame.K_LSHIFT]:
        keys[key] = False
    
    # Test player movement
    initial_y = game.player.y
    keys[pygame.K_UP] = True  # Press UP key
    game.player.update_physics(1/60, keys)
    assert game.player.y != initial_y, "Player should move when UP is pressed"
    
    print("Smoke test passed!")
    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ultimate Racing Pro - run options")
    parser.add_argument("--fullscreen", action="store_true", help="Run the game in fullscreen mode")
    parser.add_argument("--test", action="store_true", help="Run smoke test instead of the game")
    args = parser.parse_args()

    if args.test:
        run_smoke_test()
    else:
        game = UltimateRacingGame(fullscreen=args.fullscreen)
        game.run()

