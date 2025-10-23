import pygame
import random
import sys
from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

# Display settings
WIDTH = 600
HEIGHT = 400
BLOCK_SIZE = 20
SPEED = 15

# Setup display
display = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def show_score(score):
    value = score_font.render(f"Score: {score}", True, WHITE)
    display.blit(value, [0, 0])

def draw_snake(block_size, snake_list):
    for x in snake_list:
        pygame.draw.rect(display, GREEN, [x[0], x[1], block_size, block_size])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    display.blit(mesg, [WIDTH / 6, HEIGHT / 3])

def game_loop():
    game_over = False
    game_close = False

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

    while not game_over:

        while game_close:
            display.fill(BLUE)
            message("Game Over! Press Q-Quit or C-Play Again", RED)
            show_score(snake_length - 1)
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
                        # Restart the game: call new loop and return to avoid stacking calls
                        game_loop()
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

        # Move snake head
        x1 += x1_change
        y1 += y1_change

        # Check for collisions with boundaries
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True

        display.fill(BLACK)
        pygame.draw.rect(display, RED, [foodx, foody, BLOCK_SIZE, BLOCK_SIZE])

        snake_head = [x1, y1]
        snake_list.append(snake_head)

        if len(snake_list) > snake_length:
            del snake_list[0]

        # Check collision with self
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        draw_snake(BLOCK_SIZE, snake_list)
        show_score(snake_length - 1)

        pygame.display.update()

        # Check if snake ate the food
        if x1 == foodx and y1 == foody:
            foodx = random.randrange(0, WIDTH, BLOCK_SIZE)
            foody = random.randrange(0, HEIGHT, BLOCK_SIZE)
            snake_length += 1

        clock.tick(SPEED)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()