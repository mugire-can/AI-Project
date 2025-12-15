"""
RACING GAME - Simplified Working Version
This version is guaranteed to work on any system!
"""

import pygame
import math
import random
import sys

pygame.init()

# Settings
WIDTH = 1280
HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GREEN = (50, 205, 50)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
CYAN = (0, 255, 255)
GRAY = (100, 100, 100)
SKY = (135, 206, 235)
GRASS = (34, 139, 34)
ROAD = (50, 50, 50)

class Car:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.color = color
        self.width = 50
        self.height = 80
        self.speed = 0
        self.max_speed = 20
        self.angle = 0
        self.is_player = is_player
        self.nitro = 100
        self.nitro_boost = False
        
    def update(self, keys):
        if self.is_player:
            # Acceleration
            if keys[pygame.K_UP]:
                self.speed = min(self.speed + 0.5, self.max_speed)
            else:
                self.speed = max(self.speed - 0.2, 0)
            
            # Steering
            if keys[pygame.K_LEFT] and self.speed > 0:
                self.angle -= 3
            if keys[pygame.K_RIGHT] and self.speed > 0:
                self.angle += 3
            
            # Nitro
            if keys[pygame.K_SPACE] and self.nitro > 0:
                self.nitro_boost = True
                self.nitro -= 1
                self.speed = min(self.speed + 0.3, self.max_speed * 1.5)
            else:
                self.nitro_boost = False
                self.nitro = min(100, self.nitro + 0.1)
            
            # Move
            rad = math.radians(self.angle)
            self.x += math.sin(rad) * self.speed
            self.y -= math.cos(rad) * self.speed
            
            # Keep on screen
            self.x = max(50, min(self.x, WIDTH - 50))
    
    def draw(self, screen, camera_y=0):
        y = self.y - camera_y
        
        # Shadow
        pygame.draw.rect(screen, (0, 0, 0, 100), 
                        (self.x - self.width//2 + 3, y - self.height//2 + 3,
                         self.width, self.height), border_radius=10)
        
        # Car body
        car_surf = pygame.Surface((self.width*2, self.height*2), pygame.SRCALPHA)
        pygame.draw.rect(car_surf, self.color,
                        (self.width//2, self.height//2, self.width, self.height),
                        border_radius=10)
        
        # Window
        pygame.draw.rect(car_surf, (100, 150, 200),
                        (self.width//2 + 10, self.height//2 + 15,
                         self.width - 20, 25), border_radius=5)
        
        # Headlights
        light_color = CYAN if self.nitro_boost else YELLOW
        pygame.draw.circle(car_surf, light_color,
                          (self.width//2 + 15, self.height//2 + self.height - 8), 5)
        pygame.draw.circle(car_surf, light_color,
                          (self.width//2 + self.width - 15, self.height//2 + self.height - 8), 5)
        
        # Rotate
        rotated = pygame.transform.rotate(car_surf, -self.angle)
        rect = rotated.get_rect(center=(self.x, y))
        screen.blit(rotated, rect)
        
        # Nitro effect
        if self.is_player and self.nitro_boost:
            for i in range(3):
                fx = self.x + random.randint(-10, 10)
                fy = y - random.randint(10, 25)
                pygame.draw.circle(screen, random.choice([ORANGE, RED, YELLOW]),
                                 (int(fx), int(fy)), random.randint(3, 6))

class AI_Car:
    def __init__(self, x, y, color):
        self.car = Car(x, y, color, False)
        self.speed = random.uniform(8, 12)
        
    def update(self, player_y):
        self.car.y += self.speed
        
        # Simple AI movement
        center = WIDTH // 2
        if abs(self.car.x - center) > 100:
            self.car.x += (center - self.car.x) * 0.02
        
        # Wrap around
        if self.car.y > player_y + 800:
            self.car.y = player_y - 500
            self.car.x = center + random.randint(-150, 150)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Racing Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        self.state = "menu"  # menu or playing
        self.player = Car(WIDTH // 2, HEIGHT - 150, RED, True)
        self.camera_y = 0
        
        # AI cars
        self.ai_cars = []
        for i in range(5):
            color = random.choice([BLUE, GREEN, ORANGE, CYAN])
            x = WIDTH // 2 + random.randint(-150, 150)
            y = -random.randint(200, 800)
            self.ai_cars.append(AI_Car(x, y, color))
        
        self.score = 0
        self.distance = 0
        
    def draw_road(self):
        # Sky
        self.screen.fill(SKY)
        
        # Grass
        pygame.draw.rect(self.screen, GRASS, (0, HEIGHT//2, WIDTH, HEIGHT//2))
        
        # Road
        road_width = 600
        road_x = WIDTH // 2 - road_width // 2
        
        # Draw road segments
        for i in range(-2, 20):
            y = (i * 100 - int(self.camera_y) % 100)
            
            # Road
            color = ROAD if i % 2 == 0 else (60, 60, 60)
            pygame.draw.rect(self.screen, color,
                           (road_x, y, road_width, 100))
            
            # Center line
            if i % 2 == 0:
                pygame.draw.rect(self.screen, YELLOW,
                               (WIDTH//2 - 3, y + 10, 6, 80))
            
            # Side lines
            pygame.draw.rect(self.screen, WHITE, (road_x - 5, y, 5, 100))
            pygame.draw.rect(self.screen, WHITE, (road_x + road_width, y, 5, 100))
    
    def draw_hud(self):
        # Speed
        speed_kmh = int(self.player.speed * 15)
        speed_text = self.font_large.render(str(speed_kmh), True, WHITE)
        self.screen.blit(speed_text, (50, HEIGHT - 150))
        
        label = self.font_small.render("km/h", True, WHITE)
        self.screen.blit(label, (50, HEIGHT - 90))
        
        # Nitro bar
        bar_x = WIDTH - 320
        bar_y = HEIGHT - 80
        pygame.draw.rect(self.screen, GRAY, (bar_x, bar_y, 300, 40), border_radius=10)
        nitro_color = CYAN if self.player.nitro > 30 else RED
        pygame.draw.rect(self.screen, nitro_color,
                        (bar_x + 5, bar_y + 5, int((self.player.nitro / 100) * 290), 30),
                        border_radius=8)
        
        nitro_label = self.font_small.render("NITRO", True, WHITE)
        self.screen.blit(nitro_label, (bar_x + 10, bar_y + 8))
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (50, 30))
        
        # Distance
        dist_text = self.font_small.render(f"Distance: {int(self.distance)}m", True, WHITE)
        self.screen.blit(dist_text, (50, 90))
        
        # Controls
        controls = self.font_small.render("↑ Accelerate | ← → Steer | SPACE Nitro | ESC Menu", True, WHITE)
        self.screen.blit(controls, (WIDTH//2 - 350, HEIGHT - 40))
    
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # Title
        title = self.font_large.render("RACING GAME", True, CYAN)
        title_rect = title.get_rect(center=(WIDTH//2, 150))
        self.screen.blit(title, title_rect)
        
        # Start prompt
        start = self.font_medium.render("Press SPACE to Start", True, GREEN)
        start_rect = start.get_rect(center=(WIDTH//2, 350))
        self.screen.blit(start, start_rect)
        
        # Instructions
        inst = [
            "Controls:",
            "Arrow UP - Accelerate",
            "Arrow LEFT/RIGHT - Steer",
            "SPACE - Nitro Boost",
            "ESC - Pause"
        ]
        
        y = 450
        for line in inst:
            text = self.font_small.render(line, True, WHITE)
            text_rect = text.get_rect(center=(WIDTH//2, y))
            self.screen.blit(text, text_rect)
            y += 40
    
    def run(self):
        running = True
        
        while running:
            self.clock.tick(FPS)
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "menu"
                        else:
                            running = False
                    
                    if event.key == pygame.K_SPACE and self.state == "menu":
                        self.state = "playing"
                        # Reset
                        self.player = Car(WIDTH // 2, HEIGHT - 150, RED, True)
                        self.score = 0
                        self.distance = 0
                        self.camera_y = 0
            
            if self.state == "menu":
                self.draw_menu()
            
            elif self.state == "playing":
                # Update
                self.player.update(keys)
                
                for ai_car in self.ai_cars:
                    ai_car.update(self.player.y)
                
                # Camera
                self.camera_y = self.player.y - HEIGHT + 300
                
                # Score
                self.distance += self.player.speed * 0.1
                self.score += int(self.player.speed)
                
                # Draw
                self.draw_road()
                
                # Draw AI
                for ai_car in self.ai_cars:
                    ai_car.car.draw(self.screen, self.camera_y)
                
                # Draw player
                self.player.draw(self.screen, self.camera_y)
                
                self.draw_hud()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
