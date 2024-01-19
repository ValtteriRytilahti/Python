import pygame
import random
from time import sleep
import json

"""
classic snake game but with a twist
every time snake eats an apple, it grows by 1
there also appears 1 black spot on random position on the screen
if snake collides with black spot, it dies and the game is over
"""


apple_color = (255, 0, 0)
snake_color = (0, 255, 0)
background_color = (0, 50, 0)

path = ""
fps = 9
apple_size = 20
snake_size = 20
snake_speed = 20
screen_width = 700
screen_height = 600


class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_change = 0
        self.y_change = 0
        self.body = [[self.x, self.y]]

        self.length = 1

    def update(self):
        self.body.insert(0, [self.x, self.y])
        if len(self.body) > self.length:
            self.body.pop()
        self.x += self.x_change
        self.y += self.y_change
    
    def draw(self, surface):
        for cords in self.body:
            pygame.draw.rect(surface, snake_color, (cords[0], cords[1], snake_size, snake_size))
        
    def move(self, x, y):
        self.x_change = x
        self.y_change = y
    
    def key_pressed(self, key):
        if key == pygame.K_LEFT:
            self.move(-snake_speed, 0)
        elif key == pygame.K_RIGHT:
            self.move(snake_speed, 0)
        elif key == pygame.K_UP:
            self.move(0, -snake_speed)
        elif key == pygame.K_DOWN:
            self.move(0, snake_speed)

    def eat(self, apple):
        if self.x == apple.x and self.y == apple.y:
            self.length += 1
            return True
        return False
        
    def check_collision(self, spots):
        if self.x > screen_width - snake_size or self.x < 0:
            return True
        elif self.y > screen_height - snake_size or self.y < 0:
            return True
        
        for spot in spots:
            if self.x == spot[0] and self.y == spot[1]:
                return True
        
        # check if snake collides with itself
        for cord in self.body:
            # skip the head
            if cord == self.body[0]:
                continue
            if self.x == cord[0] and self.y == cord[1]:
                return True
class Apple:
    def __init__(self, death_spots):
        self.death_spots = death_spots
        self.getPos()
    
    def getPos(self):
        while True:
            self.x = random.randint(0, screen_width - apple_size)
            self.y = random.randint(0, screen_height - apple_size)
            # make positions divisible by 20 so they are on the grid
            self.x = self.x - self.x % apple_size
            self.y = self.y - self.y % apple_size
            # check if apple is on a death spot
            if (self.x, self.y) not in self.death_spots:
                break        
            
    def draw(self, surface):
        pygame.draw.rect(surface, apple_color, (self.x, self.y, apple_size, apple_size))
    
class Game:
    def __init__(self, config):
        self.config = config
        self.highScore = config["snakeHighScore"]
        self.game_over = False
        self.score = 0
        self.snake = Snake(100, 100)
        self.deadSpots = []
        self.apple = Apple(self.deadSpots)

    def update(self):
        self.snake.update()
        if self.snake.eat(self.apple):
            self.deadSpot()
            self.score += 1
            self.apple = Apple(self.deadSpots)
        if self.snake.check_collision(self.deadSpots):
            self.game_over = True
    
    def saveScore(self):
        if self.score > self.highScore:
            self.config["snakeHighScore"] = self.score
            with open(f"{path}/inttiConfig.json", "w") as f:
                json.dump(self.config, f, indent=2)

    def draw(self, surface):
        # draw a grid on the screen
        surface.fill(background_color)
        for x in range(0, screen_width, snake_size):
            pygame.draw.line(surface, (0, 0, 0), (x, 0), (x, screen_height))
        for y in range(0, screen_height, snake_size):
            pygame.draw.line(surface, (0, 0, 0), (0, y), (screen_width, y))

        self.snake.draw(surface)
        self.apple.draw(surface)
        font = pygame.font.SysFont('comicsans', 30)
        text = font.render("Score: " + str(self.score), 1, (255, 255, 255))
        surface.blit(text, (0, 0))
        text = font.render("High Score: " + str(self.highScore), 1, (255, 255, 255))
        surface.blit(text, (0, 30))

        # draw dead spots
        for spot in self.deadSpots:
            pygame.draw.rect(surface, (0, 0, 0), (spot[0], spot[1], snake_size, snake_size))

        if self.game_over:
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render("Game Over", 1, (255, 255, 255))
            surface.blit(text, (screen_width / 2 - text.get_width() / 2, screen_height / 2 - text.get_height() / 2))
            pygame.display.update()
            
    def check_radius(self, x, y):
        for cord in self.snake.body:
            if abs(cord[0] - x) < 100 and abs(cord[1] - y) < 100:
                return True
        return False

    def deadSpot(self):
        x = random.randint(0, screen_width - snake_size)
        y = random.randint(0, screen_height - snake_size)
        # make cordinates devisible by 20 so they are on the grid
        x = x - (x % snake_size)
        y = y - (y % snake_size)
        if (x, y) not in self.snake.body and (x, y) not in self.deadSpots:

            # check if spot is in 100 pixels radius of the snake x and y
            # if not, then add it to the deadSpots list
            if not self.check_radius(x, y):
                self.deadSpots.append((x, y))
    def replay(self):
        self.game_over = False
        self.score = 0
        self.snake = Snake(100, 100)
        self.apple = Apple(self.deadSpots)
        self.deadSpots = []

def main():
    while True:
        with open(f"{path}/Config.json") as f:
            data = json.load(f)

        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Snake')
        clock = pygame.time.Clock()
        game = Game(data)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    game.snake.key_pressed(event.key)
            game.update()
            game.draw(screen)
            pygame.display.update()
            if game.game_over:
                game.saveScore()
                sleep(2)
                break
            clock.tick(fps)

if __name__ == '__main__':
    main()
