import pygame
from utils import *
from colors import *

########################################
####        Global Consts           ####
########################################
WIDTH,HEIGHT = 800,800
FPS = 60

MIN_SPEED = 3.5

pygame.init()

WIN = pygame.display.set_mode((WIDTH,HEIGHT))
UFO = scale_image(pygame.image.load("imgs/FlyingObject.png"),0.03)
OBSTACLE = scale_image(pygame.image.load("imgs/MetalObstacle.png"),0.2)
FUEL_CAN = scale_image(pygame.image.load("imgs/MetalObstacle.png"),0.05)
COIN = scale_image(pygame.image.load("imgs/MetalObstacle.png"),0.03)
GAME_FONT = pygame.font.SysFont("Cambria", 25)


########################################
####        Global Variables        ####
########################################

pygame.display.set_caption("UFO game")
clock = pygame.time.Clock()

coinsValue = 0

class TextMsg(pygame.sprite.Sprite):
    def __init__(self,x,y,getText,color):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.color = color
        self.getText = getText
        self.image = GAME_FONT.render(self.getText(), 1, color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        # objects.append(self)
    
    def update(self):
        self.image = GAME_FONT.render(self.getText(),1,self.color)

class World:
    gravity = 9.8
    airFriction = 0.2   # ms-2 per ms-1
    xMultiplier = 5.8
    yMultiplier = 10.5


class AbstractUFO(pygame.sprite.Sprite):
    x = 0
    y = 0
    img = UFO
    mass = 50.0
    fuelCap = 10.0
    fuelLevel = 10.0
    fuelEfficency = 0.999
    enginForce = 1000.0
    acceleration = enginForce/mass
    liftingEnginCount = 1
    HorizontalAirFrictionMultiplier = 0.3
    VerticalAirFrictionMultiplier = 0.5
    speedX = 0.0
    speedY = 0.0
    prevPos = (x,y)
    e = 0.5
    isColidedLeft = False
    isColidedRight = False
    isColidedTop = False
    isColidedBottom = False

    def __init__(self,world):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self.image = self.img.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.topleft = (self.x,self.y)

    def fuelRefill(self,fuelCan):
        newFuelLevel = 0.0
        for can in fuelCan:
            newFuelLevel += can.fuelLevel
        if self.fuelLevel + newFuelLevel >= self.fuelCap:
            self.fuelLevel = self.fuelCap
        else:
            self.fuelLevel += newFuelLevel
        
    def collide(self,colisions):
        if not (self.isColidedTop or self.isColidedBottom or self.isColidedLeft or self.isColidedRight):
            for obs in colisions:
                print(obs.rect.left,obs.rect.right,obs.rect.top,obs.rect.bottom,self.rect.left,self.rect.right,self.rect.top,self.rect.bottom)
                offset = max(self.rect.right - obs.rect.left,self.rect.bottom - obs.rect.top)/5
                self.prevPos = (self.x,self.y)
                if obs.rect.bottom > self.rect.top and obs.rect.bottom < self.rect.top+offset:
                    print('collision at bottom')
                    self.speedY = (self.speedY)*-1*((obs.e+self.e)/2)
                    self.y = self.prevPos[1]+1
                    self.isColidedTop = True
                elif obs.rect.top < self.rect.bottom and obs.rect.top > self.rect.bottom-offset:
                    print('collision at top')
                    self.speedY = (self.speedY)*-1*((obs.e+self.e)/2)
                    print('speedY',self.speedY)
                    if self.speedY < 1.5:
                        print('speedY set to 0')
                        self.speedY = 0.0
                    # self.y = obs.rect.top - self.img.get_height()
                    self.y = self.prevPos[1]
                    self.isColidedBottom = True
                if obs.rect.left < self.rect.right and obs.rect.left > self.rect.right-offset:
                    print('collision at left')
                    self.speedX = (self.speedX)*-1*((obs.e+self.e)/2)
                    # self.x = obs.rect.left - self.img.get_width()
                    self.x = self.prevPos[0]-1
                    self.isColidedRight = True
                elif obs.rect.right > self.rect.left and obs.rect.right < self.rect.left+offset:
                    print('collision at right')
                    self.speedX = (self.speedX)*-1*((obs.e+self.e)/2)
                    # self.x = obs.rect.right
                    self.x = self.prevPos[0]+1
                    self.isColidedLeft = True

                
        
    
    def noColied(self):
        if self.isColidedTop or self.isColidedBottom or self.isColidedLeft or self.isColidedRight:
            self.isColidedLeft = False
            self.isColidedRight = False
            self.isColidedTop = False
            self.isColidedBottom = False

    def shiftXPosition(self,deltaX,deltaT):
        tmp = self.x + deltaX*self.world.xMultiplier
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
        tmp = self.y - deltaY*self.world.yMultiplier
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
        if self.fuelLevel>0 and not self.isColidedLeft:
            dt = clock.get_time()/1000.0
            dx = self.speedX * dt + (abs(self.world.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX)+(-1*self.acceleration))*(dt**2)
            # print('dx',dx)
            self.shiftXPosition(dx,dt)
            self.burnFuel()
        else:
            self.burnLinearInertiaX()

    def moveRight(self):
        if self.fuelLevel>0 and not self.isColidedRight:
            dt = clock.get_time()/1000.0
            dx = self.speedX * dt + (-1*abs(self.world.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX)+(self.acceleration))*(dt**2)
            # print('dx',dx)
            self.shiftXPosition(dx,dt)
            self.burnFuel()
        else:
            self.burnLinearInertiaX()

    def moveUp(self):
        if self.fuelLevel>0 and not self.isColidedTop:
            dt = clock.get_time()/1000.0
            dy = self.speedY * dt + (-1*abs(self.world.airFriction * self.VerticalAirFrictionMultiplier * self.speedY)+(self.liftingEnginCount*self.acceleration - self.world.gravity))*(dt**2)
            # print('dy',dy)
            self.shiftYPosition(dy,dt)
            self.burnFuel(self.liftingEnginCount)
        else:
            self.burnLinearInertiaY()


    def burnLinearInertiaX(self):
        dt = clock.get_time()/1000.0
        if self.speedX > MIN_SPEED:
            dx = self.speedX * dt + (-1*abs(self.world.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX))*(dt**2)
            self.shiftXPosition(dx,dt)
        elif self.speedX < -1* MIN_SPEED:
            dx = self.speedX * dt + (abs(self.world.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX))*(dt**2)
            self.shiftXPosition(dx,dt)
        else:
            self.speedX = 0.0
        # print('burn',self.speedX)

    def burnLinearInertiaY(self):
        if abs(self.speedY) - 0.8 > 0.0 or not self.isColidedBottom:
            dt = clock.get_time()/1000.0
            if self.speedY <= 0.0:
                dy = self.speedY * dt + (abs(self.world.airFriction * self.VerticalAirFrictionMultiplier * self.speedY)-self.world.gravity)*(dt**2)
                self.shiftYPosition(dy,dt)
            elif self.speedY > 0.0:
                dy = self.speedY * dt + (-1*abs(self.world.airFriction * self.VerticalAirFrictionMultiplier * self.speedY)-self.world.gravity)*(dt**2)
                self.shiftYPosition(dy,dt)
            # print('burnY',self.speedY)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pygame.Surface((10,10))
        self.rect = self.image.get_rect()
        self.image.fill((255,0,0))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self,color):
        pos = pygame.mouse.get_pos()
        self.rect.center = (pos)
        self.image.fill(color)

