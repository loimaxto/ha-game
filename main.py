import pygame
import sys
import random
import time
import os

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
WIDTH, HEIGHT = 1440, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Thử Thách Xếp Chồng")

# Màu sắc
BACKGROUND = (255, 255, 255)  # Nền trắng
TEXT_COLOR = (40, 40, 40)
GRID_COLOR = (240, 240, 240)
TIMER_COLOR = (220, 80, 60)
GAME_OVER_COLOR = (200, 60, 60)
BUTTON_COLOR = (70, 180, 70)

# Tải hình ảnh
def load_image(name, width=None, height=None):
    try:
        image = pygame.image.load(name)
        if width and height:
            image = pygame.transform.scale(image, (width, height))
        elif width:
            # Giữ tỷ lệ nếu chỉ chỉ định chiều rộng
            ratio = width / image.get_width()
            height = int(image.get_height() * ratio)
            image = pygame.transform.scale(image, (width, height))
        elif height:
            # Giữ tỷ lệ nếu chỉ chỉ định chiều cao
            ratio = height / image.get_height()
            width = int(image.get_width() * ratio)
            image = pygame.transform.scale(image, (width, height))
        return image
    except pygame.error:
        print(f"Không thể tải hình ảnh: {name}")
        # Tạo hình ảnh thay thế nếu không tải được
        surf = pygame.Surface((width or 100, height or 100))
        surf.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
        return surf

# Tải hình ảnh cho catcher và vật thể rơi
# Lưu ý: Thay thế bằng đường dẫn hình ảnh thực tế của bạn
catcher_img = load_image("./assets/catcher.png", width=150)  # Điều chỉnh kích thước catcher
block_imgs = [
    load_image("./assets/item1.png", width=random.randint(40, 60)), 
    load_image("./assets/item2.png", width=random.randint(40, 60)),
    load_image("./assets/item3.png", width=random.randint(40, 60)),
]

# Nếu không có hình ảnh, sử dụng danh sách hình ảnh mặc định
if not os.path.exists("./assets/catcher.png"):
    print("Không tìm thấy hình ảnh catcher, sử dụng hình chữ nhật thay thế.")
    catcher_img = None
    block_imgs = [None] * 4

# Lớp Catcher
class Catcher:
    def __init__(self):
        # Kích thước catcher
        self.width = 150
        self.height = 40
        
        # Vị trí ban đầu
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 60
        self.speed = 20
        self.held_objects = []  # Danh sách các vật thể đã hứng được

    def draw(self):
        # Vẽ catcher bằng hình ảnh hoặc hình chữ nhật nếu không có ảnh
        if catcher_img:
            screen.blit(catcher_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (50, 150, 200), (self.x, self.y, self.width, self.height), border_radius=6)
            pygame.draw.rect(screen, (30, 100, 150), (self.x, self.y, self.width, self.height), 3, border_radius=6)
        
        # Vẽ các vật thể đang giữ (xếp chồng)
        for obj in self.held_objects:
            obj.draw()

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
            # Di chuyển tất cả vật thể cùng với catcher
            for obj in self.held_objects:
                obj.x -= self.speed
                
        if direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed
            # Di chuyển tất cả vật thể cùng với catcher
            for obj in self.held_objects:
                obj.x += self.speed

