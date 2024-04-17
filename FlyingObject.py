import pygame
from utils import *
from colors import *
from loadLevels import *
import json
import os

########################################
####        Global Consts           ####
########################################
WIDTH,HEIGHT = 1200,800
FPS = 32
TILES_RES = 64
MIN_SPEED = 3.5

pygame.init()

WIN = pygame.display.set_mode((WIDTH,HEIGHT))
GAME_FONT = pygame.font.SysFont("Cambria", 25)
GAME_FONT_LARGE = pygame.font.SysFont("Cambria", 55)
PADDING = 600
CAM_BOX = pygame.Rect(100,0,WIDTH - PADDING,HEIGHT)
MAX_OFFSET = 0
MIN_OFFSET = -232
menuOBJ = {
    0: {
        'text': 'Start Game',
        'isDisable':False,
        'subMenu': None,
        'cmd':None
    },
    1: {
        'text': 'Levels',
        'isDisable':False,
        'subMenu': {
            0: {
                'text': 'Level 1',
                'isDisable':False,
                'subMenu': None,
                'cmd':'level3'
            },
            1: {
                'text': 'Level 2',
                'isDisable':True,
                'subMenu': None,
                'cmd':None
            },
            2: {
                'text': 'Level 3',
                'isDisable':True,
                'subMenu': None,
                'cmd':None

            },
            3: {
                'text': 'Level 4',
                'isDisable':True,
                'subMenu': None,
                'cmd':None

            },
            4: {
                'text': 'Level 5',
                'isDisable':True,
                'subMenu': None,
                'cmd':None

            },
            5: {
                'text': 'Level 6',
                'isDisable':True,
                'subMenu': None,
                'cmd':None

            },
            6: {
                'text': 'Level 7',
                'isDisable':True,
                'subMenu': None,
                'cmd':None

            },
        }
    },
    2: {
        'text': 'Exit',
        'isDisable':False,
        'subMenu': None,
        'cmd':'quit'
    }
}

level = 0

# load level data 
def loadLevelData(levelFile):
    json_data = open('levels/'+levelFile).read()
    data = json.loads(json_data)
    del(json_data)
    return data

def loadUserData():
    global menuOBJ
    print('befor',menuOBJ)
    if not os.path.exists('userData.dat'):
        with open('userData.dat','w') as f:
            f.write(json.dumps({'coins':0,'currentLevel':0,'levels':menuOBJ[1]['subMenu']}))
    json_data = open('userData.dat').read()
    data = json.loads(json_data)
    for l in data['levels'].keys():
        menuOBJ[1]['subMenu'][int(l)]['isDisable'] = data['levels'][l]['isDisable']
    del(json_data)
    global level
    global coinsValue
    coinsValue = data['coins']
    for l in data['levels']:
        if data['levels'][l]['isDisable']:
            level = int(l)
            break
    print('after',menuOBJ)

def unlockNextLevel():
    global menuOBJ
    global level
    for l in menuOBJ[1]['subMenu']:
        if menuOBJ[1]['subMenu'][l]['isDisable']:
            level = int(l)
            menuOBJ[1]['subMenu'][l]['isDisable'] = False
            break
    saveUserData()



def saveUserData():
    global menuOBJ
    global coinsValue
    global level
    with open('userData.dat','w') as f:
        f.write(json.dumps({'coins':coinsValue,'currentLevel':str(level),'levels':menuOBJ[1]['subMenu']}))

loadUserData()

########################################
####        Global Variables        ####
########################################

pygame.display.set_caption("UFO game")
clock = pygame.time.Clock()
coinsValue = 0
current_offset = 0
sounds = {
    "grab":'grab.wav',
    "conflict":'conflict.wav',
    "conflict2":'conflict2.wav',
    "failing":'failing.wav',
    "menuSelect":'menuSelect.wav',
    "splash":'splash.wav',
    "win":'win.wav',
    "refill":'refill.wav',
    "engineStop":'engineStop.wav',
    "engineWorking":'engineWorking.wav'
}

loadedSounds=dict()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)
for key in sounds:
    print('loading',key)
    loadedSounds[key] = pygame.mixer.Sound('sounds/'+sounds[key])

def playSound(sound_key,volume,loops=0,reserved=False):
    if reserved:
        pygame.mixer.set_reserved(1)
        channel = pygame.mixer.Channel(0)
        channel.play(loadedSounds[sound_key],loops=loops)
        channel.set_volume(volume)
        return channel
    else:
        channel = pygame.mixer.find_channel(True)
        channel.set_volume(volume)
        channel.play(loadedSounds[sound_key],loops=loops)
        return channel



