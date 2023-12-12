                             ##  Assignment 2  ##
                                ## INF-1400 ##
                              ##  Magus Kanck ##
                                ##  mka080  ##
import sys
import pygame
import numpy as np
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
FPS = 20

##BOID ATTRIBUTES##
NUMBER_OF_BOIDS = 100
BOID_MAX_SPEED = 2.0
BOID_MIN_SPEED = 1.0
BOID_SIZE = 3
BOID_PROXIMITY = 100
AVOID_BOID_FACTOR = 1
GROUP_TO_CENTER_FACTOR = 10
GROUP_DIRECTION_FACTOR = 1
BOID_ANGLE_NOISE = 1
BOID_VELOCITY_NOISE = 1.0

##HOIK ATTRIBUTES##
NUMBER_OF_HOIKS = 1
HOIK_MAX_SPEED = 3.0
HOIK_MIN_SPEED = 2.0
HOIK_SIZE = 10
HOIK_PROXIMITY = 20
HOIK_ANGLE_NOISE = 5
HOIK_VELOCITY_NOISE = 0.0

##OBSTACLE ATTRIBUTES##
NUMBER_OF_OBSTACLES = 5
OBSTACLE_SIZE = 20


class Rectangle(pygame.sprite.Sprite):
    '''
    Rectangle object representation, derived from pygame.Sprite class.
    This class requires 7 inputs:
    width: int
    height: int
    x-axis position: int
    y-axis position: int
    angle (optional): int between 0 and 359
    proximity (optional): int
    velocity (optional): int or float
    color: 3-dim tuple, with int values between 0 and 255
    '''

    def __init__(self,width,height,x_pos,y_pos,color,angle=0,velocity=0,proximity=0):
        '''Create a rectangle.'''
        #call parent class
        super().__init__()      #super() finds next class in search list
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
        self.velocity = velocity
        self.proximity = proximity

        self.local_group = pygame.sprite.Group()
        self.hoik_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()


    def find_local_object(self,other):
        '''
        Take in an object derived from Rectangle, i.e. has rect attribute,
        find out if object is boid, hoik or obstacle and add to respective group,
        check if object is in proximity, if true add to respective group.
        '''

        x_dist = abs(self.rect.centerx - other.rect.centerx) #find absolute dist along x-axis from centers
        y_dist = abs(self.rect.centery - other.rect.centery) #find absolute dist along y-axis from centers
        dist = np.hypot(x_dist,y_dist)

        if other.__class__.__name__ == "Boid":
            if dist < np.hypot(self.width/2 + self.proximity, self.height/2 + self.proximity):
                self.local_group.add(other)
                return

        if other.__class__.__name__ == "Hoik":
            if dist < np.hypot(self.width/2 + self.proximity, self.height/2 + self.proximity):
                self.hoik_group.add(other)
                return

        if other.__class__.__name__ == "Rectangle":
            if dist <= np.hypot(self.width/2 + other.width/2 + 1, self.height/2 + other.height/2 + 1):
                self.obstacle_group.add(other)
                return
        else:
            return


    def PointAngle(self,target_x,target_y):
        '''
        Find angle between two points,
        pointing towards target coordinates (target_x,target_y),
        from own coordinates (self.rect.x,self.rect.y).
        Returns int between 0 and 359.
        '''

        opposite = self.rect.x - target_x
        adjacent = self.rect.y - target_y

        if opposite == 0 or adjacent == 0:
            return self.angle

        if opposite > 0:    #left side
            if adjacent > 0:    #upper left
                #target point is NW of start point
                newangle = int((359 - np.rad2deg(np.arctan(abs(opposite/adjacent)))) % 359)

            if adjacent < 0:    #lower left
                #target point is SW of start point
                newangle = int(180 + np.rad2deg(np.arctan(abs(opposite/adjacent))) % 359)

        if opposite < 0:    #right side
            if adjacent > 0:    #upper right
                #target point is NE of start point
                newangle = int(np.rad2deg(np.arctan(abs(opposite/adjacent))) % 359)

            if adjacent < 0: #lower right
                #target point is SE of start point
                newangle = int((180 - np.rad2deg(np.arctan(abs(opposite/adjacent)))) % 359)

        return int(newangle)


