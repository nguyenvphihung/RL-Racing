import pygame, sys, random
import numpy as np
from collections import defaultdict
from pygame.locals import *
import json

# Game Constants
WINDOWWIDTH = 400
WINDOWHEIGHT = 600
X_MARGIN = 80
LANEWIDTH = 60
CARWIDTH = 40
CARHEIGHT = 60
CARSPEED = 3
DISTANCE = 200
OBSTACLESSPEED = 2
CHANGESPEED = 0.001
BGSPEED = 1.5
FPS = 60

# Pygame Initialization
pygame.init()
fpsClock = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('AI RACING')

# Load Images
CARIMG = pygame.image.load('assets/images/car.png')
OBSTACLESIMG = pygame.image.load('assets/images/obstacles.png')
BGIMG = pygame.image.load('assets/images/background.png')

class Background():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = BGSPEED
        self.img = BGIMG
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        
    def draw(self):
        DISPLAYSURF.blit(self.img, (int(self.x), int(self.y)))
        DISPLAYSURF.blit(self.img, (int(self.x), int(self.y-self.height)))
        
    def update(self):
        self.y += self.speed
        if self.y > self.height:
            self.y -= self.height

class Car():
    def __init__(self):
        self.width = CARWIDTH
        self.height = CARHEIGHT
        self.x = (WINDOWWIDTH-self.width)/2
        self.y = WINDOWHEIGHT - self.height - 50  # Cố định vị trí y của xe
        self.speed = CARSPEED
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill((255, 255, 255))
    
    def draw(self):
        DISPLAYSURF.blit(CARIMG, (int(self.x), int(self.y)))
    
    def update(self, moveLeft, moveRight, moveUp, moveDown):
        # Chỉ xử lý di chuyển trái/phải
        if moveLeft == True:
            self.x -= self.speed
        if moveRight == True:
            self.x += self.speed
        
        # Giới hạn trong đường đua
        if self.x < X_MARGIN:
            self.x = X_MARGIN
        if self.x + self.width > WINDOWWIDTH - X_MARGIN:
            self.x = WINDOWWIDTH - X_MARGIN - self.width

class Obstacles():
    def __init__(self):
        self.width = CARWIDTH
        self.height = CARHEIGHT
        self.distance = DISTANCE
        self.speed = OBSTACLESSPEED
        self.changeSpeed = CHANGESPEED
        self.ls = []
        self.current_lane = 0  # Theo dõi làn đường hiện tại để tạo mẫu từ trái sang phải
        
        # Khởi tạo 5 vật cản ban đầu với quy luật từ trái sang phải
        for i in range(5):
            y = -CARHEIGHT-i*self.distance
            lane = self.current_lane % 4  # Đảm bảo lane từ 0-3
            self.ls.append([lane, y])
            self.current_lane += 1  # Tăng lane cho vật cản tiếp theo
            
    def draw(self):
        for i in range(5):
            x = int(X_MARGIN + self.ls[i][0]*LANEWIDTH + (LANEWIDTH-self.width)/2)
            y = int(self.ls[i][1])
            DISPLAYSURF.blit(OBSTACLESIMG, (x, y))
            
    def update(self):
        for i in range(5):
            self.ls[i][1] += self.speed
        self.speed += self.changeSpeed
        
        # Khi vật cản đầu tiên ra khỏi màn hình
        if self.ls[0][1] > WINDOWHEIGHT:
            self.ls.pop(0)  # Xóa vật cản đầu tiên
            y = self.ls[3][1] - self.distance  # Tính toán vị trí y cho vật cản mới
            
            # Tạo vật cản mới theo quy luật từ trái sang phải
            lane = self.current_lane % 4  # Đảm bảo lane từ 0-3
            self.ls.append([lane, y])
            self.current_lane += 1  # Tăng lane cho vật cản tiếp theo

class Score():
    def __init__(self):
        self.score = 0
        
    def draw(self):
        font = pygame.font.SysFont('consolas', 30)
        scoreSuface = font.render('Score: '+str(int(self.score)), True, (0, 0, 0))
        DISPLAYSURF.blit(scoreSuface, (10, 10))
        
    def update(self):
        self.score += 0.02