playSound('splash',1)

class TextMsg(pygame.sprite.Sprite):
    def __init__(self,x,y,getText,color,text=None):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.color = color
        self.getText = getText
        self.text = text
        if self.text:
            self.image = GAME_FONT.render(self.text,1,color)
        else:
            self.image = GAME_FONT.render(self.getText(), 1, color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
        # objects.append(self)
    
    def update(self):
        if self.text:
            self.image = GAME_FONT.render(self.text,1,self.color)
        else:
            self.image = GAME_FONT.render(self.getText(),1,self.color)

    def setColor(self,color):
        self.color = color
        self.update()

class Banner(pygame.sprite.Sprite):
    def __init__(self,text,color):
        pygame.sprite.Sprite.__init__(self)
        self.x = WIDTH//2 - 100
        self.y = HEIGHT//2 - 50
        self.color = color
        self.text = text
        self.image = GAME_FONT_LARGE.render(self.text,1,color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x,self.y)
    
    def update(self):
        self.image = GAME_FONT_LARGE.render(self.text,1,self.color)
        self.rect.topleft = (self.x,self.y)


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
    maxhealth = 1000.0
    health = maxhealth
    strength = 10.0
    acceleration = enginForce/mass
    liftingEnginCount = 1
    HorizontalAirFrictionMultiplier = 0.3
    VerticalAirFrictionMultiplier = 0.5
    speedX = 0.0
    speedY = 0.0
    prevPos = (x,y)
    e = 0.5
    noFuel = False
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
        self.engineSound = playSound('engineWorking',0.2,-1,True)


    def update(self):
        self.rect.topleft = (self.x,self.y)

    def destroyObj(self):
        self.engineSound.stop()
        pygame.mixer.set_reserved(0)

    def fuelRefill(self,fuelCan):
        newFuelLevel = 0.0
        for can in fuelCan:
            newFuelLevel += can.fuelLevel
        if self.fuelLevel + newFuelLevel >= self.fuelCap:
            self.fuelLevel = self.fuelCap
        else:
            self.fuelLevel += newFuelLevel
        self.noFuel = False
        playSound('refill',1)
        
    def collide(self,colisions):
        if not (self.isColidedTop or self.isColidedBottom or self.isColidedLeft or self.isColidedRight):
            for obs in colisions:
                # print(obs.rect.left,obs.rect.right,obs.rect.top,obs.rect.bottom,self.rect.left,self.rect.right,self.rect.top,self.rect.bottom)
                # offset = max(self.rect.right - obs.rect.left,self.rect.bottom - obs.rect.top)/5
                offset = max([self.speedX*5,self.speedY*5,10])
                damage = 0
                if self.speedX !=0 and self.speedY!=0:
                    damage = abs(self.speedX * self.speedY)
                elif self.speedX !=0:
                    damage = abs(self.speedX)
                elif self.speedY !=0:
                    damage = abs(self.speedY)

                if damage > self.strength:
                    h = self.health - damage
                    if h<0:
                        self.destroyObj()
                        self.health = 0.0
                        bullet_group.empty()
                        ufo_group.empty()
                        text_group.empty()
                        obstacle_group.empty()
                        fuel_can_group.empty()
                        coins_group.empty()
                        gameObjective_group.empty()
                        background_group.empty()
                        banner_msg_group.empty()
                        global inBanner
                        global inGame
                        print('You loss')
                        playSound('failing',1)
                        banner = Banner('DAMAGED SERIOUSLY',ORANGE)
                        banner.x = WIDTH//2-200
                        banner.update()
                        banner_msg_group.add(banner)
                        text_group.add(TextMsg(WIDTH//2-150,HEIGHT//2+50,None,GRAY,'(press enter key to continue.)'))
                        loadUserData()
                        inBanner = True
                        inGame = False
                    else:
                        self.health = float(h)

                # print('offset',offset)
                self.prevPos = (self.x,self.y)
                if obs.rect.bottom > self.rect.top and obs.rect.bottom < self.rect.top+offset:
                    # print('collision at bottom')
                    self.speedY = (self.speedY)*-1*((obs.e+self.e)/2)
                    self.y = self.prevPos[1]+1
                    self.isColidedTop = True
                    playSound('conflict',offset/100.0)
                elif obs.rect.top < self.rect.bottom and obs.rect.top > self.rect.bottom-offset:
                    # print('collision at top')
                    self.speedY = (self.speedY)*-1*((obs.e+self.e)/2)
                    # print('speedY',self.speedY)
                    if self.speedY < 1.5:
                        # print('speedY set to 0')
                        self.speedY = 0.0
                    # self.y = obs.rect.top - self.img.get_height()
                    self.y = self.prevPos[1]
                    self.isColidedBottom = True
                    playSound('conflict',offset/100.0)
                if obs.rect.left < self.rect.right and obs.rect.left > self.rect.right-offset:
                    # print('collision at left')
                    self.speedX = (self.speedX)*-1*((obs.e+self.e)/2)
                    # self.x = obs.rect.left - self.img.get_width()
                    self.x = self.prevPos[0]-1
                    self.isColidedRight = True
                    playSound('conflict2',offset/100.0)
                elif obs.rect.right > self.rect.left and obs.rect.right < self.rect.left+offset:
                    # print('collision at right')
                    self.speedX = (self.speedX)*-1*((obs.e+self.e)/2)
                    # self.x = obs.rect.right
                    self.x = self.prevPos[0]+1
                    self.isColidedLeft = True
                    playSound('conflict2',offset/100.0)

                
        
    
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
            if not self.noFuel:
                self.noFuel = True
                self.engineSound.set_volume(0.0)
                playSound('engineStop',1)
    
    def moveLeft(self):
        if self.fuelLevel>0 and not self.isColidedLeft:
            dt = clock.get_time()/1000.0
            dx = self.speedX * dt + (abs(self.world.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX)+(-1*self.acceleration))*(dt**2)
            # print('dx',dx)
            self.shiftXPosition(dx,dt)
            self.burnFuel()
            self.engineSound.set_volume(0.6)
        else:
            self.burnLinearInertiaX()

    def moveRight(self):
        if self.fuelLevel>0 and not self.isColidedRight:
            dt = clock.get_time()/1000.0
            dx = self.speedX * dt + (-1*abs(self.world.airFriction * self.HorizontalAirFrictionMultiplier * self.speedX)+(self.acceleration))*(dt**2)
            # print('dx',dx)
            self.shiftXPosition(dx,dt)
            self.burnFuel()
            self.engineSound.set_volume(0.6)
        else:
            self.burnLinearInertiaX()


    def moveUp(self):
        if self.fuelLevel>0 and not self.isColidedTop:
            dt = clock.get_time()/1000.0
            dy = self.speedY * dt + (-1*abs(self.world.airFriction * self.VerticalAirFrictionMultiplier * self.speedY)+(self.liftingEnginCount*self.acceleration - self.world.gravity))*(dt**2)
            # print('dy',dy)
            self.shiftYPosition(dy,dt)
            self.burnFuel(self.liftingEnginCount)
            self.engineSound.set_volume(0.8)
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

        if self.speedY == 0.0 and self.noFuel:
            self.destroyObj()
            bullet_group.empty()
            ufo_group.empty()
            text_group.empty()
            obstacle_group.empty()
            fuel_can_group.empty()
            coins_group.empty()
            gameObjective_group.empty()
            background_group.empty()
            banner_msg_group.empty()
            global inBanner
            global inGame
            print('You loss')
            playSound('failing',1)
            banner = Banner('OUT OF FUEL',ORANGE)
            banner.x = WIDTH//2 - 150
            banner.update()
            banner_msg_group.add(banner)
            text_group.add(TextMsg(WIDTH//2-150,HEIGHT//2+50,None,GRAY,'(press enter key to continue.)'))
            loadUserData()
            inBanner = True
            inGame = False
            
            # print('burnY',self.speedY)

    def engineStandby(self):
        self.engineSound.set_volume(0.2)

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


bullet_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
text_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
fuel_can_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
gameObjective_group = pygame.sprite.Group()
background_group = pygame.sprite.Group()
banner_msg_group = pygame.sprite.Group()

ufo = None
inGame = False
inBanner = False
def startLevel(currentLevel):
    # load layers 
    global coinsValue
    global MIN_OFFSET
    global MAX_OFFSET
    global current_offset
    current_offset = 0
    data = loadLevelData('level{}.tmj'.format(currentLevel))
    tiles = TileSetContainer()
    for tileset in data['tilesets']:
        # print('loading ',tileset['image'])
        tmp = TileSet(tileset['name'], pygame.image.load(tileset['image']).convert_alpha(), tileset['firstgid'], tiles, tileset['tilewidth'], tileset['tileheight'], tileset['imagewidth'], tileset['imageheight'])
        del(tmp)
        
    # print(allTiles)
    layerData = {}

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
            print('min offset set to ',MIN_OFFSET)
        elif prop['name'] == 'offset_max':
            MAX_OFFSET = prop['value']
            print('max offset set to ',MAX_OFFSET)

    for layer in data['layers']:
        if layer['name'] == 'BaseLayer' or layer['name'] == 'Non_Interactive_obstacles':
            # print('loading background...')
            l = pygame.Surface((data['width'] * TILES_RES, data['height'] * TILES_RES))
            l.set_colorkey((0,0,0))
            for x in range(data['width']):
                for y in range(data['height']):
                    # print('loading...',layer['data'][x + y * data['width']])
                    tile = tiles.getTile(layer['data'][x + y * data['width']])
                    l.blit(tile, (x * TILES_RES, y * TILES_RES))
            layerData[layer['name']]={ 'data': l, 'x': layer['x'], 'y': layer['y']}
        elif layer['name'] == 'Interactive_obstacles':
            # print('loading obstacles...')
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
                # print('loading fuel...')
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
                # print('loading coins...')
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
                # print('loading game objective...')
                for x in range(data['width']):
                    for y in range(data['height']):
                        if layer['data'][x + y * data['width']] != 0:
                            gobj = GameObjective(x*TILES_RES,y*TILES_RES,tiles.getTile(layer['data'][x + y * data['width']]))
                            gameObjective_group.add(gobj)
        elif layer['name'] == 'UFO':
                # print('loading UFO...')
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
    del(tiles)


    scoreLabmda = lambda: 'Chips: {}'.format(coinsValue)
    fuelLambda = lambda: 'Fuel: {:.7}/{:.5}'.format(ufo.fuelLevel,ufo.fuelCap)
    healthLambda = lambda: 'health: {:.7}/{:.5}'.format(ufo.health,ufo.maxhealth)
    score = TextMsg(5,0,scoreLabmda,WHITE)
    fuel = TextMsg(5,28,fuelLambda,WHITE)
    health = TextMsg(5,56,healthLambda,WHITE)
    bullet = Bullet(0,0)



    bullet_group.add(bullet)
    text_group.add(score)
    text_group.add(fuel)
    text_group.add(health)
    return ufo

def keepInCamBounds(allObjects):
    global current_offset
    global MAX_OFFSET
    global MIN_OFFSET
    if ufo.x <= CAM_BOX.left and  current_offset <= MAX_OFFSET:
        print('ufo going left',current_offset ,'<=',MAX_OFFSET , ufo.x ,'<=', CAM_BOX.left)
        current_offset += CAM_BOX.left - ufo.x
        for obj_grp in allObjects:
            for obj in obj_grp:
                obj.x += CAM_BOX.left - ufo.x
                obj.update()
    elif ufo.x >= CAM_BOX.right and current_offset >= MIN_OFFSET:
        print('ufo going right',current_offset , '',MIN_OFFSET , ufo.x,'>=',CAM_BOX.right)
        current_offset -= ufo.x - CAM_BOX.right
        for obj_grp in allObjects:
            for obj in obj_grp:
                obj.x -= ufo.x - CAM_BOX.right
                obj.update()

def drawBanner():
    WIN.fill(DARK_TEAL)
    banner_msg_group.draw(WIN)
    text_group.draw(WIN)
    bullet_group.draw(WIN)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
        text_group.empty()
        global inGame
        global inBanner
        inGame = False
        inBanner = False

def drawGame():
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
        playSound('grab',1)

    gameObjectiveColisions = pygame.sprite.spritecollide(ufo,gameObjective_group,True)
    if gameObjectiveColisions:
        ufo.destroyObj()
        bullet_group.empty()
        ufo_group.empty()
        text_group.empty()
        obstacle_group.empty()
        fuel_can_group.empty()
        coins_group.empty()
        gameObjective_group.empty()
        background_group.empty()
        banner_msg_group.empty()
        global inBanner
        global inGame
        global menu
        menu.reset()
        print('You Win')
        playSound('win',1)
        banner_msg_group.add(Banner('YOU WIN',GOLD))
        text_group.add(TextMsg(WIDTH//2-150,HEIGHT//2+50,None,GRAY,'(press enter key to continue.)'))
        unlockNextLevel()
        inGame = False
        inBanner = True

        
    keepInCamBounds([obstacle_group,fuel_can_group,coins_group,gameObjective_group,background_group,ufo_group])
    
    bullet_group.update(RED)
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

    # pygame.draw.rect(WIN,PURPLE,CAM_BOX,2)
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
    if not (linearMovementX or linearMovementY):
        ufo.engineStandby()


class Menu:
    def __init__(self,menuObj):
        self.menuObj = menuObj
        self.selectedIndex = 0
        self.menuItems_group = pygame.sprite.Group()
        self.hasMore = False
        self.currentObj = self.menuObj
        self.previousObj = []
        self.prepareMenuItems()
        self.hilightSelected()
        self.offset = 0
        self.isDisable = False

    def getMenuItemGroup(self):
        tmp = pygame.sprite.Group(self.menuItems_group)
        backCol = GREEN
        selectCol = GREEN
        if len(self.previousObj)==0:
            backCol = GRAY
        if self.isDisable:
            selectCol = GRAY
        tmp.add(TextMsg(WIDTH//2 - 250,HEIGHT//2 + 150,None,backCol,'Back (BackSpace)'))
        tmp.add(TextMsg(WIDTH//2 + 50 ,HEIGHT//2 + 150,None,selectCol,'Select (Enter)'))
        return tmp


    def prepareMenuItems(self):
        self.menuItems_group.empty()
        if self.selectedIndex>4:
            self.offset = self.selectedIndex - 4
        else:
            self.offset = 0
        for i in range(min(5,len(self.currentObj))):
            self.menuItems_group.add(TextMsg(WIDTH//2 - 100,HEIGHT//2 -100 +i*50,None,WHITE,self.currentObj[i+self.offset]['text']))
        if len(self.currentObj) > 5:
            self.hasMore = True
        else:
            self.hasMore = False  

    def up(self):
        if self.selectedIndex > 0:
            self.selectedIndex -= 1
        else:
            self.selectedIndex = len(self.currentObj)-1
        self.prepareMenuItems()
        self.hilightSelected()
        playSound('menuSelect',0.8)
        
    
    def down(self):
        if self.selectedIndex < len(self.currentObj)-1:
            self.selectedIndex += 1
        else:
            self.selectedIndex = 0
        self.prepareMenuItems()
        self.hilightSelected()
        playSound('menuSelect',0.8)


    def select(self):
        sm =  self.currentObj[self.selectedIndex]
        if sm['subMenu']:
            self.previousObj.append(self.currentObj)
            self.currentObj = sm['subMenu']
            self.selectedIndex = 0
            self.prepareMenuItems()
            self.hilightSelected()
            playSound('grab',1)
        elif sm['cmd']:
            if sm['cmd'] == 'quit':
                quit()
            elif sm['cmd'][:5]=='level':
                global ufo
                global inGame
                ufo = startLevel(int(sm['cmd'][5:]))
                print(MAX_OFFSET,MIN_OFFSET)
                inGame = True
                playSound('splash',1) 
        else:
            print('nothing to execute')
    
    def back(self):
        if len(self.previousObj)>0:
            self.currentObj =self.previousObj.pop()
            self.selectedIndex = 0
            self.offset = 0
            self.prepareMenuItems()
            self.hilightSelected()
            playSound('grab',1)



    def hilightSelected(self):
        for i in range(len(self.menuItems_group)):
            if i+self.offset == self.selectedIndex:
                self.menuItems_group.sprites()[i].setColor(RED)
                if self.currentObj[self.offset+i]['isDisable']:
                    self.isDisable = True
                else:
                    self.isDisable = False
            else:
                self.menuItems_group.sprites()[i].setColor(WHITE)

    def reset(self):
        self.currentObj = self.menuObj
        self.selectedIndex = 0
        self.previousObj = []
        self.prepareMenuItems()
        self.hilightSelected()

menu = Menu(menuOBJ)

pressedAndReleased = True
def drawMenu():
    global pressedAndReleased
    WIN.fill(DARK_TEAL)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:
        if pressedAndReleased:
            # code to move down
            menu.down()
            #
            pressedAndReleased = False
    elif keys[pygame.K_UP]:
        if pressedAndReleased:
            # code to move up
            menu.up()
            #
            pressedAndReleased = False
    elif keys[pygame.K_RETURN]:
        if pressedAndReleased:
            # code to select
            menu.select()
            #
            pressedAndReleased = False
    elif keys[pygame.K_BACKSPACE]:
        if pressedAndReleased:
            # code to select
            menu.back()
            #
            pressedAndReleased = False
    else:
        pressedAndReleased = True

    menu.getMenuItemGroup().draw(WIN)

run = True
pygame.mouse.set_visible(False)

while run:
    clock.tick(FPS)
    if inGame:
        drawGame()
    elif inBanner:
        drawBanner()
    else:
        drawMenu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
            break

    pygame.display.update()

pygame.quit()


