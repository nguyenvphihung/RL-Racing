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
GREEN = (0, 255, 0)
DARK_GRAY = (50, 50, 50)
SKY_BLUE = (135, 206, 235)

# Thiết lập màn hình
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racing Game - Rear View")

# Tần số khung hình
clock = pygame.time.Clock()
FPS = 60

# Kích thước xe của người chơi
PLAYER_BASE_WIDTH = 120
PLAYER_BASE_HEIGHT = 100
player_x = SCREEN_WIDTH // 2
player_speed = 8

# Kích thước và thông số đường đua
ROAD_TOP_WIDTH = 300
ROAD_BOTTOM_WIDTH = 600
HORIZON_Y = SCREEN_HEIGHT // 3
ROAD_LENGTH = 1000
STRIPE_SPACING = 50
road_offset = 0
road_speed = 5

# Điểm số
score = 0
font = pygame.font.Font(None, 36)

# Tải hình ảnh xe của người chơi
car_image = pygame.image.load(r'D:\Racing AI\RL-Racing\assets\images\car.jpg')
car_image = pygame.transform.scale(car_image, (PLAYER_BASE_WIDTH, PLAYER_BASE_HEIGHT))

# Lớp chướng ngại vật (Obstacle)
class Obstacle:
    def __init__(self, track_position):
        self.track_z = track_position
        self.x = random.uniform(-0.4, 0.4)
        self.width = 40
        self.height = 60
        self.active = True

    # Tính toán vị trí trên màn hình của chướng ngại vật
    def get_screen_position(self, road_offset):
        relative_z = 1 - ((self.track_z - road_offset) % ROAD_LENGTH / ROAD_LENGTH)
        if relative_z < -0.2 or relative_z > 1:  # Nếu vượt khỏi màn hình (không hiển thị)
            return None

        perspective = relative_z
        screen_y = HORIZON_Y + (SCREEN_HEIGHT - HORIZON_Y) * (1 - relative_z)
        road_width = ROAD_TOP_WIDTH + (ROAD_BOTTOM_WIDTH - ROAD_TOP_WIDTH) * (1 - relative_z)
        screen_x = SCREEN_WIDTH // 2 + self.x * road_width

        width = self.width * (1 - perspective * 0.7)
        height = self.height * (1 - perspective * 0.7)

        return screen_x, screen_y, width, height, relative_z

    # Vẽ chướng ngại vật trên màn hình
    def draw(self, screen, road_offset):
        pos = self.get_screen_position(road_offset)
        if pos:
            screen_x, screen_y, width, height, _ = pos
            pygame.draw.rect(screen, RED, (
                screen_x - width / 2,
                screen_y - height,
                width,
                height
            ))

# Tạo các vạch kẻ trên đường
def create_road_stripes():
    stripes = []
    for i in range(0, ROAD_LENGTH, STRIPE_SPACING * 5):  # Khoảng cách vạch lớn hơn
        stripes.append(i)
    return stripes

road_stripes = create_road_stripes()

