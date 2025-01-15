import pygame
import random
import sys
import math

# Khởi tạo Pygame
pygame.init()

# Kích thước màn hình
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Màu sắc
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (92,179,56)
DARK_GRAY = (50, 50, 50)
SKY_BLUE = (135, 206, 235)

# Thiết lập màn hình
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racing Game - Rear View")
icon = pygame.image.load(r'assets/images/icon.png')
pygame.display.set_icon(icon)
# Tần số khung hình
clock = pygame.time.Clock()
FPS = 60
# Thêm biến trạng thái game và đếm ngược
COUNTDOWN = 3
game_state = "countdown"  # Các trạng thái: "countdown", "playing", "game_over"
countdown_timer = FPS * COUNTDOWN  # Số frame để đếm ngược (3 giây)
countdown_font = pygame.font.Font(None, 74)  # Font lớn hơn cho đếm ngược

# Kích thước và thông số đường đua
ROAD_TOP_WIDTH = 300
ROAD_BOTTOM_WIDTH = 600
HORIZON_Y = SCREEN_HEIGHT // 1.5
ROAD_LENGTH = 1000
STRIPE_SPACING = 50
road_offset = 0
road_speed = 5

# Điểm số
score = 0
font = pygame.font.Font(None, 36)

# Kích thước xe của người chơi
PLAYER_BASE_WIDTH = 90  # Giảm từ 120
PLAYER_BASE_HEIGHT = 75  # Giảm từ 100
player_x = SCREEN_WIDTH // 2
player_speed = 8

# Tải hình ảnh xe của người chơi
car_image = pygame.image.load(r'assets/images/car.jpg')
car_image = pygame.transform.scale(car_image, (PLAYER_BASE_WIDTH, PLAYER_BASE_HEIGHT))

