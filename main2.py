import pygame
import random
import sys
import asyncio
import platform

# Khởi tạo Pygame
pygame.init()

# Thiết lập màn hình
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Trò chơi Né Vật Cản")

# Màu sắc
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BACKGROUND_COLOR = (200, 230, 255)

# Giới hạn di chuyển của xe
left_limit = 100
right_limit = 700

# Tải tài nguyên
def load_images(path, num):
    try:
        images = [pygame.image.load(f'{path}{i+1}.png').convert_alpha() for i in range(num)]
        # Điều chỉnh kích thước vật cản
        return [pygame.transform.scale(img, (30, 30)) for img in images]
    except pygame.error:
        print(f"Không thể tải hình ảnh từ {path}. Sử dụng hình chữ nhật thay thế.")
        surface = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(surface, BLACK, (0, 0, 30, 30))
        pygame.draw.rect(surface, GREEN, (0, 0, 30, 30), 2)
        return [surface for _ in range(num)]

try:
    vehicles = pygame.image.load('./assets/catcher.png').convert_alpha()
    vehicles = pygame.transform.scale(vehicles, (50, 100))  # Điều chỉnh kích thước xe
except pygame.error:
    print("Không thể tải hình xe. Sử dụng hình chữ nhật thay thế.")
    vehicles = pygame.Surface((50, 100), pygame.SRCALPHA)
    pygame.draw.rect(vehicles, BLACK, (0, 0, 50, 100))
    pygame.draw.rect(vehicles, RED, (0, 0, 50, 100), 2)

obstacles_types = load_images('./assets/obstacles/item', 3)
try:
    background = pygame.image.load('./assets/background.png').convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, background.get_height()))
except pygame.error:
    print("Không thể tải hình nền. Sử dụng màu nền dự phòng.")
    background = None

# Biến trò chơi
vehicle_image = None
obstacle_image = None
vehicle_rect = None
obstacles = []
background_y = 0
speed = 5
last_spawn_time = 0
last_speed_increase = 0
score = 0
game_over = False
game_over_time = 0
clock = pygame.time.Clock()
FPS = 60

# Font
font_small = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 74)

# Chọn vật cản
def select_obstacle():
    screen.fill(BACKGROUND_COLOR)
    text = font_small.render("Chọn vật cản: 1. Obstacle1 2. Obstacle2 3. Obstacle3", True, BLACK)
    screen.blit(text, (100, 100))
    for i, obstacle in enumerate(obstacles_types):
        screen.blit(obstacle, (100 + i * 100, 150))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 0
                elif event.key == pygame.K_2:
                    return 1
                elif event.key == pygame.K_3:
                    return 2

def setup(selected_obstacle_idx):
    global vehicle_rect, obstacles, background_y, speed, score, game_over, last_spawn_time, last_speed_increase, vehicle_image, obstacle_image
    vehicle_image = vehicles
    obstacle_image = obstacles_types[selected_obstacle_idx]
    vehicle_rect = vehicle_image.get_rect()
    vehicle_rect.bottom = SCREEN_HEIGHT - 10
    vehicle_rect.centerx = SCREEN_WIDTH // 2
    obstacles = []
    background_y = 0
    speed = 5
    score = 0
    game_over = False
    last_spawn_time = pygame.time.get_ticks()
    last_speed_increase = pygame.time.get_ticks()

async def main():
    global vehicle_rect, obstacles, background_y, speed, score, game_over, game_over_time, last_spawn_time, last_speed_increase
    selected_obstacle_idx = select_obstacle()
    setup(selected_obstacle_idx)

    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if game_over and current_time - game_over_time > 3000 and event.key == pygame.K_r:
                    setup(selected_obstacle_idx)

        if not game_over:
            # Di chuyển xe với giới hạn mới
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and vehicle_rect.left > left_limit:
                vehicle_rect.x -= 5
            if keys[pygame.K_RIGHT] and vehicle_rect.right < right_limit:
                vehicle_rect.x += 5

            # Spawn vật cản
            if current_time - last_spawn_time > 1500:
                x = random.randint(left_limit, right_limit - obstacle_image.get_width())
                obstacle_rect = pygame.Rect(x, -obstacle_image.get_height(), obstacle_image.get_width(), obstacle_image.get_height())
                obstacles.append({'rect': obstacle_rect, 'image': obstacle_image})
                last_spawn_time = current_time

            # Di chuyển vật cản
            for obj in obstacles:
                obj['rect'].y += speed

            # Xóa vật cản ra khỏi màn hình
            obstacles = [obj for obj in obstacles if obj['rect'].top < SCREEN_HEIGHT]

            # Kiểm tra va chạm
            for obj in obstacles:
                if vehicle_rect.colliderect(obj['rect']):
                    game_over = True
                    game_over_time = current_time

            # Tăng tốc độ
            if current_time - last_speed_increase > 10000:
                speed += 1
                last_speed_increase = current_time

            # Cập nhật điểm số
            score += 1

            # Di chuyển nền
            background_y += speed
            if background_y >= background.get_height():
                background_y -= background.get_height()

        # Vẽ
        if background:
            screen.blit(background, (0, background_y))
            screen.blit(background, (0, background_y - background.get_height()))
        else:
            screen.fill(BACKGROUND_COLOR)

        for obj in obstacles:
            screen.blit(obj['image'], obj['rect'])

        screen.blit(vehicle_image, vehicle_rect)

        score_text = font_small.render(f"Điểm: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        if game_over:
            game_over_text = font_large.render("Game Over! Nhấn R để chơi lại", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(game_over_text, text_rect)

        pygame.display.flip()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())