# Lớp FallingObject (các khối gạch)
class FallingObject:
    def __init__(self):
        # Chọn hình ảnh ngẫu nhiên hoặc tạo màu ngẫu nhiên
        self.img = random.choice(block_imgs) if block_imgs[0] else None
        
        # Kích thước ngẫu nhiên nếu không có hình ảnh
        if self.img:
            self.width = self.img.get_width()
            self.height = self.img.get_height()
        else:
            self.width = random.randint(20, 60)
            self.height = random.randint(20, 60)
        
        # Vị trí ban đầu
        self.x = random.randint(0, WIDTH - self.width)
        self.y = -self.height
        self.speed = random.uniform(4, 10)
        self.caught = False
        
        # Tạo màu ngẫu nhiên nếu không có hình ảnh
        if not self.img:
            self.color = (
                random.randint(50, 220),
                random.randint(50, 220),
                random.randint(50, 220)
            )
            self.border_color = (
                max(0, self.color[0]-40), 
                max(0, self.color[1]-40), 
                max(0, self.color[2]-40)
            )

    def move(self):
        if not self.caught:
            self.y += self.speed

    def draw(self):
        # Vẽ bằng hình ảnh hoặc hình chữ nhật nếu không có ảnh
        if self.img:
            screen.blit(self.img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, self.border_color, (self.x, self.y, self.width, self.height), 2)
            
            # Vẽ các đường gạch
            pygame.draw.line(screen, self.border_color, (self.x, self.y), (self.x + self.width, self.y), 2)
            for i in range(1, 4):
                y_pos = self.y + i * self.height // 4
                pygame.draw.line(screen, self.border_color, (self.x, y_pos), (self.x + self.width, y_pos), 1)

    def check_catch(self, catcher):
        if self.caught:
            return False
            
        # Kiểm tra va chạm với catcher
        catcher_rect = pygame.Rect(catcher.x, catcher.y, catcher.width, catcher.height)
        obj_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        if catcher_rect.colliderect(obj_rect):
            self.caught = True
            # Đặt vật thể ngay trên catcher tại vị trí chạm
            self.y = catcher.y - self.height
            catcher.held_objects.append(self)
            return True
            
        # Kiểm tra va chạm với các vật thể đã hứng
        for held_obj in catcher.held_objects:
            held_rect = pygame.Rect(held_obj.x, held_obj.y, held_obj.width, held_obj.height)
            
            # Kiểm tra va chạm từ phía trên
            if (self.y + self.height > held_obj.y and 
                self.y < held_obj.y and 
                self.x + self.width > held_obj.x and 
                self.x < held_obj.x + held_obj.width):
                
                self.caught = True
                # Đặt vật thể ngay trên vật thể đã hứng tại vị trí chạm
                self.y = held_obj.y - self.height
                catcher.held_objects.append(self)
                return True
                
        return False

# Khởi tạo game
def init_game():
    global catcher, falling_objects, blocks_caught, round_start_time, game_active, final_score
    catcher = Catcher()
    falling_objects = []
    blocks_caught = 0
    round_start_time = time.time()
    game_active = True
    final_score = 0

# Tạo các đối tượng game
catcher = Catcher()
falling_objects = []
blocks_caught = 0
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 28)
title_font = pygame.font.SysFont('Arial', 64, bold=True)

# Tạo sự kiện thêm vật thể mới
ADD_OBJECT = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_OBJECT, 700)  # Thêm vật thể mỗi 700ms

# Hệ thống tính điểm trong 15 giây
round_duration = 15  # 15 giây
game_active = False
final_score = 0
show_title = True
title_start_time = time.time()

# Vẽ lưới nền
def draw_grid():
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

# Vẽ thời gian còn lại (góc trên bên phải)
def draw_timer():
    elapsed_time = time.time() - round_start_time
    time_left = max(0, round_duration - elapsed_time)
    seconds = int(time_left)
    
    # Tạo văn bản với màu sắc thay đổi khi thời gian ít
    color = TIMER_COLOR if seconds <= 5 else TEXT_COLOR
    timer_text = font.render(f"Thời gian: {seconds}s", True, color)
    
    # Vẽ ở góc trên bên phải
    screen.blit(timer_text, (WIDTH - timer_text.get_width() - 20, 20))

# Vẽ nút chơi lại
def draw_restart_button():
    button_width, button_height = 200, 60
    button_x = WIDTH // 2 - button_width // 2
    button_y = HEIGHT // 2 + 50
    
    # Vẽ nút
    pygame.draw.rect(screen, BUTTON_COLOR, (button_x, button_y, button_width, button_height), border_radius=10)
    pygame.draw.rect(screen, (40, 120, 40), (button_x, button_y, button_width, button_height), 3, border_radius=10)
    
    # Vẽ văn bản
    restart_text = font.render("Nhấn R", True, (255, 255, 255))
    screen.blit(restart_text, (button_x + button_width//2 - restart_text.get_width()//2, 
                              button_y + button_height//2 - restart_text.get_height()//2))
    
    return pygame.Rect(button_x, button_y, button_width, button_height)

# Vẽ màn hình tiêu đề
def draw_title_screen():
    # Vẽ tiêu đề
    title_text = title_font.render("THỬ THÁCH XẾP CHỒNG", True, (60, 100, 180))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4 - 50))
    
    # Vẽ hướng dẫn
    subtitle = font.render("Hứng và xếp các khối rơi trong 15 giây!", True, TEXT_COLOR)
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//4 + 50))
    
    # Vẽ điều khiển
    controls = [
        "ĐIỀU KHIỂN:",
        "- Dùng phím MŨI TÊN TRÁI/PHẢI hoặc A/D để di chuyển",
        "- Xếp các khối để ghi điểm",
        "- Hứng càng nhiều càng tốt trong 15 giây!"
    ]
    
    for i, text in enumerate(controls):
        text_surf = small_font.render(text, True, TEXT_COLOR)
        screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2 + 20 + i*40))
    
    # Vẽ nút bắt đầu
    start_button = draw_restart_button()
    start_text = font.render("Nhấn PHÍM CÁCH để bắt đầu", True, (255, 255, 255))
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 
                           start_button.y + start_button.height//2 - start_text.get_height()//2))
    
    return start_button

