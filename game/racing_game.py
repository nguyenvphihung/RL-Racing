import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GRAY = (50, 50, 50)
SKY_BLUE = (135, 206, 235)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racing Game - Rear View")

# Frame rate
clock = pygame.time.Clock()
FPS = 60

# Player car dimensions
PLAYER_BASE_WIDTH = 80
PLAYER_BASE_HEIGHT = 70
player_x = SCREEN_WIDTH // 2
player_speed = 8

# Road dimensions
ROAD_TOP_WIDTH = 300
ROAD_BOTTOM_WIDTH = 600
HORIZON_Y = SCREEN_HEIGHT // 3
ROAD_LENGTH = 1000
STRIPE_SPACING = 50
road_offset = 0
road_speed = 5  # Tốc độ vẫn dương nhưng logic sẽ đảo ngược

# Score
score = 0
font = pygame.font.Font(None, 36)

# Load player car image
car_image = pygame.image.load('assets/images/car.jpg')
car_image = pygame.transform.scale(car_image, (PLAYER_BASE_WIDTH, PLAYER_BASE_HEIGHT))

# Obstacle class
class Obstacle:
    def __init__(self, track_position):
        self.track_z = track_position
        self.x = random.uniform(-0.4, 0.4)
        self.width = 40
        self.height = 60
        self.active = True

    def get_screen_position(self, road_offset):
        # Reverse the relative_z calculation
        relative_z = 1 - ((self.track_z - road_offset) % ROAD_LENGTH / ROAD_LENGTH)
        if relative_z < 0 or relative_z > 1:
            return None
        
        # Use the reversed relative_z to calculate position
        perspective = relative_z  # Reverse perspective
        screen_y = HORIZON_Y + (SCREEN_HEIGHT - HORIZON_Y) * (1 - relative_z)  # Reverse Y position
        road_width = ROAD_TOP_WIDTH + (ROAD_BOTTOM_WIDTH - ROAD_TOP_WIDTH) * (1 - relative_z)
        screen_x = SCREEN_WIDTH // 2 + self.x * road_width
        
        width = self.width * (1 - perspective * 0.7)  # Adjust scale
        height = self.height * (1 - perspective * 0.7)
        
        return screen_x, screen_y, width, height, relative_z

    def draw(self, screen, road_offset):
        pos = self.get_screen_position(road_offset)
        if pos:
            screen_x, screen_y, width, height, _ = pos
            pygame.draw.rect(screen, RED, (
                screen_x - width/2,
                screen_y - height,
                width,
                height
            ))

def create_road_stripes():
    stripes = []
    for i in range(0, ROAD_LENGTH, STRIPE_SPACING):
        stripes.append(i)
    return stripes

road_stripes = create_road_stripes()

def draw_road():
    # Draw sky
    pygame.draw.rect(screen, SKY_BLUE, (0, 0, SCREEN_WIDTH, HORIZON_Y))
    
    # Draw grass
    pygame.draw.rect(screen, GREEN, (0, HORIZON_Y, SCREEN_WIDTH, SCREEN_HEIGHT - HORIZON_Y))
    
    # Draw road
    road_points = [
        (SCREEN_WIDTH // 2 - ROAD_BOTTOM_WIDTH // 2, SCREEN_HEIGHT),
        (SCREEN_WIDTH // 2 - ROAD_TOP_WIDTH // 2, HORIZON_Y),
        (SCREEN_WIDTH // 2 + ROAD_TOP_WIDTH // 2, HORIZON_Y),
        (SCREEN_WIDTH // 2 + ROAD_BOTTOM_WIDTH // 2, SCREEN_HEIGHT)
    ]
    pygame.draw.polygon(screen, GRAY, road_points)
    
    # Draw road stripes with reversed movement direction
    for stripe_pos in road_stripes:
        relative_pos = 1 - ((stripe_pos - road_offset) % ROAD_LENGTH / ROAD_LENGTH)
        if 0 <= relative_pos <= 1:
            y = HORIZON_Y + (SCREEN_HEIGHT - HORIZON_Y) * (1 - relative_pos)
            width = ROAD_TOP_WIDTH + (ROAD_BOTTOM_WIDTH - ROAD_TOP_WIDTH) * (1 - relative_pos)
            stripe_width = 10 + (1 - relative_pos) * 20
            pygame.draw.rect(screen, WHITE, (
                SCREEN_WIDTH // 2 - stripe_width/2,
                y - 5,
                stripe_width,
                10
            ))

def draw_player():
    # Draw player car image
    screen.blit(car_image, (player_x - PLAYER_BASE_WIDTH//2, SCREEN_HEIGHT - PLAYER_BASE_HEIGHT - 50))

def display_score():
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

# Initial obstacles
obstacles = [
    Obstacle(i * (ROAD_LENGTH / 5)) for i in range(5)
]

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move player car
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > SCREEN_WIDTH//2 - ROAD_BOTTOM_WIDTH//2 + PLAYER_BASE_WIDTH//2:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH//2 + ROAD_BOTTOM_WIDTH//2 - PLAYER_BASE_WIDTH//2:
        player_x += player_speed

    # Update road position (reversed direction)
    road_offset = (road_offset - road_speed) % ROAD_LENGTH

    # Draw game
    screen.fill(GREEN)
    draw_road()
    
    # Draw and check collision with obstacles
    for obstacle in obstacles:
        pos = obstacle.get_screen_position(road_offset)
        if pos:
            screen_x, screen_y, width, height, relative_z = pos
            obstacle.draw(screen, road_offset)
            
            # Check collision when obstacle is close
            if relative_z < 0.2:  # Reverse collision condition
                if abs(screen_x - player_x) < (PLAYER_BASE_WIDTH + width) // 3:
                    print(f"Game Over! Final Score: {score}")
                    pygame.quit()
                    sys.exit()

    # Create new obstacles when needed
    if len(obstacles) < 5:
        new_pos = max(o.track_z for o in obstacles) + ROAD_LENGTH/5
        obstacles.append(Obstacle(new_pos))

    # Remove past obstacles
    obstacles = [obs for obs in obstacles if obs.active]
    
    draw_player()
    
    score += 1
    display_score()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