#Vạch kẻ đường
def draw_road():
    # Vẽ bầu trời
    pygame.draw.rect(screen, SKY_BLUE, (0, 0, SCREEN_WIDTH, HORIZON_Y))
    # Vẽ bãi cỏ
    pygame.draw.rect(screen, GREEN, (0, HORIZON_Y, SCREEN_WIDTH, SCREEN_HEIGHT - HORIZON_Y))

    # Vẽ đường
    road_points = [
        (SCREEN_WIDTH // 2 - ROAD_BOTTOM_WIDTH // 2, SCREEN_HEIGHT),
        (SCREEN_WIDTH // 2 - ROAD_TOP_WIDTH // 2, HORIZON_Y),
        (SCREEN_WIDTH // 2 + ROAD_TOP_WIDTH // 2, HORIZON_Y),
        (SCREEN_WIDTH // 2 + ROAD_BOTTOM_WIDTH // 2, SCREEN_HEIGHT)
    ]
    pygame.draw.polygon(screen, GRAY, road_points)

    # Vẽ vạch kẻ giữa đường
    for stripe_pos in road_stripes:
        relative_pos = 1 - ((stripe_pos - road_offset) % ROAD_LENGTH / ROAD_LENGTH)
        if 0 <= relative_pos <= 1:
            y = HORIZON_Y + (SCREEN_HEIGHT - HORIZON_Y) * (1 - relative_pos)
            stripe_width = 10 + (1 - relative_pos) * 20  # Tính chiều rộng
            stripe_length = 30 + (1 - relative_pos) * 50  # Tính chiều dài

            pygame.draw.rect(screen, WHITE, (
                SCREEN_WIDTH // 2 - stripe_width / 2,
                y - stripe_length / 2,
                stripe_width,
                stripe_length
            ))

# Tải hình ảnh cây
tree_image = pygame.image.load(r'D:\Racing AI\RL-Racing\assets\images\tree.png')

# Tạo lớp cây (Tree)
class Tree:
    def __init__(self, track_position, side):
        self.track_z = track_position
        self.side = side  # "left" hoặc "right"
        self.width = 200
        self.height = 400

    def get_screen_position(self, road_offset):
        relative_z = 1 - ((self.track_z - road_offset) % ROAD_LENGTH / ROAD_LENGTH)
        if relative_z < -0.2 or relative_z > 1:  # Nếu vượt khỏi màn hình
            return None

        perspective = relative_z
        screen_y = HORIZON_Y + (SCREEN_HEIGHT - HORIZON_Y) * (1 - relative_z)
        road_width = ROAD_TOP_WIDTH + (ROAD_BOTTOM_WIDTH - ROAD_TOP_WIDTH) * (1 - relative_z)

        if self.side == "left":
            screen_x = SCREEN_WIDTH // 2 - road_width / 2 - 50
        else:
            screen_x = SCREEN_WIDTH // 2 + road_width / 2 + 50

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

# Vẽ xe của người chơi
def draw_player():
    screen.blit(car_image, (player_x - PLAYER_BASE_WIDTH // 2, SCREEN_HEIGHT - PLAYER_BASE_HEIGHT - 50))

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
# Biến trạng thái màn chơi
current_level = 1
level_2_score = 2000
level_3_score = 3000
final_score = 5000
transition_message = ""

# Hàm hiển thị thông báo
def display_message(message, duration=3):
    global transition_message
    transition_message = message
    pygame.display.flip()
    pygame.time.wait(duration * 1000)
    transition_message = ""

# Vòng lặp chính của trò chơi
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Xử lý di chuyển xe
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > SCREEN_WIDTH // 2 - ROAD_BOTTOM_WIDTH // 2 + PLAYER_BASE_WIDTH // 2:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH // 2 + ROAD_BOTTOM_WIDTH // 2 - PLAYER_BASE_WIDTH // 2:
        player_x += player_speed


    # Cập nhật trạng thái đường và độ khó
    road_offset = (road_offset - road_speed) % ROAD_LENGTH
    difficulty_timer += 1
    if difficulty_timer % (FPS * 10) == 0:
        road_speed += 1
        obstacle_frequency *= 0.9
        if obstacle_frequency < 50:
            obstacle_frequency = 50

    # Thêm chướng ngại vật
    if len(obstacles) < 5 or max(o.track_z for o in obstacles) < ROAD_LENGTH:
        new_pos = max(o.track_z for o in obstacles) + obstacle_frequency
        obstacles.append(Obstacle(new_pos))

    obstacles = [obs for obs in obstacles if obs.active]

    # Vẽ giao diện
    screen.fill(GREEN)
    draw_road()
    for tree in trees:
        tree.draw(screen, road_offset)  # Vẽ cây
    for obstacle in obstacles:
        obstacle.draw(screen, road_offset)

    draw_player()
    display_score()

    # Kiểm tra va chạm
    for obstacle in obstacles:
        pos = obstacle.get_screen_position(road_offset)
        if pos:
            screen_x, screen_y, width, height, relative_z = pos
            if relative_z < 0.2:
                if abs(screen_x - player_x) < (PLAYER_BASE_WIDTH + width) // 3:
                    print(f"Game Over! Final Score: {score}")
                    pygame.quit()
                    sys.exit()

    # Cập nhật điểm và kiểm tra chuyển màn
    score += 1
    if current_level == 1 and score >= level_2_score:
        display_message("Chúc mừng! Bạn đã hoàn thành màn 1. Đến màn 2!")
        current_level = 2
        score = 0
        road_speed = 5  # Reset tốc độ

    elif current_level == 2 and score >= level_3_score:
        display_message("Tuyệt vời! Bạn đã vào màn cuối cùng!")
        current_level = 3
        score = 0
        road_speed = 5

    elif current_level == 3 and score >= final_score:
        display_message("Chúc mừng! Bạn đã phá đảo trò chơi!")
        pygame.quit()
        sys.exit()

    # Hiển thị thông báo màn chơi (nếu có)
    if transition_message:
        message_surface = font.render(transition_message, True, WHITE)
        screen.blit(message_surface, (SCREEN_WIDTH // 2 - message_surface.get_width() // 2, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