class obstacle(pygame.sprite.Sprite):
    def __init__(self,x,y,image,e):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        self.mask = pygame.mask.from_surface(self.image)
        self.e = e


class FuelCan(pygame.sprite.Sprite):
    def __init__(self,x,y,image,fuelLevel):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        self.mask = pygame.mask.from_surface(self.image)
        self.fuelLevel = fuelLevel

class Coins(pygame.sprite.Sprite):
    def __init__(self,x,y,image,value):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        self.mask = pygame.mask.from_surface(self.image)
        self.value = value

class Level1UFO(AbstractUFO):
    def __init__(self,x,y,world):
        super().__init__(world)
        self.x = x
        self.y = y



world = World()
ufo = Level1UFO(400,500,world)
scoreLabmda = lambda: 'Score: {}'.format(0)
fuelLambda = lambda: 'Fuel: {:.7}/{:.5}'.format(ufo.fuelLevel,ufo.fuelCap)
score = TextMsg(5,0,scoreLabmda,WHITE)
fuel = TextMsg(5,28,fuelLambda,WHITE)
bullet = Bullet(0,0)
obs1 = obstacle(100,100,OBSTACLE,0.1)
obs2 = obstacle(400,600,OBSTACLE,0.8)
fuelcan1 = FuelCan(550,500,FUEL_CAN,5.0)
coin = Coins(200,200,COIN,1)

bullet_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
fuel_can_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()

bullet_group.add(bullet)
ufo_group.add(ufo)
text_group.add(score)
text_group.add(fuel)
obstacle_group.add(obs1)
obstacle_group.add(obs2)
fuel_can_group.add(fuelcan1)
coins_group.add(coin)

color = RED

def draw(win):
    WIN.fill(DARK_TEAL)

    if pygame.sprite.spritecollide(ufo,obstacle_group,False):
        colisions = pygame.sprite.spritecollide(ufo,obstacle_group,False,pygame.sprite.collide_mask)
        if colisions:
            ufo.collide(colisions)
    else:
        ufo.noColied()
    
    fuelColisions = pygame.sprite.spritecollide(ufo,fuel_can_group,True)
    if fuelColisions:
        ufo.fuelRefill(fuelColisions)

    coinsColisions = pygame.sprite.spritecollide(ufo,coins_group,True)
    if coinsColisions:
        global coinsValue
        for c in coinsColisions:
            coinsValue += c.value


        
    
    bullet_group.update(color)
    ufo_group.update()
    text_group.update()

    ufo_group.draw(WIN)
    bullet_group.draw(WIN)
    text_group.draw(WIN)
    obstacle_group.draw(WIN)
    fuel_can_group.draw(WIN)
    coins_group.draw(WIN)

    pygame.display.update()

run = True
while run:
    clock.tick(FPS)
    draw(WIN)


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

    elif keys[pygame.K_RIGHT]:
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