# Vẽ màn hình kết thúc
def draw_game_over():
    # Vẽ kết quả
    result_text = title_font.render("KẾT THÚC", True, GAME_OVER_COLOR)
    screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//4 - 50))
    
    score_text = font.render(f"Bạn đã hứng được {final_score} khối!", True, TEXT_COLOR)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//4 + 50))
    
    # Vẽ hướng dẫn chơi lại
    restart_text = font.render("Nhấn R để chơi lại", True, TEXT_COLOR)
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//4 + 120))
    
    # Vẽ nút chơi lại
    button_rect = draw_restart_button()
    return button_rect

# Khởi tạo game lần đầu
init_game()
game_active = False
show_title = True

# Vòng lặp game chính
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Thêm vật thể mới
        if event.type == ADD_OBJECT and game_active:
            falling_objects.append(FallingObject())
            
        # Xử lý sự kiện bàn phím
        if event.type == pygame.KEYDOWN:
            # Bắt đầu game từ màn hình tiêu đề
            if show_title and event.key == pygame.K_SPACE:
                show_title = False
                game_active = True
                round_start_time = time.time()
            
            # Chơi lại từ màn hình kết thúc
            if not game_active and not show_title and event.key == pygame.K_r:
                init_game()
        
        # Xử lý sự kiện chuột
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Kiểm tra nút trên màn hình tiêu đề
            if show_title:
                start_button = draw_title_screen()
                if start_button.collidepoint(mouse_pos):
                    show_title = False
                    game_active = True
                    round_start_time = time.time()
            
            # Kiểm tra nút trên màn hình kết thúc
            elif not game_active:
                restart_button = draw_game_over()
                if restart_button.collidepoint(mouse_pos):
                    init_game()

    # Kiểm tra thời gian vòng chơi
    if game_active:
        elapsed_time = time.time() - round_start_time
        if elapsed_time >= round_duration:
            game_active = False
            final_score = blocks_caught

    # Xử lý di chuyển
    if game_active:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            catcher.move("left")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            catcher.move("right")

    # Di chuyển và kiểm tra vật thể
    for obj in falling_objects[:]:
        if game_active:
            obj.move()
        
        # Kiểm tra hứng vật thể
        if obj.check_catch(catcher) and game_active:
            blocks_caught += 1
            falling_objects.remove(obj)
        
        # Kiểm tra rơi ra ngoài màn hình
        elif obj.y > HEIGHT + obj.height:
            falling_objects.remove(obj)

    # Vẽ nền
    screen.fill(BACKGROUND)
    draw_grid()
    
    # Vẽ các vật thể đang rơi
    for obj in falling_objects:
        obj.draw()
    
    # Vẽ catcher và vật thể đã hứng
    if not show_title:
        catcher.draw()
    
    # Vẽ giao diện người dùng
    if show_title:
        # Màn hình tiêu đề
        draw_title_screen()
    elif game_active:
        # Vẽ điểm số (góc trên bên trái)
        score_text = font.render(f"Khối: {blocks_caught}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        
        # Vẽ thời gian (góc trên bên phải)
        draw_timer()
        
        # Vẽ hướng dẫn (giữa màn hình)
        help_text = small_font.render("Dùng MŨI TÊN TRÁI/PHẢI hoặc A/D để di chuyển", True, TEXT_COLOR)
        screen.blit(help_text, (WIDTH//2 - help_text.get_width()//2, 60))
    else:
        # Màn hình kết thúc
        draw_game_over()
        
        # Hiển thị điểm số cuối cùng
        final_text = font.render(f"Điểm số: {final_score}", True, TEXT_COLOR)
        screen.blit(final_text, (WIDTH//2 - final_text.get_width()//2, HEIGHT//4 + 90))
    
    # Cập nhật màn hình
    pygame.display.flip()
    clock.tick(60)