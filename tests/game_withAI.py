import pygame, sys, random
import numpy as np
from collections import defaultdict
from pygame.locals import *
import json
import os

# Game Constants
WINDOWWIDTH = 400
WINDOWHEIGHT = 600
X_MARGIN = 80
LANEWIDTH = 60
CARWIDTH = 40
CARHEIGHT = 60
CARSPEED = 7
DISTANCE = 200
OBSTACLESSPEED = 1
CHANGESPEED = 0.0005
BGSPEED = 2
FPS = 60

# File lưu kết quả học
MODEL_FILE = 'q_table.json'

# Pygame Initialization
pygame.init()
fpsClock = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('AI RACING')

icon = pygame.image.load('assets/images/icon.png')
pygame.display.set_icon(icon)

# Load Images
CARIMG = pygame.image.load('assets/images/car.png')
OBSTACLESIMG = pygame.image.load('assets/images/obstacles.png')
BGIMG = pygame.image.load('assets/images/background.png')

class CarAIAgent:
    def __init__(self, action_space=2, learning_rate=0.1, discount_factor=0.95, epsilon=1.0, epsilon_decay=0.995):
        self.action_space = action_space
        self.q_table = defaultdict(lambda: np.zeros(action_space))
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.total_reward = 0
        self.episode_reward = 0
        self.load_model()

    def get_state(self, car, obstacles):
        """Convert game state to a discrete state representation"""
        car_x = int(car.x)
        car_y = int(car.y)
        
        # Find closest obstacle
        closest_obstacle = None
        min_distance = float('inf')
        
        for obstacle in obstacles.ls:
            obstacle_x = int(X_MARGIN + obstacle[0]*LANEWIDTH + (LANEWIDTH-CARWIDTH)/2)
            obstacle_y = int(obstacle[1])
            
            distance = ((car_x - obstacle_x)**2 + (car_y - obstacle_y)**2)**0.5
            if distance < min_distance:
                min_distance = distance
                closest_obstacle = (obstacle_x, obstacle_y)
        
        if closest_obstacle:
            # Discretize distances into bins
            dx = (closest_obstacle[0] - car_x) // 20
            dy = (closest_obstacle[1] - car_y) // 20
            
            # Add car's lane position
            car_lane = (car_x - X_MARGIN) // LANEWIDTH
            
            return (dx, dy, car_lane)
        return (0, 0, 0)
    
    def get_action(self, state):
        """Choose action using epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.action_space)
        else:
            return np.argmax(self.q_table[state])
    
    def update(self, state, action, reward, next_state):
        """Update Q-table using Q-learning formula"""
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        
        new_value = (1 - self.lr) * old_value + self.lr * (reward + self.gamma * next_max)
        self.q_table[state][action] = new_value
        
        self.episode_reward += reward

    def get_movement_from_action(self, action):
        """Convert action index to movement commands (chỉ di chuyển sang trái/phải)"""
        moveLeft = False
        moveRight = False
        
        if action == 0:  # Left
            moveLeft = True
        elif action == 1:  # Right
            moveRight = True
            
        return moveLeft, moveRight

    def save_model(self):
        """Save the Q-table and epsilon value into a JSON file"""
        serializable_q = {str(k): v.tolist() for k, v in self.q_table.items()}
        model_data = {
            'q_table': serializable_q,
            'epsilon': self.epsilon
        }
        with open(MODEL_FILE, 'w') as f:
            json.dump(model_data, f)

    def load_model(self):
        """Load the Q-table and epsilon value from a JSON file if exists"""
        if os.path.exists(MODEL_FILE):
            try:
                with open(MODEL_FILE, 'r') as f:
                    model_data = json.load(f)
                q_table_loaded = {}
                for key, value in model_data.get('q_table', {}).items():
                    # Convert string representation of tuple back to tuple
                    state = eval(key)
                    q_table_loaded[state] = np.array(value)
                self.q_table = defaultdict(lambda: np.zeros(self.action_space), q_table_loaded)
                self.epsilon = model_data.get('epsilon', self.epsilon)
            except Exception as e:
                print("Error loading model:", e)
                # Nếu có lỗi, reset Q-table
                self.q_table = defaultdict(lambda: np.zeros(self.action_space))
        else:
            # Không có file lưu, giữ nguyên giá trị khởi tạo
            pass

class Background:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = BGSPEED
        self.img = BGIMG
        self.width = self.img.get_width()
        self.height = self.img.get_height()
    def draw(self):
        DISPLAYSURF.blit(self.img, (int(self.x), int(self.y)))
        DISPLAYSURF.blit(self.img, (int(self.x), int(self.y - self.height)))
    def update(self):
        self.y += self.speed
        if self.y > self.height:
            self.y -= self.height

class Obstacles:
    def __init__(self):
        self.width = CARWIDTH
        self.height = CARHEIGHT
        self.distance = DISTANCE
        self.speed = OBSTACLESSPEED
        self.changeSpeed = CHANGESPEED
        self.ls = []
        for i in range(5):
            y = -CARHEIGHT - i * self.distance
            lane = random.randint(0, 3)
            self.ls.append([lane, y])
    def draw(self):
        for i in range(5):
            x = int(X_MARGIN + self.ls[i][0] * LANEWIDTH + (LANEWIDTH - self.width) / 2)
            y = int(self.ls[i][1])
            DISPLAYSURF.blit(OBSTACLESIMG, (x, y))
    def update(self):
        for i in range(5):
            self.ls[i][1] += self.speed
        self.speed += self.changeSpeed
        if self.ls[0][1] > WINDOWHEIGHT:
            self.ls.pop(0)
            y = self.ls[3][1] - self.distance
            lane = random.randint(0, 3)
            self.ls.append([lane, y])

class Car():
    def __init__(self):
        self.width = CARWIDTH
        self.height = CARHEIGHT
        self.x = (WINDOWWIDTH-self.width)/2
        self.y = WINDOWHEIGHT - self.height - 20  # Fixed Y position near bottom
        self.speed = CARSPEED
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((255, 255, 255))
    def draw(self):
        DISPLAYSURF.blit(CARIMG, (int(self.x), int(self.y)))
    def update(self, moveLeft, moveRight):
        if moveLeft == True:
            self.x -= self.speed
        if moveRight == True:
            self.x += self.speed
        
        # Only check horizontal boundaries
        if self.x < X_MARGIN:
            self.x = X_MARGIN
        if self.x + self.width > WINDOWWIDTH - X_MARGIN:
            self.x = WINDOWWIDTH - X_MARGIN - self.width

class Score:
    def __init__(self):
        self.score = 0
    def draw(self):
        font = pygame.font.SysFont('consolas', 30)
        scoreSurface = font.render('Score: ' + str(int(self.score)), True, (0, 0, 0))
        DISPLAYSURF.blit(scoreSurface, (10, 10))
    def update(self):
        self.score += 0.02

def calculate_reward(car, obstacles, score, previous_score):
    # Check for collision
    if isGameover(car, obstacles):
        return -100
    # Reward for score increase
    score_reward = (score.score - previous_score) * 10
    # Calculate distance to nearest obstacle
    min_distance = float('inf')
    for obstacle in obstacles.ls:
        obstacle_x = int(X_MARGIN + obstacle[0] * LANEWIDTH + (LANEWIDTH - CARWIDTH) / 2)
        obstacle_y = int(obstacle[1])
        distance = ((car.x - obstacle_x)**2 + (car.y - obstacle_y)**2)**0.5
        min_distance = min(min_distance, distance)
    distance_reward = min_distance / 100
    # Extra reward for staying in center of lane
    lane_pos = (car.x - X_MARGIN) % LANEWIDTH
    lane_center = LANEWIDTH / 2
    lane_reward = -abs(lane_pos - lane_center) / 10
    return score_reward + distance_reward + lane_reward

def rectCollision(rect1, rect2):
    if rect1[0] <= rect2[0] + rect2[2] and rect2[0] <= rect1[0] + rect1[2] and rect1[1] <= rect2[1] + rect2[3] and rect2[1] <= rect1[1] + rect1[3]:
        return True
    return False

def isGameover(car, obstacles):
    carRect = [car.x, car.y, car.width, car.height]
    for i in range(5):
        x = int(X_MARGIN + obstacles.ls[i][0] * LANEWIDTH + (LANEWIDTH - obstacles.width) / 2)
        y = int(obstacles.ls[i][1])
        obstaclesRect = [x, y, obstacles.width, obstacles.height]
        if rectCollision(carRect, obstaclesRect):
            return True
    return False

def gamePlay(bg, car, obstacles, score, ai_agent):
    car.__init__()
    obstacles.__init__()
    bg.__init__()
    score.__init__()
    previous_score = 0
    ai_agent.episode_reward = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ai_agent.save_model()
                pygame.quit()
                sys.exit()

        current_state = ai_agent.get_state(car, obstacles)
        action = ai_agent.get_action(current_state)
        moveLeft, moveRight = ai_agent.get_movement_from_action(action)

        if isGameover(car, obstacles):
            ai_agent.total_reward += ai_agent.episode_reward

            ai_agent.save_model()
            
            ai_agent.epsilon = max(0.01, ai_agent.epsilon * ai_agent.epsilon_decay)
            break

        bg.draw()
        bg.update()
        car.draw()
        car.update(moveLeft, moveRight)
        obstacles.draw()
        obstacles.update()
        score.draw()
        score.update()

        reward = calculate_reward(car, obstacles, score, previous_score)
        next_state = ai_agent.get_state(car, obstacles)
        ai_agent.update(current_state, action, reward, next_state)

        previous_score = score.score

        font = pygame.font.SysFont('consolas', 16)
        statsSurface = font.render(f'Epsilon: {ai_agent.epsilon:.3f} | Episode Reward: {ai_agent.episode_reward:.0f}', True, (0, 0, 0))
        DISPLAYSURF.blit(statsSurface, (10, 40))
        pygame.display.update()
        fpsClock.tick(FPS)

def main():
    bg = Background()
    car = Car()
    obstacles = Obstacles()
    score = Score()
    ai_agent = CarAIAgent(learning_rate=0.1, discount_factor=0.95, epsilon=1.0, epsilon_decay=0.995)

    # Vòng lặp chính tự động chơi lại mà không cần ấn space
    while True:
        gamePlay(bg, car, obstacles, score, ai_agent)

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings("ignore", message="libpng warning: iCCP: known incorrect sRGB profile")
    main()