import pygame, sys, random
import numpy as np
import tensorflow as tf
from collections import deque
from pygame.locals import *

# Cài đặt game
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

# Tải hình ảnh
CARIMG = pygame.image.load('assets/images/car.png')
OBSTACLESIMG = pygame.image.load('assets/images/obstacles.png')
BGIMG = pygame.image.load('assets/images/background.png')

pygame.init()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('RACING RL')
fpsClock = pygame.time.Clock()

# Định nghĩa DQN Agent
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.model = self._build_model()

    def _build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(24, input_dim=self.state_size, activation='relu'),
            tf.keras.layers.Dense(24, activation='relu'),
            tf.keras.layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=0.001))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

# Các lớp game
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
        DISPLAYSURF.blit(self.img, (int(self.x), int(self.y-self.height)))
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
            y = -CARHEIGHT-i*self.distance
            lane = random.randint(0, 3)
            self.ls.append([lane, y])
    def draw(self):
        for i in range(5):
            x = int(X_MARGIN + self.ls[i][0]*LANEWIDTH + (LANEWIDTH-self.width)/2)
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

class Car:
    def __init__(self):
        self.width = CARWIDTH
        self.height = CARHEIGHT
        self.x = (WINDOWWIDTH-self.width)/2
        self.y = (WINDOWHEIGHT-self.height)/2
        self.speed = CARSPEED
    def draw(self):
        DISPLAYSURF.blit(CARIMG, (int(self.x), int(self.y)))
    def update(self, action):
        if action == 0:  # Trái
            self.x -= self.speed
        elif action == 1:  # Phải
            self.x += self.speed
        elif action == 2:  # Lên
            self.y -= self.speed
        elif action == 3:  # Xuống
            self.y += self.speed
        
        # Giới hạn di chuyển
        if self.x < X_MARGIN:
            self.x = X_MARGIN
        if self.x + self.width > WINDOWWIDTH - X_MARGIN:
            self.x = WINDOWWIDTH - X_MARGIN - self.width
        if self.y < 0:
            self.y = 0
        if self.y + self.height > WINDOWHEIGHT:
            self.y = WINDOWHEIGHT - self.height

class Score:
    def __init__(self):
        self.score = 0
    def draw(self):
        font = pygame.font.SysFont('consolas', 30)
        scoreSuface = font.render('Score: '+str(int(self.score)), True, (0, 0, 0))
        DISPLAYSURF.blit(scoreSuface, (10, 10))
    def update(self):
        self.score += 0.02

# Hàm hỗ trợ
def rectCollision(rect1, rect2):
    return (rect1[0] <= rect2[0]+rect2[2] and 
            rect2[0] <= rect1[0]+rect1[2] and 
            rect1[1] <= rect2[1]+rect2[3] and 
            rect2[1] <= rect1[1]+rect1[3])

def isGameover(car, obstacles):
    carRect = [car.x, car.y, car.width, car.height]
    for i in range(5):
        x = X_MARGIN + obstacles.ls[i][0]*LANEWIDTH + (LANEWIDTH-obstacles.width)/2
        y = obstacles.ls[i][1]
        obstaclesRect = [x, y, obstacles.width, obstacles.height]
        if rectCollision(carRect, obstaclesRect):
            return True
    return False

# Trích xuất trạng thái và phần thưởng
def get_state(car, obstacles):
    closest_obstacles = sorted(obstacles.ls, key=lambda x: x[1])[:2]
    state = [car.x/WINDOWWIDTH, car.y/WINDOWHEIGHT]
    for obs in closest_obstacles:
        lane, y = obs
        x = X_MARGIN + lane * LANEWIDTH
        state.extend([x/WINDOWWIDTH, y/WINDOWHEIGHT])
    return np.array([state])

def get_reward(car, obstacles, done):
    reward = 0.1
    if done:
        reward = -100
    if car.x < X_MARGIN + 10 or car.x > WINDOWWIDTH - X_MARGIN - 10 - CARWIDTH:
        reward -= 0.1
    return reward

# Các màn hình game
def gameStart(bg):
    bg.__init__()
    font = pygame.font.SysFont('consolas', 60)
    headingSuface = font.render('RACING RL', True, (255, 0, 0))
    headingSize = headingSuface.get_size()
    font = pygame.font.SysFont('consolas', 20)
    commentSuface = font.render('Press SPACE to start', True, (0, 0, 0))
    commentSize = commentSuface.get_size()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP and event.key == K_SPACE:
                return
        bg.draw()
        DISPLAYSURF.blit(headingSuface, ((WINDOWWIDTH - headingSize[0])//2, 100))
        DISPLAYSURF.blit(commentSuface, ((WINDOWWIDTH - commentSize[0])//2, 400))
        pygame.display.update()
        fpsClock.tick(FPS)

def gamePlay(bg, car, obstacles, score, agent):
    car.__init__()
    obstacles.__init__()
    bg.__init__()
    score.__init__()
    state = get_state(car, obstacles)
    total_reward = 0
    batch_size = 32

    while True:
        action = agent.act(state)
        car.update(action)
        next_state = get_state(car, obstacles)
        done = isGameover(car, obstacles)
        reward = get_reward(car, obstacles, done)
        agent.remember(state, action, reward, next_state, done)
        total_reward += reward
        state = next_state

        # Cập nhật game
        bg.update()
        obstacles.update()
        score.update()

        # Vẽ các thành phần
        bg.draw()
        car.draw()
        obstacles.draw()
        score.draw()
        pygame.display.update()
        fpsClock.tick(FPS)

        # Huấn luyện
        agent.replay(batch_size)

        if done:
            print(f"Episode Reward: {total_reward:.2f}, Score: {int(score.score)}")
            return

def gameOver(bg, car, obstacles, score):
    font = pygame.font.SysFont('consolas', 60)
    headingSuface = font.render('GAMEOVER', True, (255, 0, 0))
    headingSize = headingSuface.get_size()
    font = pygame.font.SysFont('consolas', 20)
    commentSuface = font.render('Press SPACE to replay', True, (0, 0, 0))
    commentSize = commentSuface.get_size()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYUP and event.key == K_SPACE:
                return
        bg.draw()
        car.draw()
        obstacles.draw()
        score.draw()
        DISPLAYSURF.blit(headingSuface, ((WINDOWWIDTH - headingSize[0])//2, 100))
        DISPLAYSURF.blit(commentSuface, ((WINDOWWIDTH - commentSize[0])//2, 400))
        pygame.display.update()
        fpsClock.tick(FPS)

def main():
    bg = Background()
    car = Car()
    obstacles = Obstacles()
    score = Score()
    agent = DQNAgent(state_size=6, action_size=5)
    gameStart(bg)
    while True:
        gamePlay(bg, car, obstacles, score, agent)
        gameOver(bg, car, obstacles, score)

if __name__ == '__main__':
    main()