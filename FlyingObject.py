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

pygame.init()

WIN = pygame.display.set_mode((WIDTH,HEIGHT))
UFO = scale_image(pygame.image.load("imgs/FlyingObject.png"),0.03)
GAME_FONT = pygame.font.SysFont("Cambria", 25)



########################################
####        Global Variables        ####
########################################
objects = [

]

pygame.display.set_caption("UFO game")
clock = pygame.time.Clock()

class TextMsg:
    def __init__(self,x,y,text,color):
        self.x = x
        self.y = y
        self.color = color
        self.img = GAME_FONT.render(text, 1, color)
        objects.append(self)
    
    def setText(self,text):
        self.img = GAME_FONT.render(text,1,self.color)

class World:
    gravity = 9.8
    airDensity = 1.0
    airFriction = 1.5   # ms-2 per ms-1
    gravityMultiplier = 2.0


class AbstractUFO(World):
    X = 0
    Y = 0
    img = UFO
    mass = 50.0
    fuelCap = 10.0
    fuelLevel = 10.0
    fuelEfficency = 0.99
    enginForce = 2000.0
    acceleration = enginForce/mass
    liftingEnginCount = 2
    HorizontalAirFrictionMultiplier = 1.0
    VerticalAirFrictionMultiplier = 0.5
    speedX = 0.0
    speedY = 0.0
    def __init__(self):
        self.x = self.X
        self.y = self.Y

    def shiftXPosition(self,deltaX,deltaT):
        tmp = self.x + deltaX
        if tmp<0:
            self.speedX = 0.0
            self.x = 0.0
        elif tmp>WIDTH-self.img.get_width():
            self.speedX = 0.0
            self.x = WIDTH-self.img.get_width()
        else:
            self.x = tmp
            self.speedX = deltaX/deltaT
        
    def shiftYPosition(self,deltaY,deltaT):
        tmp = self.y - deltaY
        if tmp<0:
            self.speedY = 0.0
            self.y = 0.0
        elif tmp>HEIGHT-self.img.get_height():
            self.speedY = 0.0
            self.y = HEIGHT-self.img.get_height()
        else:
            self.y = tmp
            self.speedY = deltaY/deltaT

    def burnFuel(self,multiplier=1):
        if self.fuelLevel-(multiplier * (1.0-self.fuelEfficency))>=0.0:
            self.fuelLevel -= (multiplier * (1.0-self.fuelEfficency))
        else:
            self.fuelLevel = 0.0


    
    def moveLeft(self):
        if self.fuelLevel>0:
            dt = clock.get_time()/1000.0
            dx = self.speedX * dt + (abs(self.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX)+(-1*self.acceleration))*(dt**2)
            # print('dx',dx)
            self.shiftXPosition(dx,dt)
            self.burnFuel()
        else:
            self.burnLinearInertiaX()

    def moveRight(self):
        if self.fuelLevel>0:
            dt = clock.get_time()/1000.0
            dx = self.speedX * dt + (-1*abs(self.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX)+(self.acceleration))*(dt**2)
            # print('dx',dx)
            self.shiftXPosition(dx,dt)
            self.burnFuel()
        else:
            self.burnLinearInertiaX()

    def moveUp(self):
        if self.fuelLevel>0:
            dt = clock.get_time()/1000.0
            dy = self.speedY * dt + (-1*abs(self.airFriction * self.VerticalAirFrictionMultiplier * self.speedY)+(self.liftingEnginCount*self.acceleration - self.gravity*self.gravityMultiplier))*(dt**2)
            # print('dy',dy)
            self.shiftYPosition(dy,dt)
            self.burnFuel(self.liftingEnginCount)
        else:
            self.burnLinearInertiaY()


    def burnLinearInertiaX(self):
        dt = clock.get_time()/1000.0
        if self.speedX > MIN_SPEED:
            dx = self.speedX * dt + (-1*abs(self.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX))*(dt**2)
            self.shiftXPosition(dx,dt)
        elif self.speedX < -1* MIN_SPEED:
            dx = self.speedX * dt + (abs(self.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX))*(dt**2)
            self.shiftXPosition(dx,dt)
        else:
            self.speedX = 0.0
        # print('burn',self.speedX)

    def burnLinearInertiaY(self):
        dt = clock.get_time()/1000.0
        if self.speedY <= 0.0:
            dy = self.speedY * dt + (abs(self.airFriction * self.VerticalAirFrictionMultiplier * self.speedY)-self.gravity*self.gravityMultiplier)*(dt**2)
            self.shiftYPosition(dy,dt)
        elif self.speedY > 0.0:
            dy = self.speedY * dt + (-1*abs(self.airFriction * self.VerticalAirFrictionMultiplier * self.speedY)-self.gravity*self.gravityMultiplier)*(dt**2)
            self.shiftYPosition(dy,dt)
        # print('burnY',self.speedY)




class Level1UFO(AbstractUFO):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        objects.append(self)


ufo = Level1UFO(400,500)
score = TextMsg(5,0,'Score: 0',(0,0,0))
fuel = TextMsg(5,28,'Fuel: {:.7}/{:.5}'.format(ufo.fuelLevel,ufo.fuelCap),(0,0,0))


def draw(win,objs):
    fuel.setText('Fuel: {:.7}/{:.5}'.format(ufo.fuelLevel,ufo.fuelCap))
    WIN.fill((110,120,150))
    for obj in objs:
        win.blit(obj.img,(obj.x,obj.y))

    pygame.display.update()

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