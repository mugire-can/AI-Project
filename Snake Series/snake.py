"""
ULTIMATE SNAKE PRO - Advanced Snake Game
Features: Multiple game modes, power-ups, obstacles, levels, animations,
particle effects, high score system, and smooth graphics!
"""

import pygame
import random
import sys
import math
import json
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()
pygame.mixer.init()

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class GameMode(Enum):
    MENU = "menu"
    CLASSIC = "classic"
    SURVIVAL = "survival"
    TIMED = "timed"
    SETTINGS = "settings"
    LEADERBOARD = "leaderboard"

class PowerUpType(Enum):
    SPEED_BOOST = "speed_boost"
    SLOW_DOWN = "slow_down"
    DOUBLE_POINTS = "double_points"
    INVINCIBLE = "invincible"
    SHRINK = "shrink"

# Colors
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (213, 50, 80)
    GREEN = (0, 255, 0)
    BLUE = (50, 153, 213)
    DARK_GREEN = (0, 180, 0)
    LIGHT_GREEN = (144, 238, 144)
    YELLOW = (255, 215, 0)
    ORANGE = (255, 140, 0)
    PURPLE = (138, 43, 226)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GOLD = (255, 215, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (50, 50, 50)
    GRADIENT_BLUE = (30, 144, 255)
    NEON_GREEN = (57, 255, 20)

# Display settings
WIDTH = 800
HEIGHT = 600
BLOCK_SIZE = 20
BASE_SPEED = 12
SPEED = BASE_SPEED

# Setup display
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ultimate Snake Pro')
clock = pygame.time.Clock()

font_small = pygame.font.SysFont("bahnschrift", 20)
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)
title_font = pygame.font.SysFont("bahnschrift", 60)

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    lifetime: int
    size: int

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.twinkle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.02, 0.05)
        
    def update(self):
        self.twinkle += self.speed
        
    def draw(self, display):
        alpha = int((math.sin(self.twinkle) + 1) / 2 * 255)
        brightness = int((math.sin(self.twinkle) + 1) / 2 * 100 + 155)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(display, color, (int(self.x), int(self.y)), self.size)