class Boid(Rectangle):
    '''
    Boid object representation, derived from Rectangle class.
    '''

    def __init__(self,width,height,x_pos,y_pos,color,angle,velocity,proximity):
        '''Create a Boid.'''
        super().__init__(width,height,x_pos,y_pos,color,angle,velocity,proximity)
        self.MAX_SPEED = BOID_MAX_SPEED
        self.MIN_SPEED = BOID_MIN_SPEED


    def local_boid_center(self):
        '''
        Find angle pointing towards average center of boids in local group,
        return int between 0 and 359.
        '''

        list_x = []
        list_y = []
        for boid in self.local_group.sprites():
            list_x.append(boid.rect.x)
            list_y.append(boid.rect.y)

        avg_x = np.mean(list_x)
        avg_y = np.mean(list_y)

        newangle = self.PointAngle(avg_x,avg_y)
        return newangle


    def local_boid_vel(self):
        '''
        Find average velocity of boids in local group,
        return float greater than, or equal to, zero.
        '''

        newvelocity = 0.0
        for boid in self.local_group.sprites():
            newvelocity += boid.velocity

        newvelocity = (newvelocity)/len(self.local_group.sprites()) #take the mean of all velocities in group
        return newvelocity


    def local_boid_dir(self):
        '''
        Find average direction of boids in local group,
        return int between 0 and 359.
        '''
        if len(self.local_group.sprites()) == 0:
            return self.angle

        newangle = 0.0
        for boid in self.local_group.sprites():
            newangle += boid.angle

        newangle = int((newangle)/len(self.local_group.sprites()) % 359)
        return newangle


    def avoid_nearest_boid(self):
        '''
        Find angle pointing away from nearest boid in local group,
        return int between 0 and 359.
        '''

        closest_boid = pygame.sprite.Group()
        smallest_h = np.hypot(self.width+1,self.height+1)

        for boid in self.local_group.sprites():
            x_dist = abs(self.rect.centerx - boid.rect.centerx)
            y_dist = abs(self.rect.centery - boid.rect.centery)
            h = np.hypot(x_dist,y_dist) #find hypotenuse defined by dist in x- and y-dir between boids
            if h < smallest_h:
                smallest_h = h
                closest_boid.empty() #remove previous boid
                closest_boid.add(boid)


        if len(closest_boid.sprites()) > 0:
            newangle = - self.PointAngle(closest_boid.sprites()[0].rect.x,closest_boid.sprites()[0].rect.y)
            return newangle
        else:
            return self.angle


    def avoid_nearest_obstacle(self):
        '''
        Find angle pointing away from nearest obstacle,
        return int between 0 and 359.
        '''

        if len(self.obstacle_group.sprites()) > 1:  #if there are more obstacles, find nearest one
            closest_obstacle = pygame.sprite.Group()
            smallest_h = np.hypot(self.width/2 + self.obstacle_group.sprites()[0].width/2 + 1,self.height/2 + self.obstacle_group.sprites()[0].height/2 + 1)
            for obstacle in self.obstacle_group.sprites():
                x_dist = abs(self.rect.centerx - obstacle.rect.centerx)
                y_dist = abs(self.rect.centery - obstacle.rect.centery)
                h = np.hypot(x_dist,y_dist)

                if h <= smallest_h:
                    smallest_h = h
                    closest_obstacle.empty() #remove previous boid
                    closest_obstacle.add(obstacle)

            newangle = - self.PointAngle(closest_obstacle.sprites()[0].rect.x,closest_obstacle.sprites()[0].rect.y)
            return newangle

        else:
            newangle = - self.PointAngle(self.obstacle_group.sprites()[0].rect.x,self.obstacle_group.sprites()[0].rect.y)
            return newangle


    def avoid_nearest_hoik(self):
        '''
        Find angle pointing away from nearest hoik,
        Return int between 0 and 359.
        '''
        if len(self.hoik_group.sprites()) > 1:  #if more than 1 hoik, find nearest hoik
            closest_hoik = pygame.sprite.Group()
            smallest_h = np.hypot(self.width/2 + self.proximity,self.height/2 + self.proximity)

            for hoik in self.hoik_group.sprites():
                x_dist = abs(self.rect.centerx - hoik.rect.centerx)
                y_dist = abs(self.rect.centery - hoik.rect.centery)
                h = np.hypot(x_dist,y_dist) #find hypotenuse defined by dist in x- and y-dir between rects

                if h < smallest_h:
                    smallest_h = h
                    closest_hoik.empty() #remove previous hoik
                    closest_hoik.add(hoik)

            newangle = - self.PointAngle(closest_hoik.sprites()[0].rect.x,closest_hoik.sprites()[0].rect.y)
            return newangle

        else:
            newangle = - self.PointAngle(self.hoik_group.sprites()[0].rect.x,self.hoik_group.sprites()[0].rect.y)
            return newangle


    def new_angle(self):
        '''
        Find new angle based on rules of boids,
        return int between 0 and 359.
        '''

        if len(self.obstacle_group.sprites()) > 0: #boids should avoid obstacles
            newangle = self.avoid_nearest_obstacle()
            return newangle

        elif len(self.hoik_group.sprites()) > 0: #boids should flee from hoiks
            newangle = self.avoid_nearest_hoik()
            return newangle

        elif len(self.local_group.sprites()) > 0:
            avoid = self.avoid_nearest_boid() * AVOID_BOID_FACTOR      #angle away from closest boid in group
            center = self.local_boid_center() * GROUP_TO_CENTER_FACTOR #angle towards average center of local group
            dir = self.local_boid_dir() * GROUP_DIRECTION_FACTOR       #average angle of local group

            n = 0
            if avoid != 0:
                n += 1
            if center != 0:
                n += 1
            if dir != 0:
                n += 1
            if n == 0:
                return self.angle

            else:
                newangle = int(((dir + avoid + center)/n)% 359)
                return newangle

        else:
            return self.angle


    def new_velocity(self):
        '''
        Find average velocity of boids in local group,
        return float.
        '''

        if len(self.local_group.sprites()) > 0:
            newvelocity = ((self.angle+self.local_boid_vel())/2)
            if newvelocity > self.MAX_SPEED:
                newvelocity = self.MAX_SPEED
            if newvelocity < self.MIN_SPEED:
                newvelocity = self.MIN_SPEED
            return newvelocity

        else:
            return self.velocity


    def new_position(self):
        '''
        Calculate new position from velocity and angle/direction.
        '''
        self.angle = self.new_angle()
        self.velocity = self.new_velocity()
        self.angle, self.velocity = self.noise(BOID_ANGLE_NOISE,BOID_VELOCITY_NOISE) #add noise to velocity and direction

        self.rect.x += self.velocity * np.sin(np.radians(self.angle))
        self.rect.y -= self.velocity * np.cos(np.radians(self.angle))


    def noise(self,a,v):
        '''
        Function takes two ints a and v,
        returns two values:
        noisyangle: int between 0 and 359
        noisyvelocity: float between -v and v
        '''
        noisyangle = (random.randint((self.angle - a),(self.angle + a))) % 359
        noisyvelocity = self.velocity + random.uniform(-v,v)

        if noisyvelocity > self.MAX_SPEED:
            noisyvelocity = self.MAX_SPEED
        if noisyvelocity < self.MIN_SPEED:
            noisyvelocity = self.MIN_SPEED
        return noisyangle, noisyvelocity


    def update(self):
        '''Update Object behaviour.'''

        self.new_position()    #calculate new position
        #left wall collide
        if self.rect.x < 0.0 - self.width:
            self.rect.x = SCREEN_WIDTH + self.width - 1
            #self.angle = -self.angle
            #self.rect.x = 51
        #right wall collide
        if self.rect.x > SCREEN_WIDTH + self.width:
            self.rect.x = 0.0 - self.width + 1
            #self.angle= -self.angle
            #self.rect.x = SCREEN_WIDTH - 51
        #roof collide
        if self.rect.y < 0.0 - self.height:
            self.rect.y = SCREEN_HEIGHT + self.height - 1
            #self.angle = 180 - self.angle
            #self.rect.y = 51
        #bottom collide
        if self.rect.y > SCREEN_HEIGHT + self.height:
            self.rect.y = 0.0 - self.height + 1
            #self.angle = 180 - self.angle
            #self.rect.y = SCREEN_HEIGHT - 50

        self.local_group.empty()
        self.obstacle_group.empty()
        self.hoik_group.empty()


