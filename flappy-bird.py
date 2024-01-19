import random
import pygame
import json


# Classic flappy bird game

path = ""
debugMode = False

def loadImages():
    global pipe, bird, topPipe, bottomPipe, bg
    pipe = pygame.image.load(path + "/images/pipe.png")
    bottomPipe = pygame.transform.scale(pipe, (60, 500))
    topPipe = pygame.transform.flip(pygame.transform.scale(pipe, (60, 500)), False, True)

    bg = pygame.image.load(path + "/images/bg.png")
    bird = pygame.image.load(path + "/images/bird.png")
    bg = pygame.transform.scale(bg, (640, 650))
    bird = pygame.transform.scale(bird, (50, 50))

class Pipes():
    def __init__(self, x, screen):

        self.screen = screen
        self.x = x
        self.height = 200

        self.difficulty = 0

        self.top_difference = 450
        self.bottom_difference = 180

        self.top = self.height - self.top_difference
        self.bottom = self.height + self.bottom_difference
        # create a hitbox for the pipes
        self.hitbox = pygame.Rect(self.x, self.top, 60, 500)
        self.hitbox2 = pygame.Rect(self.x, self.bottom, 60, 500)

    def draw(self):
        # draw the pipes
        self.screen.blit(topPipe, (self.x, self.top))
        self.screen.blit(bottomPipe, (self.x, self.bottom))

        # draw the hitbox for the pipes
        if debugMode:
            pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox, 2)
            pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox2, 2)

    def update(self):
        # update the pipes position
        self.x -= 5
        # move pipe back to the rigth of the screen
        if self.x < -60:
            self.x = 700
            self.height = random.randint(20, 400)
            self.top = self.height - self.top_difference + self.difficulty
            self.bottom = self.height + self.bottom_difference 
            self.hitbox = pygame.Rect(self.x, self.top, 60, 500)
            self.hitbox2 = pygame.Rect(self.x, self.bottom, 60, 500)
            self.difficulty += 0.5 # make pipes colser together as the game goes on
        # update the hitbox position
        self.hitbox.x = self.x
        self.hitbox2.x = self.x

class Bird():
    def __init__(self, screen):
        self.x = 100
        self.y = 300
        self.screen = screen
        
        self.score = 0
        self.bird_velocity = 0
        self.bird_acceleration = 0.25
        self.hitbox = pygame.Rect(self.x, self.y, 35, 35)

    def bird_movement(self):
        # move bird        
        self.y += self.bird_velocity
        self.bird_velocity += self.bird_acceleration
        self.hitbox = pygame.Rect(self.x + 6, self.y + 6, 35, 35)

    def key_pressed(self, event):
        # check if key is pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.y > 30:
                    self.bird_velocity = -6
        if event.type == pygame.QUIT:
            pygame.quit()
    def draw(self):
        # draw bird
        self.screen.blit(bird, (self.x, self.y))
        # draw score
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("Score: " + str(self.score), 1, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        # draw high score to right of screen
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render("High Score: " + str(highScore), 1, (255, 255, 255))
        self.screen.blit(text, (10, 50))

        if debugMode:
            # draw all variables for debugging
            font = pygame.font.SysFont("comicsans", 20)
            text1 = font.render("x: " + str(self.x) + " y: " + str(round(self.y, 2)), 1, (255, 255, 255))
            text2 = font.render("bird_velocity: " + str(round(self.bird_velocity, 2)), 1, (255, 255, 255))
            text3 = font.render("bird_acceleration: " + str(round(self.bird_acceleration, 2)), 1, (255, 255, 255))

            self.screen.blit(text1, (10, 500))
            self.screen.blit(text2, (10, 530))
            self.screen.blit(text3, (10, 560))
            pygame.draw.rect(self.screen, (255, 0, 0), self.hitbox, 1)
        
class Game():
    def __init__(self, config, path) -> None:
        self.width = 480
        self.path = path
        self.config = config
        self.height = 640
        # set window title
        pygame.display.set_caption("Flappy Bird")
        # set window icon
        pygame.display.set_icon(bird)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.bird = Bird(self.screen)
        self.clock = pygame.time.Clock()
        
        self.pipes = [Pipes(400 + 350 * i, self.screen) for i in range(2)]        
        self.game_over = False
    
    def draw(self):
        # draw background
        self.screen.blit(bg, (0, 0))
        # draw bird
        self.bird.draw()
        # draw pipes
        for i, pipe in enumerate(self.pipes):
            pipe.draw()
            if debugMode:
                font = pygame.font.SysFont("comicsans", 20)
                text = font.render("top: " + str(pipe.top) + " bottom: " + str(pipe.bottom) + " Difficulty: " + str(pipe.difficulty), 1, (255, 255, 255))
                self.screen.blit(text, (10, 580 + i * 30))

    def hitCheck(self):
        # check if bird hits pipes
        for pipe in self.pipes:
            if self.bird.hitbox.colliderect(pipe.hitbox) or self.bird.hitbox.colliderect(pipe.hitbox2):
                self.game_over = True
            if self.bird.y > 650:
                self.game_over = True
    
    def replay(self):
        # restart game
        self.bird = Bird(self.screen)
        self.pipes = [Pipes(600 + 350 * x, self.screen) for x in range(1,3)]
        self.game_over = False
        self.bird.score = 0
        self.bird.bird_velocity = 0
        self.bird.bird_acceleration = 0.25
        self.bird.x = 100
        self.bird.y = 300
        self.bird.hitbox = pygame.Rect(self.bird.x, self.bird.y, 50, 50)


    def main(self):
        while True:
            # paint black screen
            self.screen.fill((0, 0, 0))
            font = pygame.font.SysFont("comicsans", 30)
            text = font.render("Press space to play", 1, (255, 255, 255))
            self.screen.blit(text, (self.width / 2 - text.get_width() / 2, self.height / 2 - text.get_height() / 2))
            # if space is pressed, start game
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.mainLoop()
                        self.replay()
                if event.type == pygame.QUIT:
                    quit()
            
            pygame.display.update()

            self.clock.tick(60)
    def mainLoop(self):
        global highScore
        while not self.game_over:

            self.clock.tick(60)
            for event in pygame.event.get():
                self.bird.key_pressed(event)
            # update bird position
            self.bird.bird_movement()
            # update pipes position
            for pipe in self.pipes:
                pipe.update()
            # check if bird hits pipes
            self.hitCheck()

            self.draw()
            # update screen
            pygame.display.update()
            # update score
            for pipe in self.pipes:
                if self.bird.x > pipe.x + 50 and self.bird.x < pipe.x + 60:
                    self.bird.score += 1
                    
        if self.bird.score > highScore:
            highScore = self.bird.score
            self.config["flappyBirdHighScore"] = self.bird.score
            print("saved high score: " + str(self.bird.score))
            with open(f"{self.path}/inttiConfig.json", "w") as f:
                json.dump(self.config, f, indent=2)
                
def main():
    loadImages()
    global highScore
    with open(f"{path}/Config.json") as f:
        data = json.load(f)

    highScore = data.get("flappyBirdHighScore", 0)
    pygame.init()
    game = Game(data, path)
    game.main()

if __name__ == "__main__":
    main()
