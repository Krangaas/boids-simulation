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

    def PointAngle(self,target_x,target_y):
        '''
        Find angle between two points,
        pointing towards target coordinates (target_x,target_y),
        from own coordinates (self.rect.x,self.rect.y).
        Returns int between 0 and 359.
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
                newangle = int((359 - np.rad2deg(np.arctan(abs(opposite/adjacent)))) % 359)
                #print("Target NW: 360 - %.2f" %(np.rad2deg(np.arctan(abs(opposite/adjacent)))%360))
                #print("%.2f elem in (270,360)\n" %newangle)

            if adjacent < 0:    #lower left
                #target point is SW of start point
                newangle = int(180 + np.rad2deg(np.arctan(abs(opposite/adjacent))) % 359)
                #print("Target SW: 180 + %.2f" %np.rad2deg(np.arctan(abs(opposite/adjacent))))
                #print("%.2f elem in (180,270)" %newangle)
        if opposite < 0:    #right side
            if adjacent > 0:    #upper right
                #target point is NE of start point
                newangle = int(np.rad2deg(np.arctan(abs(opposite/adjacent))) % 359)
                #print("Target NE: %.2f" %np.rad2deg(np.arctan(abs(opposite/adjacent))))
                #print("%.2f elem in (0,90)" %newangle)
            if adjacent < 0: #lower right
                #target point is SE of start point
                newangle = int((180 - np.rad2deg(np.arctan(abs(opposite/adjacent)))) % 359)
                #print("Target SE: 180 - %.2f" %np.rad2deg(np.arctan(abs(opposite/adjacent))))
                #print("%.2f elem in (90,180)" %newangle)

        return int(newangle)



class Boid(Rectangle):
    '''
    Boid object representation, derived from Rectangle class.
    '''

    def __init__(self,width,height,x_pos,y_pos,color,angle,velocity,proximity):
        '''Create a Boid.'''
        super().__init__(width,height,x_pos,y_pos,color,angle,velocity,proximity)

        self.local_group = pygame.sprite.Group()
        self.hoik_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.MAX_SPEED = 2.0
        self.MIN_SPEED = 1.0


    def find_local_object(self,other):
        '''
        Take in an object derived from Rectangle,
        check if object is in proximity.
        If true, find out if object is boid or hoik and add to a group.
        '''
        x_dist = abs(self.rect.centerx - other.rect.centerx) #find absolute dist along x-axis from centers
        y_dist = abs(self.rect.centery - other.rect.centery) #find absolute dist along y-axis from centers

        if other.__class__.__name__ == "Boid":
            if x_dist < self.width/2 + self.proximity:
                self.local_group.add(other)
                return
            if y_dist < self.height/2 + self.proximity:
                self.local_group.add(other)
                return

        if other.__class__.__name__ == "Hoik":
            if x_dist < self.width/2 + self.proximity:
                self.hoik_group.add(other)
                return

            if y_dist < self.height/2 + self.proximity:
                self.hoik_group.add(other)
                return

        if other.__class__.__name__ == "Obstacle":
            if x_dist <= self.width/2 + other.width/2 + 1:
                self.obstacle_group.add(other)
                return

            if y_dist <= self.height/2 + other.height/2 + 1:
                self.obstacle_group.add(other)
                return
        else:
            return


    def local_boid_center(self):
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


    def local_boid_vel(self):
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


    def local_boid_dir(self):
        '''Return angle in degrees pointing towards average direction of local boids.'''
        if len(self.local_group.sprites()) == 0:
            return self.angle

        newangle = 0.0
        for boid in self.local_group.sprites():
            newangle += boid.angle

        newangle = int((newangle)/len(self.local_group.sprites()) % 359)
        return newangle


    def avoid_nearest_boid(self):
        '''Return angle in degrees pointing away from nearest boid.'''
        if len(self.local_group.sprites()) == 0:
            return 0

        closest_boid = pygame.sprite.Group()
        smallest_h = self.width/2 + self.proximity #extent of local group
        for boid in self.local_group.sprites():
            x_dist = abs(self.rect.centerx - boid.rect.centerx)
            y_dist = abs(self.rect.centery - boid.rect.centery)
            h = np.sqrt(np.hypot(x_dist,y_dist)) #find hypotenuse defined by dist in x- and y-dir between boids
            if h < smallest_h:
                smallest_h = h
                closest_boid.empty() #remove previous boid
                closest_boid.add(boid)

        target = closest_boid.sprites()
        if len(target) > 0:
            if smallest_h < np.hypot(self.width+self.proximity/2,self.height+self.proximity/2):
                newangle = - self.PointAngle(target[0].rect.x,target[0].rect.y)
                return newangle
            else:
                return self.angle
        else:
            return self.angle
        return self.angle


    def avoid_nearest_obstacle(self):
        '''Return angle pointing away from obstacle'''
        if len(self.obstacle_group.sprites()) == 0:
            return self.angle

        else:
            closest_obstacle = pygame.sprite.Group()
            smallest_h = 100 #extent of local group
            for obstacle in self.obstacle_group.sprites():
                x_dist = abs(self.rect.centerx - obstacle.rect.centerx)
                y_dist = abs(self.rect.centery - obstacle.rect.centery)
                h = np.sqrt(np.hypot(x_dist,y_dist)) #find hypotenuse defined by dist in x- and y-dir between boids
                if h < smallest_h:
                    smallest_h = h
                    closest_obstacle.empty() #remove previous boid
                    closest_obstacle.add(obstacle)


            target = closest_obstacle.sprites()
            if len(target) > 0:
                newangle = - self.PointAngle(target[0].rect.x,target[0].rect.y)
                return newangle
                print()
            return self.angle


    def avoid_nearest_hoik(self):
        '''Return angle in degrees pointing away from nearest hoik.'''
        if len(self.hoik_group.sprites()) == 0:
            return self.angle

        closest_hoik = pygame.sprite.Group()
        smallest_h = self.width/2 + self.proximity

        for hoik in self.hoik_group.sprites():
            x_dist = abs(self.rect.centerx - hoik.rect.centerx)
            y_dist = abs(self.rect.centery - hoik.rect.centery)
            h = np.sqrt(np.hypot(x_dist,y_dist)) #find hypotenuse defined by dist in x- and y-dir between hoiks
            if h < smallest_h:
                smallest_h = h
                closest_hoik.empty() #remove previous hoik
                closest_hoik.add(hoik)

        target = closest_hoik.sprites()
        if len(target) > 0:
            newangle = - self.PointAngle(target[0].rect.x,target[0].rect.y)
            return newangle
        else:
            return self.angle
        return self.angle


    def new_angle(self,avg_x,avg_y):
        '''
        Find new angle based on mean of other angles.
        '''
        #avoid_hoik = self.avoid_nearest_hoik()
        #avoid_obstacle = self.avoid_nearest_obstacle

        if len(self.obstacle_group.sprites()) > 0:
            newangle = self.avoid_nearest_obstacle()
            return newangle

        if len(self.hoik_group.sprites()) > 0:
            newangle = self.avoid_nearest_hoik()
            return newangle

        else:
            center = self.PointAngle(avg_x,avg_y)  #angle towards average center of local group
            dir = self.local_boid_dir()            #average angle of local group
            avoid_boid = self.avoid_nearest_boid() #angle away from closest boid in group

            newangle = int((dir + avoid_boid*2 + center*10)/4 % 359)
            return newangle
        return


    def new_velocity(self):
        '''this function takes the mean of velocities'''
        newvelocity = ((self.angle+self.local_boid_vel())/2)

        if newvelocity > self.MAX_SPEED:
            newvelocity = self.MAX_SPEED
        if newvelocity < self.MIN_SPEED:
            newvelocity = self.MIN_SPEED

        return newvelocity


    def new_position(self,a_factor=0.0,v_factor=0.0):
        '''
        Calculate new position from velocity and angle/direction.
        '''
        avg_x, avg_y = self.local_boid_center()
        self.angle = self.new_angle(avg_x,avg_y)

        self.velocity = self.new_velocity()
        #self.angle, self.velocity = self.noise(a_factor,v_factor) #add noise to velocity and direction

        self.rect.x += self.velocity * np.sin(np.radians(self.angle))
        self.rect.y -= self.velocity * np.cos(np.radians(self.angle))

        #empty local_group here so that hoik can inherit update() without deleting its local_group
        self.local_group.empty()
        self.obstacle_group.empty()
        self.hoik_group.empty()


    def noise(self,a,v):
        '''this function adds a noise coefficient to the velocity and direction of the boid'''
        noisyangle = (random.randint((self.angle - a),(self.angle + a))) % 359
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
        if self.rect.x < 0.0 - self.width + 50:
            self.rect.x = SCREEN_WIDTH + self.width - 10 -50
            #self.angle = -self.angle
            #self.rect.x = 51
        #right wall collide
        if self.rect.x > SCREEN_WIDTH + self.width - 50:
            self.rect.x = 0.0 - self.width + 10 + 50
            #self.angle= -self.angle
            #self.rect.x = SCREEN_WIDTH - 51
        #roof collide
        if self.rect.y < 0.0 - self.height + 50:
            self.rect.y = SCREEN_HEIGHT + self.height - 10 - 50
            #self.angle = 180 - self.angle
            #self.rect.y = 51
        #bottom collide
        if self.rect.y > SCREEN_HEIGHT + self.height - 50:
            self.rect.y = 0.0 - self.height + 10 + 50
            #self.angle = 180 - self.angle
            #self.rect.y = SCREEN_HEIGHT - 50


class Hoik(Boid):
    '''Hoik object representation, derived from Boid class.'''

    def __init__(self,width,height,x_pos,y_pos,color,angle,velocity,proximity):
        '''Create a Hoik.'''
        super().__init__(width,height,x_pos,y_pos,color,angle,velocity,proximity)
        self.MAX_SPEED = 6.0
        self.MIN_SPEED = 1.0


    def new_angle(self):
        '''
        Find angle pointing towards nearest boid in local group,
        return float.
        '''
        if len(self.local_group.sprites()) == 0:
            return self.angle

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
        if len(target) > 0:
            newangle = self.PointAngle(target[0].rect.x,target[0].rect.y)
            target[0].image.fill((255,0,0)) #make the prey stand out.
            return newangle
        else:
            return self.angle


    def new_position(self,a_factor,v_factor):
        '''
        Calculate new position from velocity and angle/direction.
        '''
        self.angle = self.new_angle()
        self.noise(a_factor,v_factor)
        self.rect.x += self.velocity * np.sin(np.radians(self.angle))
        self.rect.y -= self.velocity * np.cos(np.radians(self.angle))


class Obstacle(Rectangle):
    '''Obstacle object representation, derived from Rectangle class.'''

    def __init__(self,width,height,x_pos,y_pos,color):
        '''Create an Obstacle.'''
        super().__init__(width,height,x_pos,y_pos,color)


class Simulation:
    '''The Simulation class'''

    def __init__(self,SCRN_W,SCRN_H):
        '''Initialize pygame, display and sprite Groups.'''
        pygame.init()
        self.SCRN_W = SCRN_W
        self.SCRN_H = SCRN_H
        SCREEN_SIZE = self.SCRN_W, self.SCRN_H
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.FPS = 20
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
        newobstacle = Obstacle(width,height,x_pos,y_pos,color)
        self.Obstacle_Group.add(newobstacle)


    def play(self,n_boids,n_hoiks,n_obstacles):
        '''Begin simulation.'''
        key = pygame.key.get_pressed()

        for i in range(n_boids):
            self.add_Boid(3,3,random.randint(3,self.SCRN_W - 3),random.randint(3,self.SCRN_H - 3),(255,255,255),random.randint(0,359),random.randint(1,2),20)
        self.all_Sprites.add(self.Boid_Group)

        for j in range(n_hoiks):
            self.add_Hoik(10,10,random.randint(10,self.SCRN_W - 10),random.randint(10,self.SCRN_H - 10),(255,255,255),random.randint(0,359),2,20)
        self.all_Sprites.add(self.Hoik_Group)

        for k in range(n_obstacles):
            self.add_Obstacle(20,20,random.randint(20,self.SCRN_W - 20),random.randint(20,self.SCRN_H - 20),(255,255,255))
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
                boid.image.fill((255,255,255))
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

            pygame.sprite.groupcollide(self.Boid_Group,self.Hoik_Group,True,False)
            self.clock.tick(self.FPS)
            self.screen.fill((0,0,0))
            self.all_Sprites.update()
            self.all_Sprites.draw(self.screen)
            pygame.display.flip()


sim = Simulation(SCREEN_WIDTH,SCREEN_HEIGHT)
sim.play(100,0,0)
