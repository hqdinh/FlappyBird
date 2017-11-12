""" Flappy Bird game in python
Real gravity physics. 
All parameters in Config can be changed without breaking the game
Simplified graphics (no background nor bird sprites)
Quit by pressing ESCAPE or click the x-mark
Play by clicking on the window or pressing any other key
"""
 

import sys
import random
import pygame

QUIT = pygame.QUIT
MOUSECLICK = pygame.MOUSEBUTTONDOWN
KEYDOWN = pygame.KEYDOWN
K_ESCAPE = pygame.K_ESCAPE

class Config:
    """Defines configurations of the game"""    
    def __init__(self):
        self.bird_x = 50  # Starting x-coor of bird. Stays the same throughout
        self.bird_yo = 50  # Starting y-coor of bird
        self.gravity = 0.8  # How fast bird accel. downward
        self.jump_v = 10  # Each jump will set the bird's velocity to jump_v
        self.gap = 200  # Gap between each set of upper and lower pipes
        self.pipe_speed = 2  # How fast the pipes move to the left
        self.pipe_dist = 200  # How far each set of pipes are (the smaller the harder)
        self.offs = 200  # how far each subsequent gap may vary vertically 
        self.screen_W = 400  # screen width
        self.screen_H = 700  # screen height
        
class FlappyBird:
    """Game class"""    
    
    def __init__(self):
        # Load configurations from Config
        self.config = Config()
        self.bird_x = self.config.bird_x
        self.bird_yo = self.config.bird_yo
        self.gravity = self.config.gravity
        self.jump_v = -self.config.jump_v
        self.gap = self.config.gap
        self.pipe_speed = self.config.pipe_speed
        self.pipe_dist = self.config.pipe_dist
        self.offs = self.config.offs 
        self.screen_W = self.config.screen_W
        self.screen_H = self.config.screen_H
                
        # Image loading procedures 
        self.screen = pygame.display.set_mode((self.screen_W, self.screen_H))
        self.bird = pygame.Rect(self.bird_x, self.bird_yo, 40, 40)
        self.bird_img = pygame.image.load("assets/pusheen_50.png").convert_alpha()
        self.pipe_bot = pygame.image.load("assets/bottom.png").convert_alpha()
        self.pipe_top = pygame.image.load("assets/top.png").convert_alpha()
        self.pipe_W = self.pipe_top.get_width()
        self.pipe_H = self.pipe_top.get_height()
        self.pipe_num = self.screen_W//self.pipe_W
        
        # Initiate game variables        
        self.new_round_handler()

    def rand_offs(self):
        # Returns distance from midscreen to midpoint of the gap of each pipe pair
        return random.randint(-self.offs, self.offs)
    
    def new_round_handler(self):
        """Reset these variables at start/death"""      
        # Pipe settings
        self.pipe_x = [self.screen_W + n*self.pipe_dist 
                       for n in range(self.pipe_num)]
        self.pipe_bot_y = [self.screen_H/2 + self.gap/2 + self.rand_offs() 
                           for n in range(self.pipe_num)]
        self.pipe_top_y = [d - self.gap - self.pipe_H 
                           for d in self.pipe_bot_y]
        self.pipe_pos = [self.pipe_x, self.pipe_bot_y, self.pipe_top_y]
        self.pipe_it = 0  # Iterator
                
        # Bird settings
        self.bird_y = self.bird_yo
        self.bird_vel = 0        
        self.jump = False # this switches to True when anykey is pressed
        self.dead = False
        self.score = 0
        
    def update_pipes(self):
        """Update pipes' positions"""
        self.pipe_pos[0] = [x - self.pipe_speed for x in self.pipe_pos[0]]
        self.pipe_it = self.pipe_it % self.pipe_num
        # replace with new pipe after curr pipe passed left edge of screen
        if self.pipe_pos[0][self.pipe_it] < -self.pipe_W:
            # x coordinates of each pair
            self.pipe_pos[0][self.pipe_it] = self.pipe_pos[0][self.pipe_it] + \
                                             self.pipe_num*self.pipe_dist
            # y coordinate of bottom pipes
            self.pipe_pos[1][self.pipe_it] = self.screen_H/2 + self.gap/2 + \
                                             self.rand_offs()
            # y coordinate of top pipes
            self.pipe_pos[2][self.pipe_it] = self.pipe_pos[1][self.pipe_it] - \
                                             self.gap - self.pipe_H 
            self.pipe_it += 1
            self.score += 1

    def update_bird(self):
        """Update bird's position"""
        if self.jump:
            self.bird_vel = self.jump_v
            self.jump = False
        else:
            self.bird_vel = self.bird_vel + self.gravity
        self.bird_y = self.bird_y + self.bird_vel            
        self.bird[1] = self.bird_y  # Update bird rectangle's y-coor
        
    def collision_check(self):
        """ Checks for bird-pipe and bird-ground collisions """        
        
        # pipe_rects contains all pipe rectangles for collision check
        pipe_rects = [pygame.Rect(self.pipe_pos[0][n], 
                                 self.pipe_pos[1][n],
                                 self.pipe_W - 10,
                                 self.pipe_H) for n in range(self.pipe_num)]
        pipe_rects += [pygame.Rect(self.pipe_pos[0][n],
                                 self.pipe_pos[2][n],
                                 self.pipe_W - 10,
                                 self.pipe_H) for n in range(self.pipe_num)]            
        
        # checks for visible collision
        for pipe in pipe_rects:
            if pipe.colliderect(self.bird):
                self.dead = True
        
        # checks for out of screen collision or hitting the ground
        if (self.bird[1] > self.screen_H or 
                (self.bird[1] < 0 and 
                 self.bird[0] > self.pipe_pos[0][self.pipe_it])):
            self.dead = True
    
    def draw_objects(self):
        self.screen.fill((0, 0, 0))
        for i in range(self.pipe_num):
                self.screen.blit(self.pipe_bot, (self.pipe_pos[0][i], self.pipe_pos[1][i]))
                self.screen.blit(self.pipe_top, (self.pipe_pos[0][i], self.pipe_pos[2][i]))
            
        self.screen.blit(self.font.render(str(self.score),
                                     -1, 
                                     (255, 255, 255)),
                         (50,50))
        self.screen.blit(self.bird_img, (self.bird_x, self.bird_y))

    def run_instance(self):
        """Main game"""        
        clock = pygame.time.Clock()
        pygame.font.init()        
        self.font = pygame.font.SysFont("Times New Roman", 50)
        
        while True:
            clock.tick(60)
            
            events = pygame.event.get()
            for event in events:
                if ((event.type == KEYDOWN and event.key == K_ESCAPE) 
                                               or event.type == QUIT):
                    pygame.quit()
                    sys.exit()
                if (event.type == KEYDOWN or event.type == MOUSECLICK):
                    self.jump = True
            
            self.draw_objects()
            self.update_bird()
            self.update_pipes()
            self.collision_check()
            if self.dead:
                self.new_round_handler()
                
            pygame.display.update()
    
    @staticmethod
    def start():
        game = FlappyBird()
        game.run_instance()
        
if __name__ == "__main__":
    FlappyBird.start()       
