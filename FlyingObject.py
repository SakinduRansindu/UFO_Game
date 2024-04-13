import pygame
from utils import *

########################################
####        Global Consts           ####
########################################
WIDTH,HEIGHT = 800,800
FPS = 60

MIN_SPEED = 3.5

pygame.init()

WIN = pygame.display.set_mode((WIDTH,HEIGHT))
UFO = scale_image(pygame.image.load("imgs/FlyingObject.png"),0.03)
GAME_FONT = pygame.font.SysFont("Cambria", 25)

# colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (128,0,128)

########################################
####        Global Variables        ####
########################################
objects = [

]

pygame.display.set_caption("UFO game")
clock = pygame.time.Clock()

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
    def __init__(self,world):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self.image = self.img.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.topleft = (self.x,self.y)

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
        if self.fuelLevel>0:
            dt = clock.get_time()/1000.0
            dx = self.speedX * dt + (abs(self.world.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX)+(-1*self.acceleration))*(dt**2)
            # print('dx',dx)
            self.shiftXPosition(dx,dt)
            self.burnFuel()
        else:
            self.burnLinearInertiaX()

    def moveRight(self):
        if self.fuelLevel>0:
            dt = clock.get_time()/1000.0
            dx = self.speedX * dt + (-1*abs(self.world.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX)+(self.acceleration))*(dt**2)
            # print('dx',dx)
            self.shiftXPosition(dx,dt)
            self.burnFuel()
        else:
            self.burnLinearInertiaX()

    def moveUp(self):
        if self.fuelLevel>0:
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


class Level1UFO(AbstractUFO):
    def __init__(self,x,y,world):
        super().__init__(world)
        self.x = x
        self.y = y


world = World()
ufo = Level1UFO(400,500,world)
scoreLabmda = lambda: 'Score: {}'.format(0)
fuelLambda = lambda: 'Fuel: {:.7}/{:.5}'.format(ufo.fuelLevel,ufo.fuelCap)
score = TextMsg(5,0,scoreLabmda,(0,0,0))
fuel = TextMsg(5,28,fuelLambda,(0,0,0))
bullet = Bullet(0,0)

bullet_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()

bullet_group.add(bullet)
ufo_group.add(ufo)
text_group.add(score)
text_group.add(fuel)

color = RED

def draw(win,objs):
    WIN.fill((110,120,150))
    # for obj in objs:
    #     win.blit(obj.img,(obj.x,obj.y))

    if pygame.sprite.spritecollide(ufo,bullet_group,False):
        color = BLUE
        if pygame.sprite.spritecollide(ufo,bullet_group,False,pygame.sprite.collide_mask):
            color = GREEN
    else:
        color = RED
    
    bullet_group.update(color)
    ufo_group.update()
    text_group.update()

    ufo_group.draw(WIN)
    bullet_group.draw(WIN)
    text_group.draw(WIN)

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