# Vẽ xe của người chơi
def draw_player():
    screen.blit(car_image, (player_x - PLAYER_BASE_WIDTH // 2, SCREEN_HEIGHT - PLAYER_BASE_HEIGHT - 50))

# Tạo danh sách hình ảnh chướng ngại vật
obstacle_images = [
    pygame.image.load('assets/images/1.png'),
    pygame.image.load('assets/images/2.png'),
    pygame.image.load('assets/images/4.png'),
    pygame.image.load('assets/images/3.png')
]
# Lớp chướng ngại vật (Obstacle)
class Obstacle:
    def __init__(self, track_position):
        self.track_z = track_position
        possible_positions = [-0.4, -0.2, 0, 0.2, 0.4]  # Các làn trên đường
        self.x = random.choice(possible_positions)
        self.image = random.choice(obstacle_images)  # Chọn hình ảnh ngẫu nhiên từ danh sách
        self.width = 70  # Tăng kích thước chiều rộng
        self.height = 110  # Tăng kích thước chiều cao
        self.active = True


    def get_screen_position(self, road_offset):
        relative_z = 1 - ((self.track_z - road_offset) % ROAD_LENGTH / ROAD_LENGTH)
        if relative_z < -0.2 or relative_z > 1:  # Nếu không hiển thị trên màn hình
            return None

        perspective = relative_z
        screen_y = HORIZON_Y + (SCREEN_HEIGHT - HORIZON_Y) * (1 - relative_z)
        road_width = ROAD_TOP_WIDTH + (ROAD_BOTTOM_WIDTH - ROAD_TOP_WIDTH) * (1 - relative_z)
        screen_x = SCREEN_WIDTH // 2 + self.x * road_width

        width = self.width * (1 - perspective * 0.7)
        height = self.height * (1 - perspective * 0.7)

        return screen_x, screen_y, width, height, relative_z

    def draw(self, screen, road_offset):
        pos = self.get_screen_position(road_offset)
        if pos:
            screen_x, screen_y, width, height, _ = pos
            # Chỉnh kích thước hình ảnh theo tỷ lệ
            scaled_image = pygame.transform.scale(self.image, (int(width), int(height)))
            # Vẽ hình ảnh lên màn hình
            screen.blit(scaled_image, (screen_x - width / 2, screen_y - height))

# Tạo các vạch kẻ trên đường
def create_road_stripes():
    stripes = []
    for i in range(0, ROAD_LENGTH, STRIPE_SPACING * 5):  # Khoảng cách vạch lớn hơn
        stripes.append(i)
    return stripes

road_stripes = create_road_stripes()

#Vạch kẻ đường
def draw_road():
    pygame.draw.rect(screen, SKY_BLUE, (0, 0, SCREEN_WIDTH, HORIZON_Y))
    pygame.draw.rect(screen, GREEN, (0, HORIZON_Y, SCREEN_WIDTH, SCREEN_HEIGHT - HORIZON_Y))

    road_points = [
        (SCREEN_WIDTH // 2 - ROAD_BOTTOM_WIDTH // 2, SCREEN_HEIGHT),
        (SCREEN_WIDTH // 2 - ROAD_TOP_WIDTH // 3, HORIZON_Y),
        (SCREEN_WIDTH // 2 + ROAD_TOP_WIDTH // 3, HORIZON_Y),
        (SCREEN_WIDTH // 2 + ROAD_BOTTOM_WIDTH // 2, SCREEN_HEIGHT)
    ]
    pygame.draw.polygon(screen, GRAY, road_points)

    for stripe_pos in road_stripes:
        relative_pos = 1 - ((stripe_pos - road_offset) % ROAD_LENGTH / ROAD_LENGTH)
        if 0 <= relative_pos <= 1:
            y = HORIZON_Y + (SCREEN_HEIGHT - HORIZON_Y) * (1 - relative_pos)
            stripe_width = 5 + (1 - relative_pos) * 15
            stripe_length = 20 + (1 - relative_pos) * 40
            pygame.draw.rect(screen, WHITE, (
                SCREEN_WIDTH // 2 - stripe_width / 2,
                y - stripe_length / 2,
                stripe_width,
                stripe_length
            ))


# Tải hình ảnh cây
tree_image = pygame.image.load('assets/images/tree.png')

class Tree:
    def __init__(self, track_position, side):
        self.track_z = track_position
        self.side = side  # "left" hoặc "right"
        self.width = 200
        self.height = 400

    def get_screen_position(self, road_offset):
        relative_z = 1 - ((self.track_z - road_offset) % ROAD_LENGTH / ROAD_LENGTH)
        if relative_z < -0.5 or relative_z > 1.2:  # Cho phép cây biến mất chậm hơn
            return None

        perspective = relative_z
        screen_y = HORIZON_Y + (SCREEN_HEIGHT - HORIZON_Y) * (1 - relative_z) + self.height * (1 - perspective) * 0.2
        road_width = ROAD_TOP_WIDTH + (ROAD_BOTTOM_WIDTH - ROAD_TOP_WIDTH) * (1 - relative_z * 0.5)

        if self.side == "left":
            screen_x = SCREEN_WIDTH // 2 - road_width / 2 - self.width * (1 - perspective * 2) / 2
        else:
            screen_x = SCREEN_WIDTH // 2 + road_width / 2 + self.width * (1 - perspective * 2) / 2

        width = self.width * (1 - perspective * 0.7)
        height = self.height * (1 - perspective * 0.7)

        return screen_x, screen_y, width, height, relative_z


    def draw(self, screen, road_offset):
        pos = self.get_screen_position(road_offset)
        if pos:
            screen_x, screen_y, width, height, _ = pos
            tree_scaled = pygame.transform.scale(tree_image, (int(width), int(height)))
            screen.blit(tree_scaled, (screen_x - width / 2, screen_y - height))

# Tạo danh sách cây
def create_trees():
    trees = []
    for i in range(0, ROAD_LENGTH, STRIPE_SPACING * 5):  # Cây cách xa nhau hơn
        trees.append(Tree(i, "left"))
        trees.append(Tree(i, "right"))
    return trees

trees = create_trees()

# Hiển thị điểm số
def display_score():
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

# Danh sách chướng ngại vật ban đầu
obstacles = [
    Obstacle(i * (ROAD_LENGTH / 5)) for i in range(5)
]

# Cơ chế tăng độ khó
difficulty_timer = 0
obstacle_frequency = ROAD_LENGTH / 5

# Thêm hàm hiển thị đếm ngược
def display_countdown(count):
    text = countdown_font.render(str(count), True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

# Hàm kiểm tra và lưu điểm cao
def check_and_save_high_score(current_score):
    try:
        with open("score.txt", "r") as file:
            high_score = int(file.read().strip())
    except (FileNotFoundError, ValueError):
        high_score = 0

    if current_score > high_score:
        with open("score.txt", "w") as file:
            file.write(str(current_score))
        return True, current_score  # Trả về True nếu phá kỷ lục
    return False, high_score  # Trả về False nếu không phá kỷ lục

# Hiển thị thông báo "Bạn có muốn chơi lại không?"
def display_restart_message():
    font_restart = pygame.font.Font(None, 48)
    text = font_restart.render("Do you want to play again? (Y/N)", True, WHITE)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)

# Vòng lặp chính
running = True
new_high_score = False  # Cờ để kiểm tra có phá kỷ lục hay không

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "game_over":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    # Chơi lại
                    game_state = "countdown"
                    countdown_timer = FPS * COUNTDOWN
                    score = 0  # Reset điểm
                    obstacles = [
                        Obstacle(i * (ROAD_LENGTH / 5)) for i in range(5)
                    ]
                    road_offset = 0
                elif event.key == pygame.K_n:
                    # Thoát
                    running = False

    # Đếm ngược
    if game_state == "countdown":
        screen.fill(DARK_GRAY)
        seconds_left = countdown_timer // FPS + 1
        display_countdown(seconds_left)
        countdown_timer -= 1

        if countdown_timer < 0:
            game_state = "playing"

        pygame.display.flip()
        clock.tick(FPS)
        continue

    # Xử lý di chuyển xe
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > SCREEN_WIDTH // 2 - ROAD_BOTTOM_WIDTH // 2 + PLAYER_BASE_WIDTH // 2:
        player_x -= player_speed
    elif keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH // 2 + ROAD_BOTTOM_WIDTH // 2 - PLAYER_BASE_WIDTH // 2:
        player_x += player_speed

    # Cập nhật trạng thái đường
    road_offset = (road_offset - road_speed) % ROAD_LENGTH
    difficulty_timer += 1
    if difficulty_timer % (FPS * 10) == 0:
        road_speed += 1

    # Thêm chướng ngại vật
    if len(obstacles) < 5 or max(o.track_z for o in obstacles) < ROAD_LENGTH:
        new_pos = max(o.track_z for o in obstacles) + obstacle_frequency
        obstacles.append(Obstacle(new_pos))

    # Vẽ giao diện
    screen.fill(GREEN)
    draw_road()
    for tree in trees:
        tree.draw(screen, road_offset)  # Vẽ cây
    for obstacle in obstacles:
        obstacle.draw(screen, road_offset)

    draw_player()
    display_score()  # Hiển thị điểm hiện tại

    # Kiểm tra va chạm
    for obstacle in obstacles:
        pos = obstacle.get_screen_position(road_offset)
        if pos:
            screen_x, screen_y, width, height, _ = pos
            if player_x > screen_x - width // 2 and player_x < screen_x + width // 2 and SCREEN_HEIGHT - PLAYER_BASE_HEIGHT - 50 > screen_y - height:
                game_state = "game_over"
                high_score_broken, high_score = check_and_save_high_score(score)
                new_high_score = high_score_broken
    score = score +1

    # Hiển thị thông báo điểm cao
    if new_high_score:
        high_score_text = font.render(f"New High Score: {high_score}", True, GREEN)
        screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    if game_state == "game_over":
        display_restart_message()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
