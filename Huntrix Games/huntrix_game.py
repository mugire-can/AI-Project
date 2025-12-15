"""
The Huntrix - K-Pop Adventure Game
A magical rhythm and adventure game for ages 6-15
Inspired by K-Pop culture and cartoon aesthetics
"""

import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (Bright, colorful palette for young girls)
PINK = (255, 192, 203)
HOT_PINK = (255, 105, 180)
PURPLE = (186, 85, 211)
LIGHT_PURPLE = (221, 160, 221)
SKY_BLUE = (135, 206, 235)
MINT = (152, 255, 152)
YELLOW = (255, 255, 102)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

class Particle:
    """Sparkle particle effect"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = color
        self.life = 255
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 5
        self.vy += 0.1  # Gravity
        
    def draw(self, screen):
        if self.life > 0:
            size = max(1, int(self.size * (self.life / 255)))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
            # Glow effect
            if size > 1:
                glow_color = tuple(min(255, c + 50) for c in self.color[:3])
                pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), size + 1, 1)
    
    def is_alive(self):
        return self.life > 0

class Trail:
    """Motion trail effect"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 128
        self.size = 30
        
    def update(self):
        self.alpha -= 8
        
    def draw(self, screen):
        if self.alpha > 0:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            col = (*self.color[:3], self.alpha)
            pygame.draw.circle(s, col, (self.size, self.size), self.size)
            screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))
    
    def is_alive(self):
        return self.alpha > 0

