import pygame
import random
from enum import Enum

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)

# Setup display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bomberman')
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

class Wall:
    def __init__(self, x, y, breakable=False):
        self.x = x
        self.y = y
        self.breakable = breakable
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

    def draw(self):
        color = BROWN if self.breakable else GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

class Bomb:
    def __init__(self, x, y, power=2):
        self.x = x
        self.y = y
        self.power = power
        self.timer = 3000  # 3 seconds
        self.placed_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

    def update(self):
        elapsed = pygame.time.get_ticks() - self.placed_time
        return elapsed >= self.timer

    def draw(self):
        elapsed = pygame.time.get_ticks() - self.placed_time
        if elapsed % 500 < 250:
            color = RED
        else:
            color = ORANGE
        pygame.draw.circle(screen, color, self.rect.center, GRID_SIZE // 3)
        pygame.draw.circle(screen, BLACK, self.rect.center, GRID_SIZE // 3, 2)

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 500
        self.created_time = pygame.time.get_ticks()
        self.rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

    def update(self):
        elapsed = pygame.time.get_ticks() - self.created_time
        return elapsed >= self.timer

    def draw(self):
        pygame.draw.rect(screen, YELLOW, self.rect)
        pygame.draw.rect(screen, ORANGE, self.rect, 3)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.max_bombs = 1
        self.bomb_power = 2
        self.alive = True
        self.rect = pygame.Rect(x * GRID_SIZE + 5, y * GRID_SIZE + 5, GRID_SIZE - 10, GRID_SIZE - 10)

    def move(self, dx, dy, walls, bombs):
        new_x = self.x + dx
        new_y = self.y + dy

        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return

        # Check collision with walls
        for wall in walls:
            if wall.x == new_x and wall.y == new_y:
                return

        # Check collision with bombs
        for bomb in bombs:
            if bomb.x == new_x and bomb.y == new_y:
                return

        self.x = new_x
        self.y = new_y
        self.rect.x = self.x * GRID_SIZE + 5
        self.rect.y = self.y * GRID_SIZE + 5

    def place_bomb(self, bombs):
        # Check if already a bomb at this position
        for bomb in bombs:
            if bomb.x == self.x and bomb.y == self.y:
                return None
        
        # Check max bombs
        if len([b for b in bombs]) >= self.max_bombs:
            return None

        return Bomb(self.x, self.y, self.bomb_power)

    def draw(self):
        pygame.draw.circle(screen, BLUE, self.rect.center, GRID_SIZE // 3)
        pygame.draw.circle(screen, WHITE, self.rect.center, GRID_SIZE // 3, 2)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True
        self.rect = pygame.Rect(x * GRID_SIZE + 5, y * GRID_SIZE + 5, GRID_SIZE - 10, GRID_SIZE - 10)
        self.move_timer = 0
        self.move_delay = 500

    def update(self, walls, bombs, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.move_timer > self.move_delay:
            self.move_timer = current_time
            
            # Simple AI: random movement
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x = self.x + dx
                new_y = self.y + dy

                if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
                    continue

                # Check collision with walls
                collision = False
                for wall in walls:
                    if wall.x == new_x and wall.y == new_y:
                        collision = True
                        break

                # Check collision with bombs
                for bomb in bombs:
                    if bomb.x == new_x and bomb.y == new_y:
                        collision = True
                        break

                if not collision:
                    self.x = new_x
                    self.y = new_y
                    self.rect.x = self.x * GRID_SIZE + 5
                    self.rect.y = self.y * GRID_SIZE + 5
                    break

    def draw(self):
        pygame.draw.circle(screen, RED, self.rect.center, GRID_SIZE // 3)
        pygame.draw.circle(screen, WHITE, self.rect.center, GRID_SIZE // 3, 2)

def create_level():
    walls = []
    
    # Create border walls (unbreakable)
    for x in range(GRID_WIDTH):
        walls.append(Wall(x, 0, False))
        walls.append(Wall(x, GRID_HEIGHT - 1, False))
    for y in range(1, GRID_HEIGHT - 1):
        walls.append(Wall(0, y, False))
        walls.append(Wall(GRID_WIDTH - 1, y, False))
    
    # Create grid pattern walls (unbreakable)
    for y in range(2, GRID_HEIGHT - 2, 2):
        for x in range(2, GRID_WIDTH - 2, 2):
            walls.append(Wall(x, y, False))
    
    # Create random breakable walls
    for y in range(1, GRID_HEIGHT - 1):
        for x in range(1, GRID_WIDTH - 1):
            # Skip player starting area
            if (x <= 2 and y <= 2):
                continue
            
            # Skip unbreakable walls
            wall_exists = False
            for wall in walls:
                if wall.x == x and wall.y == y:
                    wall_exists = True
                    break
            
            if not wall_exists and random.random() < 0.4:
                walls.append(Wall(x, y, True))
    
    return walls

def create_enemies(num_enemies, walls):
    enemies = []
    attempts = 0
    max_attempts = 100
    
    while len(enemies) < num_enemies and attempts < max_attempts:
        attempts += 1
        x = random.randint(GRID_WIDTH // 2, GRID_WIDTH - 2)
        y = random.randint(1, GRID_HEIGHT - 2)
        
        # Check if position is occupied
        occupied = False
        for wall in walls:
            if wall.x == x and wall.y == y:
                occupied = True
                break
        
        if not occupied:
            enemies.append(Enemy(x, y))
    
    return enemies

def explode_bomb(bomb, walls, explosions):
    # Add center explosion
    explosions.append(Explosion(bomb.x, bomb.y))
    
    # Explode in 4 directions
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for dx, dy in directions:
        for i in range(1, bomb.power + 1):
            ex = bomb.x + dx * i
            ey = bomb.y + dy * i
            
            if ex < 0 or ex >= GRID_WIDTH or ey < 0 or ey >= GRID_HEIGHT:
                break
            
            # Check for walls
            hit_wall = False
            for wall in walls[:]:
                if wall.x == ex and wall.y == ey:
                    if wall.breakable:
                        walls.remove(wall)
                        explosions.append(Explosion(ex, ey))
                    hit_wall = True
                    break
            
            if hit_wall:
                break
            
            explosions.append(Explosion(ex, ey))

def check_explosion_hit(explosions, player, enemies):
    # Check player
    for explosion in explosions:
        if explosion.x == player.x and explosion.y == player.y:
            player.alive = False
    
    # Check enemies
    for enemy in enemies[:]:
        for explosion in explosions:
            if explosion.x == enemy.x and explosion.y == enemy.y:
                enemies.remove(enemy)
                break

def game_loop():
    # Initialize game objects
    player = Player(1, 1)
    walls = create_level()
    enemies = create_enemies(3, walls)
    bombs = []
    explosions = []
    
    running = True
    game_over = False
    win = False
    
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.alive and not game_over:
                    new_bomb = player.place_bomb(bombs)
                    if new_bomb:
                        bombs.append(new_bomb)
                
                if event.key == pygame.K_r and game_over:
                    # Restart game
                    return game_loop()
                
                if event.key == pygame.K_q and game_over:
                    running = False
        
        if not game_over:
            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player.move(0, -1, walls, bombs)
            if keys[pygame.K_DOWN]:
                player.move(0, 1, walls, bombs)
            if keys[pygame.K_LEFT]:
                player.move(-1, 0, walls, bombs)
            if keys[pygame.K_RIGHT]:
                player.move(1, 0, walls, bombs)
            
            # Update enemies
            for enemy in enemies:
                enemy.update(walls, bombs, player)
                
                # Check collision with player
                if enemy.x == player.x and enemy.y == player.y:
                    player.alive = False
            
            # Update bombs
            for bomb in bombs[:]:
                if bomb.update():
                    bombs.remove(bomb)
                    explode_bomb(bomb, walls, explosions)
            
            # Update explosions
            for explosion in explosions[:]:
                if explosion.update():
                    explosions.remove(explosion)
            
            # Check explosion hits
            check_explosion_hit(explosions, player, enemies)
            
            # Check win/lose conditions
            if not player.alive:
                game_over = True
                win = False
            elif len(enemies) == 0:
                game_over = True
                win = True
        
        # Drawing
        screen.fill(GREEN)
        
        # Draw grid
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (0, 200, 0), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (0, 200, 0), (0, y), (SCREEN_WIDTH, y))
        
        # Draw game objects
        for wall in walls:
            wall.draw()
        
        for bomb in bombs:
            bomb.draw()
        
        for explosion in explosions:
            explosion.draw()
        
        if player.alive:
            player.draw()
        
        for enemy in enemies:
            enemy.draw()
        
        # Draw UI
        score_text = font.render(f"Enemies Left: {len(enemies)}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        bombs_text = font.render(f"Bombs: {player.max_bombs - len(bombs)}", True, WHITE)
        screen.blit(bombs_text, (10, 40))
        
        # Draw game over screen
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            if win:
                msg = "YOU WIN!"
                color = GREEN
            else:
                msg = "GAME OVER!"
                color = RED
            
            game_over_text = font.render(msg, True, color)
            restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    game_loop()
