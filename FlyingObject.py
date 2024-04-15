import pygame
from utils import *
from colors import *
from loadLevels import *
import json

########################################
####        Global Consts           ####
########################################
WIDTH,HEIGHT = 1200,800
FPS = 32
TILES_RES = 64

MIN_SPEED = 3.5

pygame.init()

WIN = pygame.display.set_mode((WIDTH,HEIGHT))
BACKGROUND = scale_image(pygame.image.load("imgs/lava.png"),1.5)
UFO = scale_image(pygame.image.load("imgs/UFO.png"),0.8)
OBSTACLE = scale_image(pygame.image.load("imgs/MetalObstacle.png"),0.2)
FUEL_CAN = scale_image(pygame.image.load("imgs/fuel.png"),0.7)
COIN = scale_image(pygame.image.load("imgs/chip.png"),0.4)
GAME_OBJECTIVE = scale_image(pygame.image.load("imgs/MetalObstacle.png"),0.1)
GAME_FONT = pygame.font.SysFont("Cambria", 25)
OFFSET = 600
CAM_BOX = pygame.Rect(100,0,WIDTH - OFFSET,HEIGHT)
MAX_OFFSET = 0
MIN_OFFSET = -232


# load level data 

json_data = open('levels/level3.tmj').read()
data = json.loads(json_data)
del(json_data)


########################################
####        Global Variables        ####
########################################

pygame.display.set_caption("UFO game")
clock = pygame.time.Clock()
coinsValue = 0
current_offset = 0

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

    def __init__(self,img,world):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self.img = img
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
                # offset = max(self.rect.right - obs.rect.left,self.rect.bottom - obs.rect.top)/5
                offset = max([self.speedX*5,self.speedY*5,10])
                print('offset',offset)
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
    def update(self):
        self.rect.topleft = (self.x,self.y)

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
    def update(self):
        self.rect.topleft = (self.x,self.y)

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
    
    def update(self):
        self.rect.topleft = (self.x,self.y)

class GameObjective(pygame.sprite.Sprite):
    def __init__(self,x,y,image):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.topleft = (self.x,self.y)

class Level1UFO(AbstractUFO):
    def __init__(self,x,y,img,world):
        super().__init__(img,world)
        self.x = x
        self.y = y

class Background(pygame.sprite.Sprite):
    def __init__(self,x,y,image):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self):
        self.rect.topleft = (self.x,self.y)



# load layers 
tiles = TileSetContainer()
for tileset in data['tilesets']:
    print('loading ',tileset['image'])
    tmp = TileSet(tileset['name'], pygame.image.load(tileset['image']).convert_alpha(), tileset['firstgid'], tiles, tileset['tilewidth'], tileset['tileheight'], tileset['imagewidth'], tileset['imageheight'])
    del(tmp)
    
# print(allTiles)
layerData = {}

bullet_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
fuel_can_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
gameObjective_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()


world = World()

mapProp = data['layers'][0]['properties']
for prop in mapProp:
    if prop['name'] == 'gravity':
        world.gravity = prop['value']
    elif prop['name'] == 'airFriction':
        world.airFriction = prop['value']
    elif prop['name'] == 'xMultiplier':
        world.xMultiplier = prop['value']
    elif prop['name'] == 'yMultiplier':
        world.yMultiplier = prop['value']
    elif prop['name'] == 'offset_min':
        MIN_OFFSET = prop['value']
    elif prop['name'] == 'offset_max':
        MAX_OFFSET = prop['value']

