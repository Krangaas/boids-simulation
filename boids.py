                             ##  Assignment 2  ##
                                ## INF-1400 ##
                              ##  Magus Kanck ##
                                ##  mka080  ##
import sys
import pygame
import numpy as np
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800

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
        Returns int between 0 and 360.
        '''
        #if target_x < 0 or target_y < 0:
        #    print("ValueError: in function PointAngle,\ntarget coordinates must be positive. (%.2f,%.2f)" %(target_x,target_y))
        #    sys.exit()

        opposite = self.rect.x - target_x
        adjacent = self.rect.y - target_y

        if opposite == 0 or adjacent == 0:
            return self.angle

        if opposite > 0:    #left side
            if adjacent > 0:    #upper left
                #target point is NW of start point
                newangle = int((360 - np.rad2deg(np.arctan(abs(opposite/adjacent)))) % 360)
                #print("Target NW: 360 - %.2f" %(np.rad2deg(np.arctan(abs(opposite/adjacent)))%360))
                #print("%.2f elem in (270,360)\n" %newangle)

            if adjacent < 0:    #lower left
                #target point is SW of start point
                newangle = int(180 + np.rad2deg(np.arctan(abs(opposite/adjacent))) % 360)
                #print("Target SW: 180 + %.2f" %np.rad2deg(np.arctan(abs(opposite/adjacent))))
                #print("%.2f elem in (180,270)" %newangle)
        if opposite < 0:    #right side
            if adjacent > 0:    #upper right
                #target point is NE of start point
                newangle = int(np.rad2deg(np.arctan(abs(opposite/adjacent))) % 360)
                #print("Target NE: %.2f" %np.rad2deg(np.arctan(abs(opposite/adjacent))))
                #print("%.2f elem in (0,90)" %newangle)
            if adjacent < 0: #lower right
                #target point is SE of start point
                newangle = int((180 - np.rad2deg(np.arctan(abs(opposite/adjacent)))) % 360)
                #print("Target SE: 180 - %.2f" %np.rad2deg(np.arctan(abs(opposite/adjacent))))
                #print("%.2f elem in (90,180)" %newangle)
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
        self.local_group = pygame.sprite.Group()
        self.MAX_SPEED = 2.0
        self.MIN_SPEED = 1.0


    def find_local_boid(self,other):
        '''
        Check if boid is in proximity and add to local group.
        '''

        x_dist = abs(self.rect.x - other.rect.x)
        if x_dist < self.width + self.proximity:
            self.local_group.add(other)
            return

        y_dist = abs(self.rect.y - other.rect.y)
        if y_dist < self.height + self.proximity:
            self.local_group.add(other)
            return
        return


    def local_center(self):
        '''
        Find average center of boids in local group, return tuple.
        '''

        if len(self.local_group.sprites()) == 0:
            return self.rect.x, self.rect.y
        list_x = []
        list_y = []
        for boid in self.local_group.sprites():
            list_x.append(boid.rect.x)
            list_y.append(boid.rect.y)

        avg_x = np.mean(list_x)
        avg_y = np.mean(list_y)
        return avg_x, avg_y


    def local_velocity(self):
        '''
        Find average velocity of boids in local group, return float.
        '''

        if len(self.local_group.sprites()) == 0:
            return self.velocity

        newvelocity = 0.0

        for boid in self.local_group.sprites():
            newvelocity += boid.velocity

        newvelocity = (newvelocity)/len(self.local_group.sprites())
        return newvelocity


    def local_direction(self):
        '''
        Find average direction of boids in proximity, return int.
        '''

        if len(self.local_group.sprites()) == 0:
            return self.angle

        newangle = 0.0
        for boid in self.local_group.sprites():
            newangle += boid.angle

        newangle = int((newangle)/len(self.local_group.sprites()) % 360)
        return newangle


    def local_collision(self):
        '''
        Find angle pointing away from nearest boid in local group,
        return float.
        '''
        if len(self.local_group.sprites()) == 0:
            return self.angle

        closest_boid = None
        smallest_h = self.proximity
        for boid in self.local_group.sprites():

            x_dist = abs(self.rect.x - boid.rect.x)
            y_dist = abs(self.rect.y - boid.rect.y)
            h = np.hypot(x_dist,y_dist)
            if h < smallest_h:
                h = smallest_h
                boid = closest_boid

        print(closest_boid)
        if smallest_h < np.hypot(self.width+self.proximity/2,self.height+self.proximity/2):
            newangle = - self.PointAngle(boid.rect.x,boid.rect.y)
            return newangle

        return self.angle


    def new_angle(self,avg_x,avg_y):
        '''
        Find new angle based on mean of other angles.
        '''
        dir = self.local_direction()
        center = self.PointAngle(avg_x,avg_y)
        col = self.local_collision()

        self.angle = int(((dir + col + center)/3) % 360)
        return


    def new_velocity(self):
        '''this function takes the mean of velocities'''
        newvelocity = ((self.angle+self.local_velocity())/2)

        if newvelocity > self.MAX_SPEED:
            newvelocity = self.MAX_SPEED
        if newvelocity < self.MIN_SPEED:
            newvelocity = self.MIN_SPEED

        return newvelocity


    def new_position(self,a_factor=0.0,v_factor=0.0):
        '''
        Calculate new position from velocity and angle/direction.
        '''
        avg_x, avg_y = self.local_center()
        self.new_angle(avg_x,avg_y,)

        self.velocity = self.new_velocity()
        self.angle, self.velocity = self.noise(a_factor,v_factor) #add noise to velocity and direction

        self.rect.x += self.velocity * np.sin(np.radians(self.angle))
        self.rect.y -= self.velocity * np.cos(np.radians(self.angle))


    def noise(self,a,v):
        '''this function adds a noise coefficient to the velocity and direction of the boid'''
        noisyangle = (random.randint((self.angle - a),(self.angle + a))) % 360
        noisyvelocity = self.velocity + random.uniform(-v,v)

        if noisyvelocity > self.MAX_SPEED:
            noisyvelocity = self.MAX_SPEED
        if noisyvelocity < self.MIN_SPEED:
            noisyvelocity = self.MIN_SPEED

        return noisyangle, noisyvelocity


    def update(self):
        '''Update Boid behaviour.'''

        self.new_position(5,2)    #calculate new position
        #left wall collide
        if self.rect.x < 0.0 - self.width:# + 50:
            self.rect.x = SCREEN_WIDTH + self.width - 1# -50
            #self.angle = -self.angle
            #self.rect.x = 51
        #right wall collide
        if self.rect.x > SCREEN_WIDTH + self.width:# - 50:
            self.rect.x = 0.0 - self.width + 1# + 50
            #self.angle= -self.angle
            #self.rect.x = SCREEN_WIDTH - 51
        #roof collide
        if self.rect.y < 0.0 - self.height:# + 50:
            self.rect.y = SCREEN_HEIGHT + self.height - 1# - 50
            #self.angle = 180 - self.angle
            #self.rect.y = 51
        #bottom collide
        if self.rect.y > SCREEN_HEIGHT + self.height:# - 50:
            self.rect.y = 0.0 - self.height + 1# + 50
            #self.angle = 180 - self.angle
            #self.rect.y = SCREEN_HEIGHT - 50

        self.local_group.empty()


class Hoik(Boid):
    '''Hoik object representation, derived from Boid class.'''

    def __init__(self,width,height,x_pos,y_pos,angle,color,velocity,proximity):
        '''Create a Hoik.'''
        super().__init__(width,height,x_pos,y_pos,angle,color,velocity,proximity)
        self.MAX_SPEED = 6.0
        self.MIN_SPEED = 1.0

    def new_angle(self):
        '''
        Find angle pointing towards nearest boid in local group,
        return float.
        '''
        if len(self.local_group.sprites()) == 0:
            return self.angle

        closest_boid = None
        smallest_h = 0.0
        for boid in self.local_group.sprites():
            #print(boid)
            x_dist = abs(self.rect.x - boid.rect.x)
            y_dist = abs(self.rect.y - boid.rect.y)
            h = np.hypot(x_dist,y_dist)
            if h < smallest_h:
                h = smallest_h
                print(boid)
                boid = closest_boid

        #print(closest_boid)
        if smallest_h < np.hypot(self.width+self.proximity/2,self.height+self.proximity/2):
            newangle =  self.PointAngle(boid.rect.x,boid.rect.y)
            return newangle

        return self.angle


    def new_position(self,a_factor,v_factor):
        '''
        Calculate new position from velocity and angle/direction.
        '''
        self.new_angle()
        #self.noise(a_factor,v_factor)
        self.rect.x += self.velocity * np.sin(np.radians(self.angle))
        self.rect.y -= self.velocity * np.cos(np.radians(self.angle))
    #override update() function inherited from boids(?)
    #def update(self):
    #    '''Update Hoik behavoiur.'''


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
        self.Hoik_Group = pygame.sprite.Group()
        self.all_Sprites = pygame.sprite.Group()

    def add_Boid(self,width,height,x_pos,y_pos,angle,color,velocity,proximity):
        '''Add a Boid to the simulation.'''
        newboid = Boid(width,height,x_pos,y_pos,angle,color,velocity,proximity)
        self.Boid_Group.add(newboid)


    def add_Hoik(self,width,height,x_pos,y_pos,angle,color,velocity,proximity):
        '''Add a Hoik to the Simulation.'''
        newhoik = Hoik(width,height,x_pos,y_pos,angle,color,velocity,proximity)
        self.Hoik_Group.add(newhoik)


    def play(self):
        '''begin simulation.'''
        key = pygame.key.get_pressed()

        for i in range(100):
            self.add_Boid(3,3,random.randint(10,self.SCRN_W - 10),random.randint(10,self.SCRN_H - 10),random.randint(0,360),(255,255,255),random.randint(1,2),10)
        self.all_Sprites.add(self.Boid_Group)

        #self.add_Hoik(10,10,random.randint(10,self.SCRN_W - 10),random.randint(10,self.SCRN_H - 10),random.randint(0,360),(255,255,255),1,30)
        #self.all_Sprites.add(self.Hoik_Group)

        while True: #the simulation loop

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        #exits game when pressing ESC
                        pygame.quit()

            for boid in self.Boid_Group.sprites():
                #for hoik in self.Hoik_Group.sprites():
                #    hoik.find_local_boid(boid)

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
