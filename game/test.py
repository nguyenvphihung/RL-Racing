import pygame
import random
import sys

# Khởi tạo pygame
pygame.init()

# Kích thước màn hình
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Khởi tạo màn hình
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Đua Xe")

# Clock
clock = pygame.time.Clock()

# Lớp xe người chơi
class PlayerCar:
    def __init__(self):
        self.width = 50
        self.height = 80
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = 5

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

# Lớp chướng ngại vật
class Obstacle:
    def __init__(self):
        self.width = 50
        self.height = 80
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = 5

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

    def move(self):
        self.y += self.speed

# Hàm chính
def main():
    running = True
    player = PlayerCar()
    obstacles = []
    score = 0

    # Font
    font = pygame.font.SysFont(None, 36)

    while running:
        screen.fill(WHITE)

        # Kiểm tra sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Điều khiển xe người chơi
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Thêm chướng ngại vật
        if random.randint(1, 50) == 1:
            obstacles.append(Obstacle())

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