class KPopStar:
    """Playable K-Pop character"""
    def __init__(self, x, y, name, color):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.size = 40
        self.speed = 5
        self.stars_collected = 0
        self.hearts = 3
        self.power_level = 0
        self.is_dancing = False
        self.dance_frame = 0
        self.animation_frame = 0
        self.trail_timer = 0
        self.bounce_offset = 0
        
    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Keep player on screen
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
    
    def draw(self, screen):
        # Animate bounce
        self.animation_frame += 1
        self.bounce_offset = math.sin(self.animation_frame * 0.2) * 3
        
        draw_y = int(self.y + self.bounce_offset)
        
        # Outer glow/aura
        for i in range(3):
            glow_color = (*self.color[:3], 30)
            s = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            pygame.draw.circle(s, glow_color, (self.size * 1.5, self.size * 1.5), 
                             self.size + 10 - i * 3)
            screen.blit(s, (int(self.x - self.size * 1.5), draw_y - self.size * 1.5))
        
        # Body (dress/outfit) with gradient effect
        for r in range(self.size, 0, -2):
            shade = min(255, self.color[0] + (self.size - r) * 2)
            body_color = (shade, self.color[1], self.color[2])
            pygame.draw.circle(screen, body_color, (int(self.x), draw_y + 10), r)
        
        # Dress shine
        pygame.draw.circle(screen, WHITE, (int(self.x - 10), draw_y + 5), 5, 2)
        
        # Head with shading
        pygame.draw.circle(screen, PINK, (int(self.x), draw_y - 10), self.size // 2)
        pygame.draw.circle(screen, (255, 200, 210), (int(self.x - 5), draw_y - 12), self.size // 3)
        
        # Eyes with animation
        eye_offset = 8
        blink = 1 if self.animation_frame % 120 > 3 else 0
        if blink:
            pygame.draw.circle(screen, BLACK, (int(self.x) - eye_offset, draw_y - 12), 5)
            pygame.draw.circle(screen, BLACK, (int(self.x) + eye_offset, draw_y - 12), 5)
            pygame.draw.circle(screen, WHITE, (int(self.x) - eye_offset + 2, draw_y - 13), 2)
            pygame.draw.circle(screen, WHITE, (int(self.x) + eye_offset + 2, draw_y - 13), 2)
        else:
            pygame.draw.line(screen, BLACK, (int(self.x) - eye_offset - 3, draw_y - 12),
                           (int(self.x) - eye_offset + 3, draw_y - 12), 2)
            pygame.draw.line(screen, BLACK, (int(self.x) + eye_offset - 3, draw_y - 12),
                           (int(self.x) + eye_offset + 3, draw_y - 12), 2)
        
        # Blush
        pygame.draw.circle(screen, (255, 150, 180), (int(self.x) - 15, draw_y - 5), 4)
        pygame.draw.circle(screen, (255, 150, 180), (int(self.x) + 15, draw_y - 5), 4)
        
        # Smile
        pygame.draw.arc(screen, HOT_PINK, 
                       (int(self.x) - 8, draw_y - 8, 16, 10), 
                       3.14, 0, 3)
        
        # Hair with multiple layers
        for i in range(3):
            offset_x = (i - 1) * 12
            pygame.draw.circle(screen, self.color, 
                             (int(self.x) + offset_x, draw_y - 25), 9)
            pygame.draw.circle(screen, WHITE, 
                             (int(self.x) + offset_x, draw_y - 25), 9, 1)
        
        # Hair accessories
        pygame.draw.circle(screen, GOLD, (int(self.x) - 15, draw_y - 25), 4)
        pygame.draw.circle(screen, GOLD, (int(self.x) + 15, draw_y - 25), 4)
        
        # Sparkle effect when dancing
        if self.is_dancing:
            for i in range(6):
                angle = (self.dance_frame + i * 60) * math.pi / 180
                sparkle_x = self.x + math.cos(angle) * 55
                sparkle_y = draw_y + math.sin(angle) * 55
                star_size = 4 + math.sin(self.dance_frame * 0.1 + i) * 2
                # Draw sparkle star
                for j in range(4):
                    spark_angle = j * math.pi / 2 + angle
                    x1 = sparkle_x + math.cos(spark_angle) * star_size
                    y1 = sparkle_y + math.sin(spark_angle) * star_size
                    x2 = sparkle_x + math.cos(spark_angle + math.pi / 4) * star_size * 0.4
                    y2 = sparkle_y + math.sin(spark_angle + math.pi / 4) * star_size * 0.4
                    pygame.draw.line(screen, GOLD, (int(sparkle_x), int(sparkle_y)), 
                                   (int(x1), int(y1)), 2)
            self.dance_frame = (self.dance_frame + 10) % 360

class CollectibleStar:
    """Stars to collect (like music notes)"""
    def __init__(self):
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.size = 15
        self.color = random.choice([GOLD, YELLOW, PINK, PURPLE])
        self.pulse = 0
        
    def draw(self, screen):
        # Pulsing star effect
        pulse_size = self.size + math.sin(self.pulse) * 3
        self.pulse += 0.1
        
        # Rotating glow
        rotation = self.pulse * 20
        
        # Outer glow rings
        for ring in range(3):
            glow_size = pulse_size + 8 - ring * 3
            glow_alpha = 50 - ring * 15
            s = pygame.Surface((glow_size * 3, glow_size * 3), pygame.SRCALPHA)
            glow_col = (*self.color[:3], glow_alpha)
            pygame.draw.circle(s, glow_col, (glow_size * 1.5, glow_size * 1.5), glow_size)
            screen.blit(s, (self.x - glow_size * 1.5, self.y - glow_size * 1.5))
        
        # Draw star shape
        points = []
        for i in range(10):
            angle = (i * 36 + rotation) * math.pi / 180
            if i % 2 == 0:
                r = pulse_size
            else:
                r = pulse_size / 2
            x = self.x + r * math.cos(angle - math.pi / 2)
            y = self.y + r * math.sin(angle - math.pi / 2)
            points.append((x, y))
        
        # Shadow
        shadow_points = [(x + 2, y + 2) for x, y in points]
        pygame.draw.polygon(screen, (0, 0, 0, 50), shadow_points)
        
        # Main star with gradient
        pygame.draw.polygon(screen, self.color, points)
        
        # Inner lighter star
        inner_points = []
        for i in range(10):
            angle = (i * 36 + rotation) * math.pi / 180
            if i % 2 == 0:
                r = pulse_size * 0.6
            else:
                r = pulse_size * 0.3
            x = self.x + r * math.cos(angle - math.pi / 2)
            y = self.y + r * math.sin(angle - math.pi / 2)
            inner_points.append((x, y))
        lighter_color = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.polygon(screen, lighter_color, inner_points)
        
        # Outline
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Sparkle points
        for i in range(5):
            angle = (i * 72 + rotation * 2) * math.pi / 180
            sx = self.x + math.cos(angle - math.pi / 2) * pulse_size
            sy = self.y + math.sin(angle - math.pi / 2) * pulse_size
            pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), 2)

