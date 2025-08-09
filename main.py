import pygame
import random
import sys
import asyncio
import platform

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
BACKGROUND_COLOR = (150, 150, 150)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
FPS = 60

# Obstacle sizes
OBSTACLE_SIZES = [(60, 100), (60, 100)]

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Obstacle Avoidance Game")

# Load fonts
font_large = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 36)

# Load images
def load_images(path, sizes):
    try:
        images = [pygame.image.load(f'{path}{i+1}.png').convert_alpha() for i in range(len(sizes))]
        return [pygame.transform.scale(img, sizes[i]) for i, img in enumerate(images)]
    except pygame.error:
        print(f"Cannot load images from {path}. Using rectangles instead.")
        surfaces = []
        for size in sizes:
            surface = pygame.Surface(size, pygame.SRCALPHA)
            pygame.draw.rect(surface, BLACK, (0, 0, size[0], size[1]))
            pygame.draw.rect(surface, GREEN, (0, 0, size[0], size[1]), 2)
            surfaces.append(surface)
        return surfaces

vehicles = pygame.image.load('./assets/catcher.png').convert_alpha()
vehicles = pygame.transform.scale(vehicles, (50, 80))
obstacles_types = load_images('./assets/obstacles/item', OBSTACLE_SIZES)
original_background = pygame.image.load('./assets/background.png').convert()

# Game variables
vehicle_image = None
vehicle_rect = None
obstacles = []
background_y = 0
speed = 5  # Background speed
obstacle_speed = 7  # Obstacle speed, different from background
last_spawn_time = 0
last_speed_increase = 0
score = 0
game_over = False
game_over_time = 0
scaled_background = None
clock = pygame.time.Clock()

# Start screen
def start_screen():
    screen.fill(BACKGROUND_COLOR)
    text = font_large.render("Press Enter to start", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

# Game setup
def setup():
    global vehicle_rect, obstacles, background_y, speed, obstacle_speed, score, game_over, last_spawn_time, last_speed_increase, vehicle_image, scaled_background
    vehicle_image = vehicles
    vehicle_rect = vehicle_image.get_rect()
    vehicle_rect.bottom = SCREEN_HEIGHT - 10
    vehicle_rect.centerx = SCREEN_WIDTH // 2
    obstacles = []
    background_y = 0
    speed = 5
    obstacle_speed = 7
    score = 0
    game_over = False
    last_spawn_time = pygame.time.get_ticks()
    last_speed_increase = pygame.time.get_ticks()
    # Scale background to match SCREEN_WIDTH, maintaining aspect ratio
    scale_factor = SCREEN_WIDTH / original_background.get_width()
    new_height = int(original_background.get_height() * scale_factor)
    scaled_background = pygame.transform.scale(original_background, (SCREEN_WIDTH, new_height))

async def main():
    global game_over, score, speed, obstacle_speed, background_y, last_spawn_time, last_speed_increase, game_over_time, SCREEN_WIDTH, SCREEN_HEIGHT, screen
    start_screen()
    setup()
    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                setup()
            if event.type == pygame.KEYDOWN:
                if game_over and current_time - game_over_time > 3000 and event.key == pygame.K_r:
                    setup()

        bg_height = scaled_background.get_height()
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and vehicle_rect.left > 0:
                vehicle_rect.x -= 5
            if keys[pygame.K_RIGHT] and vehicle_rect.right < SCREEN_WIDTH:
                vehicle_rect.x += 5

            background_y = (background_y + speed) % bg_height

            # Spawn obstacles
            if current_time - last_spawn_time > 1500:
                selected_image = random.choice(obstacles_types)
                obstacle_width = selected_image.get_width()
                obstacle_height = selected_image.get_height()
                left_limit = SCREEN_WIDTH // 4
                right_limit = SCREEN_WIDTH - (SCREEN_WIDTH // 4)
                x = random.randint(left_limit, right_limit - obstacle_width)
                obstacle_rect = pygame.Rect(x, -obstacle_height, obstacle_width, obstacle_height)
                obstacles.append({'rect': obstacle_rect, 'image': selected_image})
                last_spawn_time = current_time

            # Move obstacles
            for obj in obstacles[:]:
                obj['rect'].y += obstacle_speed
                if obj['rect'].top > SCREEN_HEIGHT:
                    obstacles.remove(obj)
                    score += 1

            # Increase speed
            if current_time - last_speed_increase > 10000:
                speed += 1
                obstacle_speed += 1
                last_speed_increase = current_time

            # Check collision
            for obj in obstacles:
                if vehicle_rect.colliderect(obj['rect']):
                    game_over = True
                    game_over_time = current_time

        # Draw
        screen.blit(scaled_background, (0, background_y - bg_height))
        screen.blit(scaled_background, (0, background_y))
        if not game_over:
            screen.blit(vehicle_image, vehicle_rect)
        for obj in obstacles:
            screen.blit(obj['image'], obj['rect'])
        
        score_text = font_small.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        if game_over:
            game_over_text = font_large.render("Game Over", True, BLACK)
            screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)))
            restart_text = font_small.render("Press R to restart", True, BLACK)
            screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)))

        pygame.display.flip()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())