class Hoik(Boid):
    '''Hoik object representation, derived from Boid class.'''

    def __init__(self,width,height,x_pos,y_pos,color,angle,velocity,proximity):
        '''Create a Hoik.'''
        super().__init__(width,height,x_pos,y_pos,color,angle,velocity,proximity)
        self.MAX_SPEED = HOIK_MAX_SPEED
        self.MIN_SPEED = HOIK_MIN_SPEED


    def seek_nearest_boid(self):
        '''
        Find angle pointing towards nearest boid in local group,
        return int between 0 and 359.
        '''

        closest_boid = pygame.sprite.Group()
        closest_boid.empty()
        smallest_h = self.width/2 + self.proximity #extent of local group

        for boid in self.local_group.sprites():
            x_dist = abs(self.rect.centerx - boid.rect.centerx)
            y_dist = abs(self.rect.centery - boid.rect.centery)
            h = np.sqrt(np.hypot(x_dist,y_dist))

            if h < smallest_h:
                smallest_h = h
                closest_boid.empty() #remove previous boid
                closest_boid.add(boid)

        target = closest_boid.sprites()
        newangle = self.PointAngle(target[0].rect.x,target[0].rect.y)
        target[0].image.fill((255,0,0)) #make the prey stand out to the viewer
        return newangle


    def new_angle(self):
        '''
        Calculate new angle based on the rules of hoiks.
        Return int between 0 and 359.
        '''

        if len(self.obstacle_group.sprites()) > 0:  #if there is a nearby obstacle, avoid it
            return self.avoid_nearest_obstacle()

        if len(self.local_group.sprites()) > 0: #if there is a nearby boid, hunt it
            return self.seek_nearest_boid()

        else:   #continue previous path
            return self.angle


    def new_position(self):

        '''
        Calculate new position from velocity and angle/direction.
        '''

        self.angle = self.new_angle()
        self.angle, self.velocity = self.noise(HOIK_ANGLE_NOISE,HOIK_VELOCITY_NOISE)
        self.rect.x += self.velocity * np.sin(np.radians(self.angle))
        self.rect.y -= self.velocity * np.cos(np.radians(self.angle))