class MusicNote:
    """Floating music notes for rhythm game"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = -20
        self.speed = random.randint(2, 4)
        self.size = 20
        self.color = random.choice([HOT_PINK, PURPLE, SKY_BLUE])
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        # Glow effect
        s = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        glow_col = (*self.color[:3], 80)
        pygame.draw.circle(s, glow_col, (self.size * 1.5, self.size * 1.5), self.size)
        screen.blit(s, (self.x - self.size * 1.5, self.y - self.size * 1.5))
        
        # Musical note with shadow
        shadow_offset = 2
        pygame.draw.circle(screen, (0, 0, 0, 100), 
                         (int(self.x) + shadow_offset, int(self.y) + shadow_offset), 
                         self.size // 2)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size // 2)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size // 2, 2)
        
        # Note stem
        stem_x = int(self.x) + self.size // 2 - 2
        stem_y = int(self.y) - self.size
        pygame.draw.rect(screen, self.color, (stem_x, stem_y, 4, self.size))
        
        # Note flag
        pygame.draw.circle(screen, self.color, (int(self.x) + self.size // 2, stem_y), 5)
        
        # Shine
        pygame.draw.circle(screen, WHITE, (int(self.x) - 3, int(self.y) - 3), 3)
        
    def off_screen(self):
        return self.y > SCREEN_HEIGHT

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🎵 The Huntrix - K-Pop Adventure 🎵")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game states
        self.state = "menu"  # menu, character_select, playing, rhythm_mode
        self.selected_character = None
        
        # K-Pop characters to choose from
        self.characters = [
            {"name": "Luna Star", "color": PINK},
            {"name": "Violet Dream", "color": PURPLE},
            {"name": "Sky Melody", "color": SKY_BLUE},
            {"name": "Mint Harmony", "color": MINT}
        ]
        
        self.player = None
        self.stars = []
        self.music_notes = []
        self.particles = []
        self.trails = []
        self.score = 0
        self.level = 1
        self.spawn_timer = 0
        self.bg_stars = [(random.randint(0, SCREEN_WIDTH), 
                         random.randint(0, SCREEN_HEIGHT),
                         random.randint(1, 3)) for _ in range(50)]
        
        # Initialize collectibles
        for _ in range(5):
            self.stars.append(CollectibleStar())
        
    def draw_background_stars(self):
        """Draw twinkling background stars"""
        for i, (x, y, size) in enumerate(self.bg_stars):
            twinkle = math.sin(pygame.time.get_ticks() * 0.005 + i) * 0.5 + 0.5
            alpha = int(150 * twinkle)
            color = (255, 255, 255, alpha)
            pygame.draw.circle(self.screen, WHITE, (x, y), size)
    
    def draw_menu(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_blend = (
                200 + int(y * 0.05),
                150 - int(y * 0.1),
                255 - int(y * 0.1)
            )
            pygame.draw.line(self.screen, color_blend, (0, y), (SCREEN_WIDTH, y))
        
        self.draw_background_stars()
        
        # Title with sparkles
        title = self.font_large.render("THE HUNTRIX", True, HOT_PINK)
        subtitle = self.font_medium.render("K-Pop Adventure", True, PURPLE)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        
        # Draw decorative sparkles
        for i in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, 300)
            size = random.randint(2, 5)
            pygame.draw.circle(self.screen, GOLD, (x, y), size)
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        play_text = self.font_medium.render("Press SPACE to Start", True, WHITE)
        play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        pygame.draw.rect(self.screen, HOT_PINK, play_rect.inflate(40, 20), border_radius=10)
        self.screen.blit(play_text, play_rect)
        
        instructions = self.font_small.render("Arrow Keys to Move | Collect Stars | Catch Music Notes", True, BLACK)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(instructions, inst_rect)
        
    def draw_character_select(self):
        # Background
        for y in range(SCREEN_HEIGHT):
            color_blend = (
                150 + int(y * 0.1),
                200 - int(y * 0.15),
                255 - int(y * 0.05)
            )
            pygame.draw.line(self.screen, color_blend, (0, y), (SCREEN_WIDTH, y))
        
        self.draw_background_stars()
        
        title = self.font_large.render("Choose Your Star!", True, HOT_PINK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Draw character options
        x_start = 100
        y_pos = 200
        spacing = 180
        
        for i, char in enumerate(self.characters):
            x = x_start + i * spacing
            
            # Character preview circle
            pygame.draw.circle(self.screen, char["color"], (x, y_pos), 40)
            pygame.draw.circle(self.screen, PINK, (x, y_pos - 20), 20)
            
            # Eyes
            pygame.draw.circle(self.screen, BLACK, (x - 8, y_pos - 22), 3)
            pygame.draw.circle(self.screen, BLACK, (x + 8, y_pos - 22), 3)
            
            # Name
            name_text = self.font_small.render(char["name"], True, BLACK)
            name_rect = name_text.get_rect(center=(x, y_pos + 60))
            self.screen.blit(name_text, name_rect)
            
            # Number to select
            num_text = self.font_medium.render(str(i + 1), True, WHITE)
            num_rect = num_text.get_rect(center=(x, y_pos + 90))
            pygame.draw.circle(self.screen, HOT_PINK, (x, y_pos + 90), 20)
            self.screen.blit(num_text, num_rect)
        
        instructions = self.font_small.render("Press 1, 2, 3, or 4 to select your character", True, BLACK)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(instructions, inst_rect)
        
    def start_game(self, character_index):
        char = self.characters[character_index]
        self.player = KPopStar(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, char["name"], char["color"])
        self.stars = [CollectibleStar() for _ in range(5)]
        self.music_notes = []
        self.score = 0
        self.level = 1
        self.state = "playing"
        
    def draw_game(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_blend = (
                135 + int(y * 0.1),
                206 - int(y * 0.2),
                235 - int(y * 0.1)
            )
            pygame.draw.line(self.screen, color_blend, (0, y), (SCREEN_WIDTH, y))
        
        self.draw_background_stars()
        
        # Draw trails
        for trail in self.trails[:]:
            trail.draw(self.screen)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Draw music notes
        for note in self.music_notes:
            note.draw(self.screen)
        
        # Draw particles
        for particle in self.particles[:]:
            particle.draw(self.screen)
        
        # Draw player
        if self.player:
            self.player.draw(self.screen)
        
        # Draw HUD with shadows
        score_shadow = self.font_medium.render(f"Score: {self.score}", True, BLACK)
        score_text = self.font_medium.render(f"Score: {self.score}", True, GOLD)
        self.screen.blit(score_shadow, (12, 12))
        self.screen.blit(score_text, (10, 10))
        
        level_shadow = self.font_medium.render(f"Level: {self.level}", True, BLACK)
        level_text = self.font_medium.render(f"Level: {self.level}", True, CYAN)
        self.screen.blit(level_shadow, (12, 52))
        self.screen.blit(level_text, (10, 50))
        
        # Hearts with animation
        for i in range(self.player.hearts):
            heart_x = SCREEN_WIDTH - 40 - i * 40
            heart_y = 30
            # Draw heart shape
            pygame.draw.circle(self.screen, HOT_PINK, (heart_x - 5, heart_y - 2), 8)
            pygame.draw.circle(self.screen, HOT_PINK, (heart_x + 5, heart_y - 2), 8)
            points = [(heart_x - 12, heart_y), (heart_x, heart_y + 12), (heart_x + 12, heart_y)]
            pygame.draw.polygon(self.screen, HOT_PINK, points)
            # Heart outline
            pygame.draw.circle(self.screen, WHITE, (heart_x - 5, heart_y - 2), 8, 2)
            pygame.draw.circle(self.screen, WHITE, (heart_x + 5, heart_y - 2), 8, 2)
            pygame.draw.polygon(self.screen, WHITE, points, 2)
        
        # Power level bar with glow
        bar_x, bar_y = 10, 90
        pygame.draw.rect(self.screen, BLACK, (bar_x + 2, bar_y + 2, 204, 24))
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, 204, 24), 3)
        if self.player.power_level > 0:
            # Gradient power bar
            for x in range(int(self.player.power_level * 2)):
                ratio = x / 200
                color = (int(255 * (1 - ratio)), int(255 * ratio), int(100 + 155 * ratio))
                pygame.draw.line(self.screen, color, 
                               (bar_x + 2 + x, bar_y + 2), 
                               (bar_x + 2 + x, bar_y + 20))
            # Glow effect
            if self.player.power_level > 80:
                s = pygame.Surface((int(self.player.power_level * 2), 20), pygame.SRCALPHA)
                glow_col = (255, 215, 0, 100)
                pygame.draw.rect(s, glow_col, (0, 0, int(self.player.power_level * 2), 20))
                self.screen.blit(s, (bar_x + 2, bar_y + 2))
        
    def update_game(self):
        # Spawn music notes
        self.spawn_timer += 1
        if self.spawn_timer > 60 - (self.level * 5):
            self.music_notes.append(MusicNote())
            self.spawn_timer = 0
        
        # Update music notes
        for note in self.music_notes[:]:
            note.update()
            
            # Check collision with player
            if self.player:
                dist = math.sqrt((note.x - self.player.x)**2 + (note.y - self.player.y)**2)
                if dist < 40:
                    self.score += 10
                    self.player.power_level = min(100, self.player.power_level + 5)
                    self.player.is_dancing = True
                    # Create particles
                    for _ in range(10):
                        self.particles.append(Particle(note.x, note.y, note.color))
                    self.music_notes.remove(note)
                    continue
            
            # Remove off-screen notes
            if note.off_screen():
                self.music_notes.remove(note)
        
        # Check star collection
        if self.player:
            for star in self.stars[:]:
                dist = math.sqrt((star.x - self.player.x)**2 + (star.y - self.player.y)**2)
                if dist < 50:
                    self.score += 50
                    # Create explosion of particles
                    for _ in range(20):
                        self.particles.append(Particle(star.x, star.y, star.color))
                    self.stars.remove(star)
                    self.stars.append(CollectibleStar())
                    
                    # Level up every 5 stars
                    if self.score % 250 == 0:
                        self.level += 1
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # Update trails
        for trail in self.trails[:]:
            trail.update()
            if not trail.is_alive():
                self.trails.remove(trail)
        
        # Create player trail
        if self.player:
            self.player.trail_timer += 1
            if self.player.trail_timer > 3:
                self.trails.append(Trail(self.player.x, self.player.y, self.player.color))
                self.player.trail_timer = 0
        
    def run(self):
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if self.state == "menu":
                        if event.key == pygame.K_SPACE:
                            self.state = "character_select"
                    
                    elif self.state == "character_select":
                        if event.key == pygame.K_1:
                            self.start_game(0)
                        elif event.key == pygame.K_2:
                            self.start_game(1)
                        elif event.key == pygame.K_3:
                            self.start_game(2)
                        elif event.key == pygame.K_4:
                            self.start_game(3)
                    
                    elif self.state == "playing":
                        if event.key == pygame.K_ESCAPE:
                            self.state = "menu"
            
            # Handle movement in playing state
            if self.state == "playing" and self.player:
                keys = pygame.key.get_pressed()
                dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
                dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
                
                if dx != 0 or dy != 0:
                    self.player.move(dx, dy)
                    self.player.is_dancing = False
                
                self.update_game()
            
            # Draw based on state
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "character_select":
                self.draw_character_select()
            elif self.state == "playing":
                self.draw_game()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