for layer in data['layers']:
    if layer['name'] == 'BaseLayer' or layer['name'] == 'Non_Interactive_obstacles':
        print('loading background...')
        l = pygame.Surface((data['width'] * TILES_RES, data['height'] * TILES_RES))
        l.set_colorkey((0,0,0))
        for x in range(data['width']):
            for y in range(data['height']):
                print('loading...',layer['data'][x + y * data['width']])
                tile = tiles.getTile(layer['data'][x + y * data['width']])
                l.blit(tile, (x * TILES_RES, y * TILES_RES))
        layerData[layer['name']]={ 'data': l, 'x': layer['x'], 'y': layer['y']}
    elif layer['name'] == 'Interactive_obstacles':
        print('loading obstacles...')
        eVal = 0.8
        for prop in layer['properties']:
            if prop['name'] == 'e':
                eVal = float(prop['value'])
        for x in range(data['width']):
            for y in range(data['height']):
                if layer['data'][x + y * data['width']] != 0:
                    obs = obstacle(x*TILES_RES,y*TILES_RES,tiles.getTile(layer['data'][x + y * data['width']]),eVal)
                    obstacle_group.add(obs)
    elif layer['name'] == 'Fuel':
            print('loading fuel...')
            fuelLevels = 0.5
            for prop in layer['properties']:
                if prop['name'] == 'fuelLevel':
                    fuelLevels = float(prop['value'])
            for x in range(data['width']):
                for y in range(data['height']):
                    if layer['data'][x + y * data['width']] != 0:
                        fuel = FuelCan(x*TILES_RES,y*TILES_RES,tiles.getTile(layer['data'][x + y * data['width']]),fuelLevels)
                        fuel_can_group.add(fuel)
    elif layer['name'] == 'Coin':
            print('loading coins...')
            cVal = 1
            for prop in layer['properties']:
                if prop['name'] == 'value':
                    cVal = int(prop['value'])
            for x in range(data['width']):
                for y in range(data['height']):
                    if layer['data'][x + y * data['width']] != 0:
                        coin = Coins(x*TILES_RES,y*TILES_RES,tiles.getTile(layer['data'][x + y * data['width']]),cVal)
                        coins_group.add(coin)
    elif layer['name'] == 'Game_Objective':
            print('loading game objective...')
            for x in range(data['width']):
                for y in range(data['height']):
                    if layer['data'][x + y * data['width']] != 0:
                        gobj = GameObjective(x*TILES_RES,y*TILES_RES,tiles.getTile(layer['data'][x + y * data['width']]))
                        gameObjective_group.add(gobj)
    elif layer['name'] == 'UFO':
            print('loading UFO...')
            for x in range(data['width']):
                for y in range(data['height']):
                    if layer['data'][x + y * data['width']] != 0:
                        ufo = Level1UFO(x*TILES_RES,y*TILES_RES,tiles.getTile(layer['data'][x + y * data['width']]),world)
                        ufo_group.add(ufo)
            for props in layer['properties']:
                if props['name'] == 'fuelCap':
                    ufo.fuelCap = float(props['value'])
                elif props['name'] == 'fuelLevel':
                    ufo.fuelLevel = float(props['value'])
                elif props['name'] == 'fuelEfficency':
                    ufo.fuelEfficency = float(props['value'])
                elif props['name'] == 'enginForce':
                    ufo.enginForce = float(props['value'])
                elif props['name'] == 'mass':
                    ufo.mass = float(props['value'])
                elif props['name'] == 'liftingEnginCount':
                    ufo.liftingEnginCount = int(props['value'])
                elif props['name'] == 'HorizontalAirFrictionMultiplier':
                    ufo.HorizontalAirFrictionMultiplier = float(props['value'])
                elif props['name'] == 'VerticalAirFrictionMultiplier':
                    ufo.VerticalAirFrictionMultiplier = float(props['value'])
                elif props['name'] == 'e':
                    ufo.e = float(props['value'])


background = Background(layerData['BaseLayer']['x'],layerData['BaseLayer']['y'],layerData['BaseLayer']['data'])
safeobs = Background(layerData['Non_Interactive_obstacles']['x'],layerData['Non_Interactive_obstacles']['y'],layerData['Non_Interactive_obstacles']['data'])

background_group.add(background)
background_group.add(safeobs)
print('background loaded')

        
del(tiles)






scoreLabmda = lambda: 'Chips: {}'.format(coinsValue)
fuelLambda = lambda: 'Fuel: {:.7}/{:.5}'.format(ufo.fuelLevel,ufo.fuelCap)
score = TextMsg(5,0,scoreLabmda,WHITE)
fuel = TextMsg(5,28,fuelLambda,WHITE)
bullet = Bullet(0,0)



bullet_group.add(bullet)
text_group.add(score)
text_group.add(fuel)

color = RED

def keepInCamBounds(allObjects):
    global current_offset
    if ufo.x <= CAM_BOX.left and  current_offset <= MAX_OFFSET:
        print('ufo going left',current_offset)
        current_offset += CAM_BOX.left - ufo.x
        for obj_grp in allObjects:
            for obj in obj_grp:
                obj.x += CAM_BOX.left - ufo.x
                obj.update()
    elif ufo.x >= CAM_BOX.right and current_offset >= MIN_OFFSET:
        print('ufo going right',current_offset)
        current_offset -= ufo.x - CAM_BOX.right
        for obj_grp in allObjects:
            for obj in obj_grp:
                obj.x -= ufo.x - CAM_BOX.right
                obj.update()

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

    gameObjectiveColisions = pygame.sprite.spritecollide(ufo,gameObjective_group,True)
    if gameObjectiveColisions:
        print('You Win')
        global run
        run = False
        
    
    
    keepInCamBounds([obstacle_group,fuel_can_group,coins_group,gameObjective_group,background_group,ufo_group])
    
    bullet_group.update(color)
    ufo_group.update()
    text_group.update()

    background_group.draw(WIN)
    ufo_group.draw(WIN)
    obstacle_group.draw(WIN)
    fuel_can_group.draw(WIN)
    coins_group.draw(WIN)
    gameObjective_group.draw(WIN)
    text_group.draw(WIN)
    bullet_group.draw(WIN)

    pygame.draw.rect(WIN,PURPLE,CAM_BOX,2)

    pygame.display.update()

run = True
while run:
    clock.tick(FPS)
    pygame.mouse.set_visible(False)
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