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
    angle : int between 0 and 260
    color: 3-dim tuple, with int values between 0 and 255
    '''

    def __init__(self,width,height,x_pos,y_pos,angle,color):
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
        self.angle = angle

    def PointAngle(self,target_x,target_y):
        '''
        Find angle between two points,
        pointing towards target coordinates (target_x,target_y),
        from own coordinates (self.rect.x,self.rect.y).
        Target coordinates must be positve.
        '''
        if target_x < 0 or target_y < 0:
            print("ValueError: target coordinates must be positive. (%.2f,%.2f)" %(target_x,target_y))
            return ValueError

        opposite = self.rect.x - target_x
        adjacent = self.rect.y - target_y

        if opposite == 0 or adjacent == 0:
            return self.angle

        if opposite > 0:    #left side
            if adjacent > 0:    #upper left
                #target point is NW of start point
                newangle = int((360 - np.arctan(abs(opposite/adjacent))) % 360)

            if adjacent < 0:    #lower left
                #target point is SW of start point
                newangle = int((180 + np.arctan(abs(opposite/adjacent))) % 360)

        if opposite < 0:    #right side
            if adjacent > 0:    #upper right
                #target point is NE of start point
                newangle = int((np.arctan(abs(opposite/adjacent))) % 360)

            if adjacent < 0: #lower right
                #target point is SE of start point
                newangle = int((180 - np.arctan(abs(opposite/adjacent))) % 360)
        return newangle



class Boid(Rectangle):
    '''
    Boid object representation, derived from Rectangle class.
    '''

    def __init__(self,width,height,x_pos,y_pos,angle,color,velocity,proximity):
        '''Create a Boid.'''
        super().__init__(width,height,x_pos,y_pos,angle,color)
        self.velocity = velocity #movement speed of boid
        #self.angle = angle  #direction of boid
        self.proximity = proximity #area around boid
        self.local_area = pygame.Surface([self.width+self.proximity,self.height+self.proximity])
        self.local_group = pygame.sprite.Group()

    def find_local_boid(self,other):
        '''Find if boid is in proximity and add to local group.'''
        x_dist = abs(self.rect.x - other.rect.x)
        y_dist = abs(self.rect.y - other.rect.y)

        if x_dist < self.width + self.proximity:
            self.local_group.add(other)
            return
        if y_dist < self.height + self.proximity:
            self.local_group.add(other)
            return
        else:
            pass

    def proximity_center(self):
        '''Adjust direction towards average center of boids in proximity.'''
        if len(self.local_group.sprites()) < 1:
            return self.angle

        flock_x = []
        flock_y = []
        for boid in self.local_group.sprites():
            flock_x.append(boid.rect.x)
            flock_y.append(boid.rect.y)

        x = np.mean(flock_x)
        y = np.mean(flock_y)

        return self.PointAngle(x,y)


    def proximity_velocity(self):
        '''Adjust boid velocity to average velocity of boids in proximity.'''
        if len(self.local_group.sprites()) == 0:
            return self.velocity

        newvelocity = 0.0

        for boid in self.local_group.sprites():
            newvelocity += boid.velocity

        newvelocity = (newvelocity)/len(self.local_group.sprites())
        return newvelocity


    def proximity_direction(self):
        '''Change direction towards average direction of boids in proximity.'''
        if len(self.local_group.sprites()) == 0:
            return self.angle

        newangle = 0.0
        for boid in self.local_group.sprites():
            newangle += boid.angle

        newangle = int((newangle)/len(self.local_group.sprites()) % 360)
        return newangle


    def proximity_collision(self):
        '''Avoid collision with other boids'''
        if len(self.local_group.sprites()) == 0:
            return self.angle

        for boid in self.local_group.sprites():

            x_dist = abs(self.rect.x - boid.rect.x)
            if x_dist < self.width + self.proximity/2:
                self.velocity *= -1
                return

            y_dist = abs(self.rect.y - boid.rect.y)
            if y_dist < self.height + self.proximity:
                self.velocity *= -1
                return
        return


    def noise(self):
        '''this function adds noise'''
        self.angle = (random.randint((self.angle - 10),(self.angle + 10))) % 360
        self.velocity = (self.velocity + random.uniform(-1,1)) % 5
        return


    def new_angle(self):
        '''this function takes the mean of angles'''
        self.angle = int(((self.proximity_center()+self.proximity_direction()+self.angle)/3) % 360)
        return


    def new_velocity(self):
        '''this function takes the mean of velocities'''
        self.velocity = ((self.angle+self.proximity_velocity())/3) % 5


    def new_position(self):
        '''calculate new position'''
        self.new_angle()
        self.new_velocity()

        self.rect.x += self.velocity * np.sin(np.radians(self.angle))
        self.rect.y -= self.velocity * np.cos(np.radians(self.angle))



    #this function should update boid behaviour by calling on the other functions
    def update(self):
        '''Update Boid behaviour.'''
        self.new_velocity()
        self.new_angle()
        self.noise()
        self.new_position()
        #self.proximity_velocity()
        #self.object_collision()

        #left wall collide
        if self.rect.x < 0.0 - self.width + 50:
            self.rect.x = SCREEN_WIDTH + self.width - 1 -50

            #right wall collide
        elif self.rect.x > SCREEN_WIDTH + self.width - 50:
                self.rect.x = 0.0 - self.width + 1 + 50

            #roof collide
        elif self.rect.y < 0.0 - self.height + 50:
            self.rect.y = SCREEN_HEIGHT + self.height - 1 - 50

            #bottom collide
        elif self.rect.y > SCREEN_HEIGHT + self.height - 50:
            self.rect.y = 0.0 - self.height + 1 + 50

        else:
            pass

        self.local_group.empty() #remove all boids in local group


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
        '''Initialize pygame, display and sprite Groups.'''
        pygame.init()
        self.SCRN_W = SCRN_W
        self.SCRN_H = SCRN_H
        SCREEN_SIZE = self.SCRN_W, self.SCRN_H
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.Boid_Group = pygame.sprite.Group()
        self.all_Sprites = pygame.sprite.Group()

    def add_Boid(self,width,height,x_pos,y_pos,angle,color,velocity,proximity):
        '''Add a Boid to the simulation.'''
        newboid = Boid(width,height,x_pos,y_pos,angle,color,velocity,proximity)
        self.Boid_Group.add(newboid)

    def play(self):
        '''begin simulation.'''
        key = pygame.key.get_pressed()
        for i in range(10):
            self.add_Boid(5,5,random.randint(0,self.SCRN_W - 10),random.randint(0,self.SCRN_H - 10),random.randint(0,360),(255,255,255),random.randint(1,5),10)
        self.all_Sprites.add(self.Boid_Group)

        while True: #the simulation loop

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        #exits game when pressing ESC
                        pygame.quit()

            for boid in self.Boid_Group.sprites():
                #other_boid = pygame.sprite.spritecollide(boid,self.Boid_Group,False)
                #if len(other_boid)>1:
                #    boid.find_local_boid(other_boid[0])
                for other_boid in self.Boid_Group.sprites():
                    if boid == other_boid:
                        pass
                    else:
                        boid.find_local_boid(other_boid)


            self.clock.tick(self.FPS)
            self.screen.fill((0,0,0))
            self.all_Sprites.update()
            self.all_Sprites.draw(self.screen)
            pygame.display.flip()


sim = Simulation(SCREEN_WIDTH,SCREEN_HEIGHT)
sim.play()
