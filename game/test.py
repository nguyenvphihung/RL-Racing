import pygame
import random
import sys
import os

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)

# Khởi tạo màn hình
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Đua Xe")

# Clock
clock = pygame.time.Clock()

# Lớp xe người chơi
class PlayerCar:
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 120))
        self.width = 80
        self.height = 100
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 50
        self.speed = 5
        self.lane = 1  # Làn giữa

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def move(self, keys):
        # Di chuyển ngang giữa các làn
        if keys[pygame.K_LEFT] and self.x > 100:  # Giới hạn di chuyển trong làn đường
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width - 50:  # Giới hạn di chuyển trong làn đường
            self.x += self.speed
        
        # Di chuyển lên xuống
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed

# Lớp chướng ngại vật
class Obstacle:
    global LANE_WIDTH
    LANE_WIDTH = 130  # Độ rộng của mỗi làn đường
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (80, 120))
        self.width = 80
        self.height = 120
        self.lane = random.randint(0, 2)
        self.x = 100 + self.lane * LANE_WIDTH
        self.y = -self.height
        self.speed = 5

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        self.y += self.speed

# Vẽ đường
def draw_road():
    global road_offset
    
    # Vẽ lề đường (đối xứng)
    pygame.draw.rect(screen, GREEN, (0, 0, 100, SCREEN_HEIGHT))
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 100, 0, 100, SCREEN_HEIGHT))
    
    # Vẽ đường
    pygame.draw.rect(screen, GRAY, (100, 0, SCREEN_WIDTH - 200, SCREEN_HEIGHT))
    
    # Vẽ vạch kẻ đường đứt đoạn với hiệu ứng di chuyển
    for lane in range(1, 3):
        x = 100 + lane * LANE_WIDTH
        for y in range(-50, SCREEN_HEIGHT, 100):
            # Vẽ đoạn đường ngắn với hiệu ứng di chuyển
            pygame.draw.line(screen, YELLOW, 
                             (x, y + road_offset), 
                             (x, y + 50 + road_offset), 5)
    
    # Cập nhật offset để tạo hiệu ứng chuyển động
    road_offset = (road_offset + 5) % 100

# Trong hàm main(), thêm dòng khởi tạo global
road_offset = 0

# Hàm chính
def main():
    

    running = True
    player = PlayerCar('assets/images/car.png')
    obstacles = []
    score = 0

    # Font
    font = pygame.font.SysFont(None, 36)

    while running:
        # Vẽ đường
        screen.fill(WHITE)
        draw_road()

        # Kiểm tra sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Điều khiển xe người chơi
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Thêm chướng ngại vật
        if random.randint(1, 50) == 1:
            obstacles.append(Obstacle('assets/images/1.png'))
            # obstacles.append(Obstacle('assets/images/2.png'))
            # obstacles.append(Obstacle('assets/images/3.png'))
            # obstacles.append(Obstacle('assets/images/4.png'))

        # Di chuyển và vẽ chướng ngại vật
        for obstacle in obstacles[:]:
            obstacle.move()
            obstacle.draw()

            # Xóa chướng ngại vật khi ra khỏi màn hình
            if obstacle.y > SCREEN_HEIGHT:
                obstacles.remove(obstacle)
                score += 1

            # Kiểm tra va chạm
            if (player.x < obstacle.x + obstacle.width and
                player.x + player.width > obstacle.x and
                player.y < obstacle.y + obstacle.height and
                player.y + player.height > obstacle.y):
                running = False

        # Vẽ xe người chơi
        player.draw()

        # Hiển thị điểm
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Cập nhật màn hình
        pygame.display.flip()

        # Tốc độ khung hình
        clock.tick(60)

    # Kết thúc game
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()