class Simulation:
    '''The Simulation class'''

    def __init__(self):
        '''Initialize pygame, display and sprite Groups.'''
        pygame.init()
        SCREEN_SIZE = SCREEN_WIDTH,SCREEN_HEIGHT
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.FPS = FPS
        self.clock = pygame.time.Clock()
        self.Boid_Group = pygame.sprite.Group()
        self.Hoik_Group = pygame.sprite.Group()
        self.Obstacle_Group = pygame.sprite.Group()
        self.all_Sprites = pygame.sprite.Group()


    def add_Boid(self,width,height,x_pos,y_pos,color,angle,velocity,proximity):
        '''Add a Boid to the simulation.'''
        newboid = Boid(width,height,x_pos,y_pos,color,angle,velocity,proximity)
        self.Boid_Group.add(newboid)


    def add_Hoik(self,width,height,x_pos,y_pos,color,angle,velocity,proximity):
        '''Add a Hoik to the simulation.'''
        newhoik = Hoik(width,height,x_pos,y_pos,color,angle,velocity,proximity)
        self.Hoik_Group.add(newhoik)


    def add_Obstacle(self,width,height,x_pos,y_pos,color):
        '''Add an Obstacle to the simulation.'''
        newobstacle = Rectangle(width,height,x_pos,y_pos,color)
        self.Obstacle_Group.add(newobstacle)


    def play(self):
        '''Begin simulation.'''
        key = pygame.key.get_pressed()

        for i in range(NUMBER_OF_BOIDS):
            self.add_Boid(BOID_SIZE,BOID_SIZE,random.randint(BOID_SIZE, SCREEN_WIDTH - BOID_SIZE),random.randint(BOID_SIZE, SCREEN_HEIGHT - BOID_SIZE),(255,255,255),random.randint(0,359),random.randint(BOID_MIN_SPEED,BOID_MAX_SPEED),BOID_PROXIMITY)
        self.all_Sprites.add(self.Boid_Group)

        for j in range(NUMBER_OF_HOIKS):
            self.add_Hoik(HOIK_SIZE,HOIK_SIZE,random.randint(HOIK_SIZE, SCREEN_WIDTH - HOIK_SIZE),random.randint(HOIK_SIZE,SCREEN_HEIGHT - HOIK_SIZE),(255,255,255),random.randint(0,359),random.randint(HOIK_MIN_SPEED,HOIK_MAX_SPEED),HOIK_PROXIMITY)
        self.all_Sprites.add(self.Hoik_Group)

        for k in range(NUMBER_OF_OBSTACLES):
            self.add_Obstacle(OBSTACLE_SIZE,OBSTACLE_SIZE,random.randint(OBSTACLE_SIZE, SCREEN_WIDTH - OBSTACLE_SIZE),random.randint(OBSTACLE_SIZE,SCREEN_HEIGHT - OBSTACLE_SIZE),(255,255,255))
        self.all_Sprites.add(self.Obstacle_Group)


        while True: #the simulation loop

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        #exits game when pressing ESC
                        pygame.quit()

            for boid in self.Boid_Group.sprites():
                boid.image.fill((255,255,255))  #recolor boids that the hoik lost target of
                for obstacle in self.Obstacle_Group.sprites():
                    boid.find_local_object(obstacle)

                for hoik in self.Hoik_Group.sprites():
                    boid.find_local_object(hoik)
                    hoik.find_local_object(boid)
                    for obstacle in self.Obstacle_Group.sprites():
                        hoik.find_local_object(obstacle)

                for other_boid in self.Boid_Group.sprites():
                    if boid != other_boid:
                        boid.find_local_object(other_boid)
                    else:
                        pass

            pygame.sprite.groupcollide(self.Boid_Group,self.Hoik_Group,True,False) #remove boid if collision with hoik detected
            self.clock.tick(self.FPS)
            self.screen.fill((0,0,0))
            self.all_Sprites.update()
            self.all_Sprites.draw(self.screen)
            pygame.display.flip()



if __name__ == "__main__":
    sim = Simulation()
    sim.play()
