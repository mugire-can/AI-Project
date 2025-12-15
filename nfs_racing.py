import pygame
import math
import random
import sys

pygame.init()

# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)
NIGHT_SKY = (20, 24, 82)
ROAD_DARK = (40, 40, 40)
ROAD_LIGHT = (60, 60, 60)

class Particle:
    def __init__(self, x, y, color, speed):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.lifetime = random.randint(10, 30)
        self.size = random.randint(2, 5)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy + self.speed
        self.lifetime -= 1
        self.size = max(1, self.size - 0.1)

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / 30))
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            screen.blit(s, (int(self.x), int(self.y)))

class Car:
    def __init__(self, x, y, color, is_player=False):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
        self.color = color
        self.speed = 0
        self.max_speed = 15 if is_player else random.uniform(3, 8)
        self.acceleration = 0.3
        self.deceleration = 0.2
        self.turn_speed = 5
        self.angle = 0
        self.drift_angle = 0
        self.is_player = is_player
        self.nitro = 100
        self.nitro_active = False
        self.lap = 0
        self.checkpoint_passed = False
        self.damage = 0
        
    def draw(self, screen, camera_y=0):
        # Car body with perspective
        draw_y = self.y - camera_y
        
        # Shadow
        shadow_surface = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80), (0, 0, self.width + 10, self.height + 10), border_radius=10)
        screen.blit(shadow_surface, (self.x - 5, draw_y + 5))
        
        # Main car body
        car_rect = pygame.Rect(self.x, draw_y, self.width, self.height)
        pygame.draw.rect(screen, self.color, car_rect, border_radius=8)
        
        # Windows
        window_color = (100, 150, 200, 180)
        pygame.draw.rect(screen, window_color, (self.x + 10, draw_y + 15, self.width - 20, 20), border_radius=5)
        
        # Headlights
        if self.is_player:
            light_color = YELLOW if not self.nitro_active else CYAN
            pygame.draw.circle(screen, light_color, (int(self.x + 15), int(draw_y + self.height - 10)), 5)
            pygame.draw.circle(screen, light_color, (int(self.x + self.width - 15), int(draw_y + self.height - 10)), 5)
        
        # Spoiler
        pygame.draw.rect(screen, DARK_GRAY, (self.x + 5, draw_y, self.width - 10, 8))
        
        # Racing stripes
        pygame.draw.rect(screen, WHITE, (self.x + self.width // 2 - 2, draw_y, 4, self.height))
        
        # Wheels
        wheel_color = BLACK
        pygame.draw.rect(screen, wheel_color, (self.x - 5, draw_y + 15, 8, 20), border_radius=3)
        pygame.draw.rect(screen, wheel_color, (self.x + self.width - 3, draw_y + 15, 8, 20), border_radius=3)
        pygame.draw.rect(screen, wheel_color, (self.x - 5, draw_y + self.height - 35, 8, 20), border_radius=3)
        pygame.draw.rect(screen, wheel_color, (self.x + self.width - 3, draw_y + self.height - 35, 8, 20), border_radius=3)
        
        # Nitro effect
        if self.is_player and self.nitro_active:
            for i in range(3):
                flame_x = self.x + self.width // 2 - 10 + i * 10
                flame_y = draw_y - random.randint(10, 20)
                flame_color = random.choice([ORANGE, RED, YELLOW])
                pygame.draw.circle(screen, flame_color, (int(flame_x), int(flame_y)), random.randint(3, 8))

class RoadSegment:
    def __init__(self, y, curve=0, width=400):
        self.y = y
        self.curve = curve
        self.width = width
        self.has_obstacle = random.random() < 0.1
        self.obstacle_x = random.randint(100, SCREEN_WIDTH - 100) if self.has_obstacle else 0

class AIRacer(Car):
    def __init__(self, x, y, color):
        super().__init__(x, y, color, False)
        self.target_x = x
        self.speed = random.uniform(5, 8)
        
    def update(self, road_segments, player_y):
        # Simple AI logic
        self.y += self.speed
        
        # Avoid obstacles and stay on road
        center_x = SCREEN_WIDTH // 2
        if abs(self.x - center_x) > 150:
            self.x += (center_x - self.x) * 0.05
        
        # Random lane changes
        if random.random() < 0.01:
            self.target_x = random.randint(SCREEN_WIDTH // 2 - 150, SCREEN_WIDTH // 2 + 150)
        
        self.x += (self.target_x - self.x) * 0.1
        
        # Wrap around
        if self.y > player_y + 1000:
            self.y = player_y - 500
            self.x = random.randint(SCREEN_WIDTH // 2 - 150, SCREEN_WIDTH // 2 + 150)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Need for Speed - Ultimate Racing")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 72)
        
        self.player = Car(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 200, RED, True)
        self.camera_y = 0
        self.road_scroll = 0
        self.score = 0
        self.distance = 0
        self.game_state = "menu"  # menu, playing, paused, gameover
        
        # AI racers
        self.ai_racers = []
        for i in range(5):
            color = random.choice([BLUE, GREEN, PURPLE, ORANGE, CYAN])
            x = random.randint(SCREEN_WIDTH // 2 - 150, SCREEN_WIDTH // 2 + 150)
            y = self.player.y - random.randint(200, 800)
            self.ai_racers.append(AIRacer(x, y, color))
        
        # Road segments
        self.road_segments = []
        for i in range(100):
            curve = math.sin(i * 0.1) * 50
            self.road_segments.append(RoadSegment(i * 100, curve))
        
        self.particles = []
        self.time_elapsed = 0
        self.best_time = float('inf')
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if self.game_state == "playing":
            # Acceleration
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.speed = min(self.player.speed + self.player.acceleration, self.player.max_speed)
            else:
                self.player.speed = max(0, self.player.speed - self.player.deceleration)
            
            # Braking
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.speed = max(0, self.player.speed - 0.5)
            
            # Steering
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.x -= self.player.turn_speed
                self.player.drift_angle = -5
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.x += self.player.turn_speed
                self.player.drift_angle = 5
            else:
                self.player.drift_angle = 0
            
            # Nitro boost
            if (keys[pygame.K_SPACE] or keys[pygame.K_LSHIFT]) and self.player.nitro > 0:
                self.player.nitro_active = True
                self.player.nitro -= 0.5
                self.player.speed = min(self.player.speed + 0.5, self.player.max_speed * 1.5)
                # Nitro particles
                for _ in range(3):
                    self.particles.append(Particle(
                        self.player.x + self.player.width // 2,
                        self.player.y - self.camera_y,
                        random.choice([ORANGE, RED, YELLOW]),
                        self.player.speed
                    ))
            else:
                self.player.nitro_active = False
                self.player.nitro = min(100, self.player.nitro + 0.1)
            
            # Keep player on screen
            self.player.x = max(SCREEN_WIDTH // 2 - 200, min(self.player.x, SCREEN_WIDTH // 2 + 200 - self.player.width))
    
    def update(self):
        if self.game_state == "playing":
            # Update camera
            self.camera_y = self.player.y - SCREEN_HEIGHT + 300
            self.road_scroll += self.player.speed
            
            # Update distance and score
            self.distance += self.player.speed * 0.1
            self.score += int(self.player.speed)
            self.time_elapsed += 1 / FPS
            
            # Update AI racers
            for racer in self.ai_racers:
                racer.update(self.road_segments, self.player.y)
                
                # Collision with player
                if (abs(self.player.x - racer.x) < 40 and 
                    abs(self.player.y - racer.y) < 60):
                    self.player.speed *= 0.7
                    racer.speed *= 0.7
                    # Crash particles
                    for _ in range(10):
                        self.particles.append(Particle(
                            self.player.x + self.player.width // 2,
                            self.player.y - self.camera_y,
                            random.choice([RED, ORANGE, YELLOW]),
                            0
                        ))
            
            # Update particles
            self.particles = [p for p in self.particles if p.lifetime > 0]
            for particle in self.particles:
                particle.update()
            
            # Generate new road segments
            while len(self.road_segments) < 100:
                last_segment = self.road_segments[-1]
                new_curve = last_segment.curve + random.uniform(-10, 10)
                new_y = last_segment.y + 100
                self.road_segments.append(RoadSegment(new_y, new_curve))
            
            # Remove old segments
            self.road_segments = [seg for seg in self.road_segments if seg.y > self.camera_y - 500]
    
    def draw_road(self):
        # Sky gradient
        for i in range(SCREEN_HEIGHT // 2):
            color_factor = i / (SCREEN_HEIGHT // 2)
            color = (
                int(NIGHT_SKY[0] + (100 - NIGHT_SKY[0]) * color_factor),
                int(NIGHT_SKY[1] + (100 - NIGHT_SKY[1]) * color_factor),
                int(NIGHT_SKY[2] + (150 - NIGHT_SKY[2]) * color_factor)
            )
            pygame.draw.line(self.screen, color, (0, i), (SCREEN_WIDTH, i))
        
        # Stars
        for _ in range(50):
            star_x = random.randint(0, SCREEN_WIDTH)
            star_y = random.randint(0, SCREEN_HEIGHT // 2)
            brightness = random.randint(150, 255)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (star_x, star_y), 1)
        
        # Road
        road_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        road_surface.fill(NIGHT_SKY)
        
        # Draw road segments
        for i, segment in enumerate(self.road_segments):
            screen_y = segment.y - self.camera_y
            
            if -200 < screen_y < SCREEN_HEIGHT + 200:
                # Road base
                road_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - segment.width // 2 + segment.curve,
                    screen_y,
                    segment.width,
                    100
                )
                color = ROAD_DARK if i % 2 == 0 else ROAD_LIGHT
                pygame.draw.rect(self.screen, color, road_rect)
                
                # Road markings
                if i % 3 == 0:
                    line_x = SCREEN_WIDTH // 2 + segment.curve
                    pygame.draw.rect(self.screen, YELLOW, (line_x - 3, screen_y, 6, 80))
                
                # Side lines
                pygame.draw.rect(self.screen, WHITE, 
                    (SCREEN_WIDTH // 2 - segment.width // 2 + segment.curve - 5, screen_y, 5, 100))
                pygame.draw.rect(self.screen, WHITE,
                    (SCREEN_WIDTH // 2 + segment.width // 2 + segment.curve, screen_y, 5, 100))
                
                # Obstacles
                if segment.has_obstacle:
                    obstacle_x = segment.obstacle_x + segment.curve
                    pygame.draw.rect(self.screen, RED, (obstacle_x - 15, screen_y + 20, 30, 40))
    
    def draw_hud(self):
        # Speed
        speed_text = self.font.render(f"Speed: {int(self.player.speed * 20)} km/h", True, WHITE)
        self.screen.blit(speed_text, (20, 20))
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 60))
        
        # Distance
        distance_text = self.font.render(f"Distance: {int(self.distance)} m", True, WHITE)
        self.screen.blit(distance_text, (20, 100))
        
        # Time
        time_text = self.font.render(f"Time: {int(self.time_elapsed)}s", True, WHITE)
        self.screen.blit(time_text, (20, 140))
        
        # Nitro bar
        pygame.draw.rect(self.screen, DARK_GRAY, (SCREEN_WIDTH - 220, 20, 200, 30), border_radius=5)
        nitro_width = int((self.player.nitro / 100) * 196)
        nitro_color = CYAN if self.player.nitro > 30 else RED
        pygame.draw.rect(self.screen, nitro_color, (SCREEN_WIDTH - 218, 22, nitro_width, 26), border_radius=5)
        nitro_text = self.small_font.render("NITRO", True, WHITE)
        self.screen.blit(nitro_text, (SCREEN_WIDTH - 210, 25))
        
        # Mini map (position indicator)
        pygame.draw.rect(self.screen, DARK_GRAY, (SCREEN_WIDTH - 220, 70, 200, 150), border_radius=10)
        pygame.draw.circle(self.screen, RED, (SCREEN_WIDTH - 120, 145), 8)  # Player
        
        # AI racers on minimap
        for racer in self.ai_racers:
            y_diff = (racer.y - self.player.y) * 0.1
            if -70 < y_diff < 70:
                minimap_y = 145 + int(y_diff)
                pygame.draw.circle(self.screen, racer.color, (SCREEN_WIDTH - 120, minimap_y), 5)
        
        # Controls hint
        controls = self.small_font.render("↑↓←→ Move | SPACE Nitro | ESC Menu", True, WHITE)
        self.screen.blit(controls, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT - 30))
    
    def draw_menu(self):
        self.screen.fill(NIGHT_SKY)
        
        # Title
        title = self.large_font.render("NEED FOR SPEED", True, CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font.render("Ultimate Racing", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_text = self.font.render("Press SPACE to Start", True, GREEN)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(start_text, start_rect)
        
        # Instructions
        instructions = [
            "Controls:",
            "Arrow Keys / WASD - Steer and Accelerate",
            "SPACE / SHIFT - Nitro Boost",
            "ESC - Pause Game",
            "",
            "Avoid traffic, collect speed, beat your best time!"
        ]
        
        y_offset = 500
        for instruction in instructions:
            inst_text = self.small_font.render(instruction, True, WHITE)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(inst_text, inst_rect)
            y_offset += 30
    
    def run(self):
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state == "playing":
                            self.game_state = "menu"
                        elif self.game_state == "menu":
                            running = False
                    
                    if event.key == pygame.K_SPACE and self.game_state == "menu":
                        self.game_state = "playing"
                        # Reset game
                        self.player = Car(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 200, RED, True)
                        self.score = 0
                        self.distance = 0
                        self.time_elapsed = 0
                        self.camera_y = 0
                        self.particles = []
            
            if self.game_state == "menu":
                self.draw_menu()
            elif self.game_state == "playing":
                self.handle_input()
                self.update()
                self.draw_road()
                
                # Draw AI racers
                for racer in self.ai_racers:
                    racer.draw(self.screen, self.camera_y)
                
                # Draw player
                self.player.draw(self.screen, self.camera_y)
                
                # Draw particles
                for particle in self.particles:
                    particle.draw(self.screen)
                
                self.draw_hud()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
