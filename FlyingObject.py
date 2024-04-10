import pygame
import time
import math
from utils import *

########################################
####        Global Consts           ####
########################################
WIDTH,HEIGHT = 800,800
FPS = 30

MIN_SPEED = 3.5


WIN = pygame.display.set_mode((WIDTH,HEIGHT))
UFO = scale_image(pygame.image.load("imgs/FlyingObject.png"),0.03)

########################################
####        Global Variables        ####
########################################
objects = [

]

pygame.display.set_caption("UFO game")
clock = pygame.time.Clock()


class World:
    gravity = 9.8
    airDensity = 1.0
    airFriction = 0.5   # ms-2 per ms-1



class AbstractUFO(World):
    X = 0
    Y = 0
    img = UFO
    mass = 10.0
    fuelCap = 10.0
    fuelLevel = 10.0
    fuelEfficency = 0.1
    enginForce = 2000.0
    acceleration = enginForce/mass
    liftingEnginCount = 2
    speedX = 0.0
    speedY = 0.0
    def __init__(self):
        self.x = self.X
        self.y = self.Y
    
    def moveLeft(self):
        dt = clock.get_time()/1000.0
        dx = self.speedX * dt + (abs(self.airFriction * self.speedX)+(-1*self.acceleration))*(dt**2)
        # print('dx',dx)
        self.x += dx
        self.speedX = dx/dt
        # print('ml',self.speedX)

    def moveRight(self):
        dt = clock.get_time()/1000.0
        dx = self.speedX * dt + (-1*abs(self.airFriction * self.speedX)+(self.acceleration))*(dt**2)
        # print('dx',dx)
        self.x += dx
        self.speedX = dx/dt
        # print('ml',self.speedX)

    def moveUp(self):
        dt = clock.get_time()/1000.0
        dy = self.speedY * dt + (-1*abs(self.airFriction * self.speedY)+(self.liftingEnginCount*self.acceleration - self.gravity))*(dt**2)
        print('dy',dy)
        self.y -= dy
        self.speedY = dy/dt
        print('mu',self.speedY)


    def burnLinearInertiaX(self):
        dt = clock.get_time()/1000.0
        if self.speedX > MIN_SPEED:
            dx = self.speedX * dt + (-1*abs(self.airFriction * self.speedX))*(dt**2)
            self.x += dx
            self.speedX =dx/dt
        elif self.speedX < -1* MIN_SPEED:
            dx = self.speedX * dt + (abs(self.airFriction * self.speedX))*(dt**2)
            self.x += dx
            self.speedX = dx/dt
        else:
            self.speedX = 0.0
        # print('burn',self.speedX)

    def burnLinearInertiaY(self):
        dt = clock.get_time()/1000.0
        if self.speedY <= 0.0:
            dy = self.speedY * dt + (abs(self.airFriction * self.speedY)-self.gravity)*(dt**2)
            print('accd:',abs(self.airFriction * self.speedY)-self.gravity)
            self.y -= dy
            self.speedY = dy/dt
        elif self.speedY > 0.0:
            dy = self.speedY * dt + (-1*abs(self.airFriction * self.speedY)-self.gravity)*(dt**2)
            print('accu:',-1*abs(self.airFriction * self.speedY)-self.gravity)
            self.y -= dy
            self.speedY = dy/dt
        print('burnY',self.speedY)




class Level1UFO(AbstractUFO):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        objects.append(self)

def draw(win,objs):
    WIN.fill((0,0,120))
    for obj in objs:
        win.blit(obj.img,(obj.x,obj.y))

    pygame.display.update()



ufo = Level1UFO(400,500)

run = True
while run:
    clock.tick(FPS)
    draw(WIN,objects)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
            break

    keys = pygame.key.get_pressed()
    
    linearMovementX = False
    linearMovementY = False
    if keys[pygame.K_LEFT]:
        ufo.moveLeft()
        linearMovementX = True

    if keys[pygame.K_RIGHT]:
        ufo.moveRight()
        linearMovementX = True

    if keys[pygame.K_UP]:
        ufo.moveUp()
        linearMovementY = True

    if not linearMovementX:
        ufo.burnLinearInertiaX()
    if not linearMovementY:
        ufo.burnLinearInertiaY()

        



pygame.quit()