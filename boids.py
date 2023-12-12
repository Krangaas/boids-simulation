                             ##  Assignment 2  ##
                                ## INF-1400 ##
                              ##  Magus Kanck ##
                                ##  mka080  ##
import pygame

class Boids(pygame.sprite.Sprite):
    '''Boid object representation'''

    def __init__(self):
        '''Create a Boid'''
        super().__init__()

class Hoids(Boids):
    '''Hoid object representation, derived from Boids'''

    def __init__(self):
        '''Create a Hoid'''
        super().__init__()
        print("ey")

class Obstacle:
    '''Obstacle object representation'''

    def __init__(self):
        '''Create an Obstacle'''
        super().__init__()
        print("ey")