class CarAIAgent:
    def __init__(self, action_space=2, learning_rate=0.1, discount_factor=0.95, epsilon=1.0, epsilon_decay=0.995):
        self.q_table = defaultdict(lambda: np.zeros(action_space))
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.action_space = action_space
        self.total_reward = 0
        self.episode_reward = 0
    
    def get_state(self, car, obstacles):
        """Convert game state to a discrete state representation"""
        car_x = int(car.x)
        
        # Find closest obstacle
        closest_obstacle = None
        min_distance = float('inf')
        
        for obstacle in obstacles.ls:
            obstacle_x = int(X_MARGIN + obstacle[0]*LANEWIDTH + (LANEWIDTH-CARWIDTH)/2)
            obstacle_y = int(obstacle[1])
            
            # Chỉ quan tâm đến các obstacle phía trước xe
            if obstacle_y > car.y:
                continue
                
            distance = ((car_x - obstacle_x)**2 + (car.y - obstacle_y)**2)**0.5
            if distance < min_distance:
                min_distance = distance
                closest_obstacle = (obstacle_x, obstacle_y)
        
        if closest_obstacle:
            # Rời rạc hóa khoảng cách thành các khoảng
            dx = (closest_obstacle[0] - car_x) // 20
            dy = (closest_obstacle[1] - car.y) // 20
            
            # Thêm vị trí làn của xe
            car_lane = (car_x - X_MARGIN) // LANEWIDTH
            
            return (dx, dy, car_lane)
        return (0, 0, 0)
    
    def get_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.action_space)
        else:
            return np.argmax(self.q_table[state])
    
    def update(self, state, action, reward, next_state):
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        
        new_value = (1 - self.lr) * old_value + self.lr * (reward + self.gamma * next_max)
        self.q_table[state][action] = new_value
        
        self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)
        self.episode_reward += reward
    
    def save_q_table(self, filename='q_table.json'):
        q_table_dict = {str(state): values.tolist() for state, values in self.q_table.items()}
        save_data = {
            'q_table': q_table_dict,
            'epsilon': self.epsilon,
            'total_reward': self.total_reward
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f)
            
    def load_q_table(self, filename='q_table.json'):
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            self.q_table = defaultdict(lambda: np.zeros(self.action_space))
            for state_str, values in save_data['q_table'].items():
                state = tuple(map(int, state_str.strip('()').split(', ')))
                self.q_table[state] = np.array(values)
            
            self.epsilon = save_data['epsilon']
            self.total_reward = save_data['total_reward']
            return True
        except FileNotFoundError:
            print("Không tìm thấy file Q-table, bắt đầu training mới")
            return False
    
    def get_movement_from_action(self, action):
        moveLeft = False
        moveRight = False
        
        if action == 0:  # Left
            moveLeft = True
        elif action == 1:  # Right
            moveRight = True
            
        return moveLeft, moveRight, False, False

def calculate_reward(car, obstacles, score, previous_score):
    """Calculate reward for the AI agent"""
    if isGameover(car, obstacles):
        return -100
    
    score_reward = (score.score - previous_score) * 10
    
    min_distance = float('inf')
    for obstacle in obstacles.ls:
        obstacle_x = int(X_MARGIN + obstacle[0]*LANEWIDTH + (LANEWIDTH-CARWIDTH)/2)
        obstacle_y = int(obstacle[1])
        distance = ((car.x - obstacle_x)**2 + (car.y - obstacle_y)**2)**0.5
        min_distance = min(min_distance, distance)
    
    distance_reward = min_distance / 100
    
    lane_pos = (car.x - X_MARGIN) % LANEWIDTH
    lane_center = LANEWIDTH / 2
    lane_reward = -abs(lane_pos - lane_center) / 10
    
    return score_reward + distance_reward + lane_reward

def rectCollision(rect1, rect2):
    if rect1[0] <= rect2[0]+rect2[2] and rect2[0] <= rect1[0]+rect1[2] and rect1[1] <= rect2[1]+rect2[3] and rect2[1] <= rect1[1]+rect1[3]:
        return True
    return False

def isGameover(car, obstacles):
    carRect = [car.x, car.y, car.width, car.height]
    for i in range(5):
        x = int(X_MARGIN + obstacles.ls[i][0]*LANEWIDTH + (LANEWIDTH-obstacles.width)/2)
        y = int(obstacles.ls[i][1])
        obstaclesRect = [x, y, obstacles.width, obstacles.height]
        if rectCollision(carRect, obstaclesRect) == True:
            return True
    return False