class Trail:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lifetime = 15
        self.initial_lifetime = 15
        
    def update(self):
        self.lifetime -= 1
        
    def draw(self, display):
        alpha = int((self.lifetime / self.initial_lifetime) * 100)
        color = (0, alpha + 100, 0)
        size = int((self.lifetime / self.initial_lifetime) * BLOCK_SIZE * 0.8)
        if size > 0:
            pygame.draw.circle(display, color, (self.x + BLOCK_SIZE // 2, self.y + BLOCK_SIZE // 2), size)

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.active = True
        self.pulse = 0
        self.rotation = 0
        self.sparkles = []
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            self.sparkles.append({'angle': angle, 'distance': 0, 'speed': random.uniform(0.5, 1.5)})
        
    def draw(self, display):
        self.pulse += 0.15
        self.rotation += 8
        pulse_size = 4 + math.sin(self.pulse) * 3
        
        color_map = {
            PowerUpType.SPEED_BOOST: Colors.CYAN,
            PowerUpType.SLOW_DOWN: Colors.PURPLE,
            PowerUpType.DOUBLE_POINTS: Colors.GOLD,
            PowerUpType.INVINCIBLE: Colors.ORANGE,
            PowerUpType.SHRINK: Colors.MAGENTA
        }
        color = color_map.get(self.type, Colors.WHITE)
        
        center_x = self.x + BLOCK_SIZE // 2
        center_y = self.y + BLOCK_SIZE // 2
        
        # Outer glow
        for i in range(3):
            glow_radius = int(BLOCK_SIZE // 2 + pulse_size + i * 4)
            glow_alpha = 100 - i * 30
            glow_color = tuple(max(0, min(255, c - i * 30)) for c in color)
            pygame.draw.circle(display, glow_color, (center_x, center_y), glow_radius, 2)
        
        # Main circle
        pygame.draw.circle(display, color, (center_x, center_y), 
                          int(BLOCK_SIZE // 2 + pulse_size))
        
        # Inner shine
        shine_offset = 3
        pygame.draw.circle(display, Colors.WHITE, (center_x - shine_offset, center_y - shine_offset), 
                          int(BLOCK_SIZE // 4))
        
        # Rotating sparkles
        for sparkle in self.sparkles:
            sparkle['angle'] += 0.05
            sparkle['distance'] = 15 + math.sin(self.pulse + sparkle['angle']) * 5
            sparkle_x = center_x + math.cos(sparkle['angle']) * sparkle['distance']
            sparkle_y = center_y + math.sin(sparkle['angle']) * sparkle['distance']
            pygame.draw.circle(display, Colors.WHITE, (int(sparkle_x), int(sparkle_y)), 2)
        
        # Symbol based on type
        if self.type == PowerUpType.SPEED_BOOST:
            # Lightning bolt
            points = [(center_x, center_y - 6), (center_x + 3, center_y), 
                     (center_x - 3, center_y), (center_x, center_y + 6)]
            pygame.draw.polygon(display, Colors.YELLOW, points)
        elif self.type == PowerUpType.INVINCIBLE:
            # Shield
            pygame.draw.circle(display, Colors.YELLOW, (center_x, center_y), 6, 2)

class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.pulse = random.uniform(0, 2 * math.pi)
        
    def draw(self, display):
        self.pulse += 0.05
        brightness = int((math.sin(self.pulse) + 1) / 2 * 30 + 80)
        
        # Draw 3D-like obstacle
        # Top face (lighter)
        top_color = (brightness + 40, brightness + 40, brightness + 40)
        pygame.draw.polygon(display, top_color, [
            (self.x, self.y),
            (self.x + BLOCK_SIZE, self.y),
            (self.x + BLOCK_SIZE - 4, self.y + 4),
            (self.x + 4, self.y + 4)
        ])
        
        # Front face
        front_color = (brightness, brightness, brightness)
        pygame.draw.rect(display, front_color, [self.x, self.y, BLOCK_SIZE, BLOCK_SIZE])
        
        # Dark outline
        pygame.draw.rect(display, Colors.BLACK, [self.x, self.y, BLOCK_SIZE, BLOCK_SIZE], 2)
        
        # Danger stripes
        stripe_color = (brightness + 60, brightness, 0)
        for i in range(0, BLOCK_SIZE, 6):
            pygame.draw.line(display, stripe_color, 
                           (self.x + i, self.y), 
                           (self.x, self.y + i), 2)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def emit(self, x, y, color, count=10):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color,
                random.randint(20, 40),
                random.randint(3, 6)
            ))
    
    def update(self):
        for particle in self.particles[:]:
            particle.x += particle.vx
            particle.y += particle.vy
            particle.lifetime -= 1
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def draw(self, display):
        for particle in self.particles:
            alpha = int((particle.lifetime / 40) * 255)
            pygame.draw.circle(display, particle.color, 
                             (int(particle.x), int(particle.y)), particle.size)

class GameState:
    def __init__(self):
        self.mode = GameMode.MENU
        self.score = 0
        self.high_score = self.load_high_score()
        self.level = 1
        self.power_ups = []
        self.obstacles = []
        self.active_power_up = None
        self.power_up_timer = 0
        self.invincible = False
        self.double_points = False
        self.particle_system = ParticleSystem()
        self.time_remaining = 60
        self.start_time = 0
        self.stars = [Star() for _ in range(50)]
        self.trails = []
        self.screen_shake = 0
        self.combo = 0
        self.combo_timer = 0
        
    def load_high_score(self):
        try:
            with open('snake_highscore.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open('snake_highscore.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

def show_score(game_state):
    # Score with shadow
    shadow_value = score_font.render(f"Score: {game_state.score}", True, Colors.BLACK)
    display.blit(shadow_value, [12, 12])
    value = score_font.render(f"Score: {game_state.score}", True, Colors.WHITE)
    display.blit(value, [10, 10])
    
    # High Score with trophy icon
    trophy_x = 10
    trophy_y = 55
    pygame.draw.polygon(display, Colors.GOLD, 
                       [(trophy_x, trophy_y), (trophy_x - 5, trophy_y + 8), (trophy_x + 5, trophy_y + 8)])
    pygame.draw.rect(display, Colors.GOLD, [trophy_x - 3, trophy_y + 8, 6, 3])
    
    high_score_text = font_small.render(f"High: {game_state.high_score}", True, Colors.GOLD)
    display.blit(high_score_text, [25, 50])
    
    # Level with badge
    level_bg_width = 100
    pygame.draw.rect(display, Colors.DARK_GRAY, 
                    [WIDTH - level_bg_width - 10, 5, level_bg_width, 30], border_radius=5)
    level_text = font_small.render(f"Level: {game_state.level}", True, Colors.CYAN)
    display.blit(level_text, [WIDTH - 100, 10])
    
    # Combo counter
    if game_state.combo > 1:
        combo_size = min(50, 30 + game_state.combo * 2)
        combo_font = pygame.font.SysFont("bahnschrift", combo_size)
        combo_text = combo_font.render(f"COMBO x{game_state.combo}!", True, Colors.GOLD)
        combo_rect = combo_text.get_rect(center=(WIDTH // 2, 100))
        
        # Combo glow
        for offset in range(3, 0, -1):
            glow_combo = combo_font.render(f"COMBO x{game_state.combo}!", True, Colors.ORANGE)
            glow_rect = glow_combo.get_rect(center=(WIDTH // 2 + offset, 100 + offset))
            display.blit(glow_combo, glow_rect)
        
        display.blit(combo_text, combo_rect)
    
    # Power-up indicator with icon
    if game_state.active_power_up:
        power_bg_y = 40
        pygame.draw.rect(display, Colors.DARK_GRAY, 
                        [WIDTH - 210, power_bg_y, 200, 40], border_radius=5)
        
        power_text = font_small.render(f"{game_state.active_power_up.name}", True, Colors.YELLOW)
        display.blit(power_text, [WIDTH - 200, power_bg_y + 5])
        
        # Animated timer bar
        timer_bar_width = (game_state.power_up_timer / 300) * 180
        bar_y = power_bg_y + 25
        pygame.draw.rect(display, Colors.GRAY, [WIDTH - 200, bar_y, 180, 10], border_radius=5)
        
        # Gradient bar
        for i in range(int(timer_bar_width)):
            color_val = int((i / 180) * 255)
            bar_color = (255 - color_val, color_val, 0)
            pygame.draw.rect(display, bar_color, [WIDTH - 200 + i, bar_y, 1, 10])
        
        pygame.draw.rect(display, Colors.WHITE, [WIDTH - 200, bar_y, 180, 10], 2, border_radius=5)
    
    # Time remaining (for timed mode) with progress bar
    if game_state.mode == GameMode.TIMED:
        time_color = Colors.RED if game_state.time_remaining < 10 else Colors.YELLOW
        
        # Time text with urgency effect
        if game_state.time_remaining < 10:
            time_size = int(25 + math.sin(pygame.time.get_ticks() / 100) * 3)
            urgent_font = pygame.font.SysFont("bahnschrift", time_size)
            time_text = urgent_font.render(f"Time: {game_state.time_remaining}s", True, time_color)
        else:
            time_text = font_style.render(f"Time: {game_state.time_remaining}s", True, time_color)
        
        time_rect = time_text.get_rect(center=(WIDTH // 2, 10))
        display.blit(time_text, time_rect)

def draw_snake(block_size, snake_list, game_state):
    for i, segment in enumerate(snake_list):
        # Gradient effect from head to tail
        if i == len(snake_list) - 1:  # Head
            color = Colors.NEON_GREEN
            
            # Head shadow
            pygame.draw.rect(display, Colors.DARK_GREEN, 
                           [segment[0] + 2, segment[1] + 2, block_size, block_size])
            
            # Main head
            pygame.draw.rect(display, color, [segment[0], segment[1], block_size, block_size])
            
            # Head highlight
            highlight_color = (100, 255, 100)
            pygame.draw.rect(display, highlight_color, 
                           [segment[0] + 2, segment[1] + 2, block_size - 4, block_size - 4])
            
            # Eyes with animation
            eye_pulse = math.sin(pygame.time.get_ticks() / 200) * 0.5 + 0.5
            eye_size = int(3 + eye_pulse)
            
            # Eye whites
            pygame.draw.circle(display, Colors.WHITE, (segment[0] + 6, segment[1] + 6), eye_size + 1)
            pygame.draw.circle(display, Colors.WHITE, (segment[0] + 14, segment[1] + 6), eye_size + 1)
            
            # Pupils
            pygame.draw.circle(display, Colors.BLACK, (segment[0] + 6, segment[1] + 6), eye_size)
            pygame.draw.circle(display, Colors.BLACK, (segment[0] + 14, segment[1] + 6), eye_size)
            
            # Shine in eyes
            pygame.draw.circle(display, Colors.WHITE, (segment[0] + 7, segment[1] + 5), 1)
            pygame.draw.circle(display, Colors.WHITE, (segment[0] + 15, segment[1] + 5), 1)
            
            # Tongue (every few frames)
            if pygame.time.get_ticks() % 1000 < 100:
                pygame.draw.line(display, Colors.RED, 
                               (segment[0] + block_size // 2, segment[1] + block_size), 
                               (segment[0] + block_size // 2, segment[1] + block_size + 4), 2)
        else:  # Body
            intensity = int(200 * (i / max(len(snake_list), 1)))
            
            # Body segment with gradient
            color = (0, min(255, 80 + intensity), 0)
            
            # Draw segment with 3D effect
            pygame.draw.rect(display, color, [segment[0], segment[1], block_size, block_size])
            
            # Scales pattern
            scale_color = (0, min(255, 100 + intensity), 0)
            for sx in range(2):
                for sy in range(2):
                    scale_x = segment[0] + sx * (block_size // 2) + 2
                    scale_y = segment[1] + sy * (block_size // 2) + 2
                    pygame.draw.circle(display, scale_color, 
                                     (scale_x, scale_y), 3)
            
            # Inner highlight
            inner_color = (50, min(255, 120 + intensity), 50)
            pygame.draw.rect(display, inner_color, 
                           [segment[0] + 3, segment[1] + 3, block_size - 6, block_size - 6])
        
        # Invincible shield effect with animation
        if game_state.invincible:
            shield_pulse = math.sin(pygame.time.get_ticks() / 100) * 2
            shield_colors = [Colors.ORANGE, Colors.YELLOW, Colors.GOLD]
            for idx, offset in enumerate([4, 6, 8]):
                color = shield_colors[idx % len(shield_colors)]
                pygame.draw.rect(display, color, 
                               [segment[0] - offset - shield_pulse, 
                                segment[1] - offset - shield_pulse, 
                                block_size + offset * 2 + shield_pulse * 2, 
                                block_size + offset * 2 + shield_pulse * 2], 1)

def message(msg, color, y_offset=0):
    mesg = font_style.render(msg, True, color)
    text_rect = mesg.get_rect(center=(WIDTH // 2, HEIGHT // 3 + y_offset))
    display.blit(mesg, text_rect)

def draw_menu(game_state):
    display.fill(Colors.BLACK)
    
    # Draw animated stars in background
    for star in game_state.stars:
        star.update()
        star.draw(display)
    
    # Animated title with glow
    pulse = math.sin(pygame.time.get_ticks() / 200) * 10
    
    # Title glow effect
    for offset in range(5, 0, -1):
        glow_alpha = 255 - offset * 40
        glow_color = (0, glow_alpha, 0)
        title_glow = title_font.render("ULTIMATE SNAKE", True, glow_color)
        glow_rect = title_glow.get_rect(center=(WIDTH // 2 + offset, 100 + pulse + offset))
        display.blit(title_glow, glow_rect)
    
    title = title_font.render("ULTIMATE SNAKE", True, Colors.NEON_GREEN)
    title_rect = title.get_rect(center=(WIDTH // 2, 100 + pulse))
    display.blit(title, title_rect)
    
    # Animated subtitle with rainbow effect
    rainbow_colors = [Colors.GOLD, Colors.ORANGE, Colors.RED, Colors.MAGENTA, Colors.CYAN]
    color_index = (pygame.time.get_ticks() // 200) % len(rainbow_colors)
    subtitle = font_style.render("PRO EDITION", True, rainbow_colors[color_index])
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 160))
    display.blit(subtitle, subtitle_rect)
    
    # Draw decorative snakes around menu
    time_offset = pygame.time.get_ticks() / 1000
    for i in range(3):
        x = WIDTH // 2 + math.cos(time_offset + i * 2) * 200
        y = 200 + math.sin(time_offset + i * 2) * 50
        pygame.draw.circle(display, Colors.GREEN, (int(x), int(y)), 5)
    
    # Menu options with hover effect
    options = [
        ("1 - Classic Mode", 250),
        ("2 - Survival Mode (Obstacles)", 300),
        ("3 - Timed Mode (60 seconds)", 350),
        ("4 - Leaderboard", 400),
        ("Q - Quit", 500)
    ]
    
    mouse_pos = pygame.mouse.get_pos()
    
    for idx, (text, y) in enumerate(options):
        option_rect = pygame.Rect(WIDTH // 2 - 200, y - 15, 400, 30)
        
        # Hover effect
        if option_rect.collidepoint(mouse_pos):
            pygame.draw.rect(display, Colors.DARK_GREEN, option_rect, border_radius=10)
            option_text = font_style.render(text, True, Colors.NEON_GREEN)
            # Draw glow
            glow_text = font_style.render(text, True, Colors.LIGHT_GREEN)
            glow_rect = glow_text.get_rect(center=(WIDTH // 2 + 2, y + 2))
            display.blit(glow_text, glow_rect)
        else:
            option_text = font_style.render(text, True, Colors.WHITE)
        
        text_rect = option_text.get_rect(center=(WIDTH // 2, y))
        display.blit(option_text, text_rect)
        
        # Draw icons next to options
        icon_x = WIDTH // 2 - 220
        if idx == 0:  # Classic
            pygame.draw.circle(display, Colors.GREEN, (icon_x, y), 8)
        elif idx == 1:  # Survival
            pygame.draw.rect(display, Colors.GRAY, [icon_x - 6, y - 6, 12, 12])
        elif idx == 2:  # Timed
            pygame.draw.circle(display, Colors.YELLOW, (icon_x, y), 8, 2)
        elif idx == 3:  # Leaderboard
            pygame.draw.polygon(display, Colors.GOLD, 
                              [(icon_x, y - 8), (icon_x - 8, y + 8), (icon_x + 8, y + 8)])
    
    pygame.display.update()

def draw_leaderboard(game_state):
    display.fill(Colors.BLACK)
    
    title = title_font.render("LEADERBOARD", True, Colors.GOLD)
    title_rect = title.get_rect(center=(WIDTH // 2, 80))
    display.blit(title, title_rect)
    
    high_score_text = score_font.render(f"High Score: {game_state.high_score}", True, Colors.NEON_GREEN)
    score_rect = high_score_text.get_rect(center=(WIDTH // 2, 200))
    display.blit(high_score_text, score_rect)
    
    back_text = font_style.render("Press ESC to return to menu", True, Colors.WHITE)
    back_rect = back_text.get_rect(center=(WIDTH // 2, 500))
    display.blit(back_text, back_rect)
    
    pygame.display.update()

def spawn_power_up(game_state, snake_list):
    if len(game_state.power_ups) < 2 and random.random() < 0.02:
        while True:
            x = random.randrange(0, WIDTH, BLOCK_SIZE)
            y = random.randrange(0, HEIGHT, BLOCK_SIZE)
            if [x, y] not in snake_list and not any(obs.x == x and obs.y == y for obs in game_state.obstacles):
                power_type = random.choice(list(PowerUpType))
                game_state.power_ups.append(PowerUp(x, y, power_type))
                break

def spawn_obstacles(game_state, count):
    game_state.obstacles = []
    for _ in range(count):
        while True:
            x = random.randrange(BLOCK_SIZE * 2, WIDTH - BLOCK_SIZE * 2, BLOCK_SIZE)
            y = random.randrange(BLOCK_SIZE * 2, HEIGHT - BLOCK_SIZE * 2, BLOCK_SIZE)
            if not any(obs.x == x and obs.y == y for obs in game_state.obstacles):
                game_state.obstacles.append(Obstacle(x, y))
                break

def game_loop(game_state):
    game_over = False
    game_close = False
    
    current_speed = BASE_SPEED

    # Start position aligned to the grid (multiples of BLOCK_SIZE)
    x1 = int(round((WIDTH / 2) / BLOCK_SIZE) * BLOCK_SIZE)
    y1 = int(round((HEIGHT / 2) / BLOCK_SIZE) * BLOCK_SIZE)

    x1_change = 0
    y1_change = 0

    snake_list = []
    snake_length = 1

    # Place food on grid aligned positions
    foodx = random.randrange(0, WIDTH, BLOCK_SIZE)
    foody = random.randrange(0, HEIGHT, BLOCK_SIZE)
    
    # Setup based on game mode
    if game_state.mode == GameMode.SURVIVAL:
        spawn_obstacles(game_state, 5)
    elif game_state.mode == GameMode.TIMED:
        game_state.start_time = pygame.time.get_ticks()
        game_state.time_remaining = 60

    while not game_over:

        while game_close:
            display.fill(Colors.DARK_GRAY)
            
            # Draw game over screen
            game_over_text = title_font.render("GAME OVER", True, Colors.RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, 150))
            display.blit(game_over_text, game_over_rect)
            
            final_score_text = score_font.render(f"Final Score: {game_state.score}", True, Colors.WHITE)
            final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, 220))
            display.blit(final_score_text, final_score_rect)
            
            if game_state.score >= game_state.high_score:
                new_high_text = font_style.render("NEW HIGH SCORE!", True, Colors.GOLD)
                new_high_rect = new_high_text.get_rect(center=(WIDTH // 2, 270))
                display.blit(new_high_text, new_high_rect)
            
            message("Press C - Play Again | M - Menu | Q - Quit", Colors.WHITE, 150)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_state.score = 0
                        game_state.level = 1
                        game_state.power_ups = []
                        game_state.obstacles = []
                        game_state.active_power_up = None
                        game_state.invincible = False
                        game_state.double_points = False
                        game_loop(game_state)
                        return
                    if event.key == pygame.K_m:
                        game_state.mode = GameMode.MENU
                        return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Prevent reversing direction directly
                if event.key == pygame.K_LEFT and x1_change != BLOCK_SIZE:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT and x1_change != -BLOCK_SIZE:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP and y1_change != BLOCK_SIZE:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN and y1_change != -BLOCK_SIZE:
                    y1_change = BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_ESCAPE:
                    game_state.mode = GameMode.MENU
                    return

        # Update power-up timer
        if game_state.power_up_timer > 0:
            game_state.power_up_timer -= 1
            if game_state.power_up_timer == 0:
                game_state.active_power_up = None
                game_state.invincible = False
                game_state.double_points = False
                current_speed = BASE_SPEED + (game_state.level - 1) * 2

        # Move snake head
        x1 += x1_change
        y1 += y1_change

        # Check for collisions with boundaries
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            if not game_state.invincible:
                game_close = True

        # Update timed mode
        if game_state.mode == GameMode.TIMED:
            elapsed = (pygame.time.get_ticks() - game_state.start_time) / 1000
            game_state.time_remaining = max(0, 60 - int(elapsed))
            if game_state.time_remaining == 0:
                game_close = True

        # Background with gradient
        for y in range(0, HEIGHT, 4):
            darkness = int(y / HEIGHT * 20)
            color = (darkness, darkness, darkness)
            pygame.draw.line(display, color, (0, y), (WIDTH, y), 4)
        
        # Draw animated stars
        for star in game_state.stars:
            star.update()
            star.draw(display)
        
        # Draw grid with glow effect
        grid_color = (30, 30, 30)
        for x in range(0, WIDTH, BLOCK_SIZE):
            pygame.draw.line(display, grid_color, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, BLOCK_SIZE):
            pygame.draw.line(display, grid_color, (0, y), (WIDTH, y), 1)
        
        # Update and draw trails
        for trail in game_state.trails[:]:
            trail.update()
            if trail.lifetime <= 0:
                game_state.trails.remove(trail)
            else:
                trail.draw(display)
        
        # Draw food with advanced animation
        pulse = math.sin(pygame.time.get_ticks() / 100) * 3
        rotation = pygame.time.get_ticks() / 20
        
        # Food glow layers
        for i in range(3, 0, -1):
            glow_size = int(BLOCK_SIZE // 2 + pulse + i * 4)
            glow_alpha = 100 - i * 25
            glow_color = (200 + glow_alpha // 2, 50 + glow_alpha // 3, 50 + glow_alpha // 3)
            pygame.draw.circle(display, glow_color, 
                             (foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2), glow_size)
        
        # Main food body (apple-like)
        pygame.draw.circle(display, Colors.RED, 
                         (foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2), 
                         BLOCK_SIZE // 2)
        
        # Highlight
        pygame.draw.circle(display, (255, 150, 150), 
                         (foodx + BLOCK_SIZE // 2 - 3, foody + BLOCK_SIZE // 2 - 3), 
                         BLOCK_SIZE // 4)
        
        # Sparkles around food
        for i in range(4):
            angle = rotation + i * (math.pi / 2)
            sparkle_dist = BLOCK_SIZE // 2 + pulse + 8
            sparkle_x = foodx + BLOCK_SIZE // 2 + math.cos(angle) * sparkle_dist
            sparkle_y = foody + BLOCK_SIZE // 2 + math.sin(angle) * sparkle_dist
            sparkle_size = 2 + int(pulse / 2)
            pygame.draw.circle(display, Colors.YELLOW, (int(sparkle_x), int(sparkle_y)), sparkle_size)

        # Draw obstacles
        for obstacle in game_state.obstacles:
            obstacle.draw(display)
        
        # Spawn and draw power-ups
        spawn_power_up(game_state, snake_list)
        for power_up in game_state.power_ups:
            if power_up.active:
                power_up.draw(display)
        
        snake_head = [x1, y1]
        snake_list.append(snake_head)

        if len(snake_list) > snake_length:
            del snake_list[0]

        # Check collision with self
        for segment in snake_list[:-1]:
            if segment == snake_head:
                if not game_state.invincible:
                    game_close = True
        
        # Check collision with obstacles
        for obstacle in game_state.obstacles:
            if obstacle.x == x1 and obstacle.y == y1:
                if not game_state.invincible:
                    game_close = True

        # Check collision with power-ups
        for power_up in game_state.power_ups[:]:
            if power_up.active and power_up.x == x1 and power_up.y == y1:
                game_state.particle_system.emit(x1 + BLOCK_SIZE // 2, y1 + BLOCK_SIZE // 2, Colors.GOLD, 20)
                game_state.active_power_up = power_up.type
                game_state.power_up_timer = 300  # 5 seconds at 60 FPS
                
                if power_up.type == PowerUpType.SPEED_BOOST:
                    current_speed = BASE_SPEED * 2
                elif power_up.type == PowerUpType.SLOW_DOWN:
                    current_speed = max(5, BASE_SPEED // 2)
                elif power_up.type == PowerUpType.DOUBLE_POINTS:
                    game_state.double_points = True
                elif power_up.type == PowerUpType.INVINCIBLE:
                    game_state.invincible = True
                elif power_up.type == PowerUpType.SHRINK:
                    snake_length = max(1, snake_length - 3)
                
                game_state.power_ups.remove(power_up)

        draw_snake(BLOCK_SIZE, snake_list, game_state)
        
        # Update and draw particles
        game_state.particle_system.update()
        game_state.particle_system.draw(display)
        
        show_score(game_state)

        pygame.display.update()

        # Add trail behind snake head
        if len(snake_list) > 0 and random.random() < 0.5:
            head = snake_list[-1]
            game_state.trails.append(Trail(head[0], head[1]))
        
        # Update combo timer
        if game_state.combo_timer > 0:
            game_state.combo_timer -= 1
            if game_state.combo_timer == 0:
                game_state.combo = 0
        
        # Check if snake ate the food
        if x1 == foodx and y1 == foody:
            # Screen shake effect
            game_state.screen_shake = 5
            
            # Emit different particles based on combo
            particle_count = 15 + game_state.combo * 5
            game_state.particle_system.emit(foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2, 
                                          Colors.RED, particle_count)
            game_state.particle_system.emit(foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2, 
                                          Colors.ORANGE, particle_count // 2)
            game_state.particle_system.emit(foodx + BLOCK_SIZE // 2, foody + BLOCK_SIZE // 2, 
                                          Colors.YELLOW, particle_count // 3)
            
            # Combo system
            game_state.combo += 1
            game_state.combo_timer = 120  # 2 seconds to maintain combo
            
            while True:
                foodx = random.randrange(0, WIDTH, BLOCK_SIZE)
                foody = random.randrange(0, HEIGHT, BLOCK_SIZE)
                if [foodx, foody] not in snake_list and not any(obs.x == foodx and obs.y == foody for obs in game_state.obstacles):
                    break
            
            points = 2 if game_state.double_points else 1
            game_state.score += points
            snake_length += 1
            
            # Level up every 5 points
            if game_state.score % 5 == 0:
                game_state.level += 1
                current_speed = min(30, BASE_SPEED + (game_state.level - 1) * 2)
                if game_state.mode == GameMode.SURVIVAL:
                    spawn_obstacles(game_state, 5 + game_state.level)
            
            # Update high score
            if game_state.score > game_state.high_score:
                game_state.high_score = game_state.score
                game_state.save_high_score()

        clock.tick(int(current_speed))

    pygame.quit()
    sys.exit()

def main():
    game_state = GameState()
    
    while True:
        if game_state.mode == GameMode.MENU:
            draw_menu(game_state)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        game_state.mode = GameMode.CLASSIC
                        game_state.score = 0
                        game_state.level = 1
                        game_state.power_ups = []
                        game_state.obstacles = []
                        game_loop(game_state)
                    elif event.key == pygame.K_2:
                        game_state.mode = GameMode.SURVIVAL
                        game_state.score = 0
                        game_state.level = 1
                        game_state.power_ups = []
                        game_loop(game_state)
                    elif event.key == pygame.K_3:
                        game_state.mode = GameMode.TIMED
                        game_state.score = 0
                        game_state.level = 1
                        game_state.power_ups = []
                        game_state.obstacles = []
                        game_loop(game_state)
                    elif event.key == pygame.K_4:
                        game_state.mode = GameMode.LEADERBOARD
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
        
        elif game_state.mode == GameMode.LEADERBOARD:
            draw_leaderboard(game_state)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state.mode = GameMode.MENU
        
        clock.tick(60)

if __name__ == "__main__":
    main()