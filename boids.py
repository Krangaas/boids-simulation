                             ##  Assignment 2  ##
                                ## INF-1400 ##
                              ##  Magus Kanck ##
                                ##  mka080  ##
import pygame
import numpy as np
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800

class Rectangle(pygame.sprite.Sprite):
    '''
    Rectangle object representation, derived from pygame.Sprite class.
    This class requires 5 inputs:
    width: int
    height: int
    x-axis position: int
    y-axis position: int
    color: 3-dim tuple, with int values between 0 and 255
    '''

    def __init__(self,width,height,x_pos,y_pos,color):
        '''create a rectangle'''
        #call parent class
        super().__init__()      #super() finds next class in search list (Sprite)
        self.width = width      #width of image/rectangle
        self.height = height    #height of image/rectangle

        #pygame.Surface() creates new image object
        self.image = pygame.Surface([self.width,self.height])
        self.image.fill(color) #fills image with color
        self.rect = self.image.get_rect() #get rectangle with dimensions of image

        #set top left corner of rectangle to [x_pos,y_pos]
        self.rect.x = x_pos
        self.rect.y = y_pos


class Boid(Rectangle):
    '''
    Boid object representation, derived from Rectangle class.
    '''

    def __init__(self,width,height,x_pos,y_pos,color,velocity,angle,proximity):
        '''Create a Boid.'''
        super().__init__(width,height,x_pos,y_pos,color)
        self.velocity = velocity #movement speed of boid
        self.angle = angle  #direction of boid
        self.proximity = proximity #area around boid
        self.local_group = pygame.sprite.Group

    def find_local_group(self):
        '''find all boids in proximity and add to local_group'''


    def proximity_center(self):
        '''adjust direction towards average center of boids in proximity'''
        flock_x = []
        flock_y = []
        total_x = 0
        total_y = 0

        for boid in self.local_group.sprites():
            flock_x.append(boid.rect.x)
            flock_y.append(boid.rect.y)

        for i in range(len(flock_x)):
            total_x += flock_x[i]
            total_y += flock_y[i]

        avg_x = total_x/len(flock_x)
        avg_y = total_y/len(flock_y)


    def proximity_speed(self,other):
        '''adjust boid velocity to average velocity of boids in proximity'''


    def proximity_direction(self,other):
        '''change direction towards average direction of boids in proximity.'''


    def object_collision(self,other):
        '''avoid collision with other boids/hoids/obstacles.'''


    #this function should update boid behaviour by calling on the other functions
    def update(self):
        '''Update Boid behaviour.'''
        #change in position = speed * direction
        self.rect.x += self.velocity * np.sin(np.radians(self.angle))
        self.rect.y -= self.velocity * np.cos(np.radians(self.angle))

        #left wall collide
        if self.rect.x <= 0:
            self.angle = -self.angle % 360
            self.rect.x = 1

        #right wall collide
        if self.rect.x >= SCREEN_WIDTH - self.width:
            self.angle = -self.angle % 360
            self.rect.x = SCREEN_WIDTH - self.width - 1

        #roof collide
        if self.rect.y < 0:
            self.angle = 180 - self.angle % 360
            self.rect.y = 1

        #bottom collide
        if self.rect.y >= SCREEN_HEIGHT:
            self.angle = 180 - self.angle % 360
            self.rect.y = SCREEN_HEIGHT - self.height - 1


class Hoid(Boid):
    '''Hoid object representation, derived from Boid class.'''

    def __init__(self,width,height,x_pos,y_pos,color,velocity,angle):
        '''Create a Hoid.'''
        super().__init__()

    def hunt():
        '''change direction towards nearest boid, if collision remove boid.'''

    #override update() function inherited from boids(?)
    def update():
        '''Update Hoid behavoiur.'''


class Obstacle(Rectangle):
    '''Obstacle object representation, derived from Rectangle class.'''

    def __init__(self,width,height,x_pos,y_pos):
        '''Create an Obstacle.'''
        super().__init__()

    def update():
        '''Obstacle is static, this function does nothing.'''


class Simulation:
    '''The Simulation class'''

    def __init__(self,SCRN_W,SCRN_H):
        '''Initialize pygame, display window and create objects.'''
        pygame.init()
        self.SCRN_W = SCRN_W
        self.SCRN_H = SCRN_H
        SCREEN_SIZE = self.SCRN_W, self.SCRN_H
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.Boid_Group = pygame.sprite.Group()
        self.all_Sprites = pygame.sprite.Group()

    def add_Boid(self,width,height,x_pos,y_pos,color,velocity,angle,proximity):
        '''add a Boid to the simulation'''
        newboid = Boid(width,height,x_pos,y_pos,color,velocity,angle,proximity)
        self.Boid_Group.add(newboid)

    def play(self):
        '''begin simulation.'''
        for i in range(100):
            self.add_Boid(10,10,random.randint(0,self.SCRN_W - 10),random.randint(0,self.SCRN_H - 10),(255,255,255),5,random.randint(0,360),100)
        self.all_Sprites.add(self.Boid_Group)

        while True: #the simulation loop

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            #exits game when pressing ESC
                            pygame.quit()

            self.clock.tick(self.FPS)
            self.screen.fill((0,0,0))
            self.all_Sprites.update()
            self.all_Sprites.draw(self.screen)
            pygame.display.flip()


sim = Simulation(SCREEN_WIDTH,SCREEN_HEIGHT)
sim.play()