def gameStart(bg, ai_agent):
    bg.__init__()
    font = pygame.font.SysFont('consolas', 60)
    headingSuface = font.render('AI RACING', True, (255, 0, 0))
    headingSize = headingSuface.get_size()
    
    font = pygame.font.SysFont('consolas', 20)
    commentSuface = font.render('Press "space" to watch AI play', True, (0, 0, 0))
    commentSize = commentSuface.get_size()
    
    font = pygame.font.SysFont('consolas', 16)
    statsSuface = font.render(f'Epsilon: {ai_agent.epsilon:.3f} | Total Reward: {ai_agent.total_reward:.0f}', True, (0, 0, 0))
    statsSize = statsSuface.get_size()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == K_SPACE:
                    return
        bg.draw()
        DISPLAYSURF.blit(headingSuface, (int((WINDOWWIDTH - headingSize[0])/2), 100))
        DISPLAYSURF.blit(commentSuface, (int((WINDOWWIDTH - commentSize[0])/2), 400))
        DISPLAYSURF.blit(statsSuface, (int((WINDOWWIDTH - statsSize[0])/2), 450))
        pygame.display.update()
        fpsClock.tick(FPS)

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
                pygame.quit()
                sys.exit()
        
        current_state = ai_agent.get_state(car, obstacles)
        action = ai_agent.get_action(current_state)
        moveLeft, moveRight, moveUp, moveDown = ai_agent.get_movement_from_action(action)
        
        if isGameover(car, obstacles):
            ai_agent.total_reward += ai_agent.episode_reward
            return
            
        bg.draw()
        bg.update()
        car.draw()
        car.update(moveLeft, moveRight, moveUp, moveDown)
        obstacles.draw()
        obstacles.update()
        score.draw()
        score.update()
        
        reward = calculate_reward(car, obstacles, score, previous_score)
        next_state = ai_agent.get_state(car, obstacles)
        ai_agent.update(current_state, action, reward, next_state)
        
        previous_score = score.score
        
        font = pygame.font.SysFont('consolas', 16)
        statsSuface = font.render(f'Epsilon: {ai_agent.epsilon:.3f} | Episode Reward: {ai_agent.episode_reward:.0f}', True, (0, 0, 0))
        DISPLAYSURF.blit(statsSuface, (10, 40))
        
        pygame.display.update()
        fpsClock.tick(FPS)
def gameOver(bg, car, obstacles, score, ai_agent):
    font = pygame.font.SysFont('consolas', 60)
    headingSuface = font.render('GAME OVER', True, (255, 0, 0))
    headingSize = headingSuface.get_size()
    
    font = pygame.font.SysFont('consolas', 20)
    commentSuface = font.render('Press "space" to replay', True, (0, 0, 0))
    commentSize = commentSuface.get_size()
    
    font = pygame.font.SysFont('consolas', 16)
    statsSuface = font.render(f'Total Reward: {ai_agent.total_reward:.0f} | Episode Reward: {ai_agent.episode_reward:.0f}', True, (0, 0, 0))
    statsSize = statsSuface.get_size()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == K_SPACE:
                    return
        bg.draw()
        car.draw()
        obstacles.draw()
        score.draw()
        DISPLAYSURF.blit(headingSuface, (int((WINDOWWIDTH - headingSize[0])/2), 100))
        DISPLAYSURF.blit(commentSuface, (int((WINDOWWIDTH - commentSize[0])/2), 400))
        DISPLAYSURF.blit(statsSuface, (int((WINDOWWIDTH - statsSize[0])/2), 450))
        pygame.display.update()
        fpsClock.tick(FPS)

def main():
    bg = Background()
    car = Car()
    obstacles = Obstacles()
    score = Score()
    ai_agent = CarAIAgent(
        action_space=2,         # Chỉ 2 action: trái/phải
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_decay=0.995
    )
    
    # Tải Q-table nếu có
    ai_agent.load_q_table()
    
    while True:
        gameStart(bg, ai_agent)
        gamePlay(bg, car, obstacles, score, ai_agent)
        
        # Lưu Q-table sau mỗi episode
        ai_agent.save_q_table()
        
        gameOver(bg, car, obstacles, score, ai_agent)

if __name__ == '__main__':
    # Bỏ qua cảnh báo libpng
    import warnings
    warnings.filterwarnings("ignore", message="libpng warning: iCCP: known incorrect sRGB profile")
    
    # Khởi chạy game
    main()