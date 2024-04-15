import pygame

# pygame.init()
# win = pygame.display.set_mode((1200,800))



class TileSetContainer:
    def __init__(self):
        self.tilesets = { 0: pygame.Surface((32,32)) }
    def addTile(self, gid ,tileset):
        self.tilesets[gid] = tileset
    def getTile(self, gid):
        return self.tilesets[gid]

class TileSet:
    def __init__(self, name, image, firstgid, tilesetContainer, tileWidth, tileHeight ,TilesetWidth ,TilesetHeight):
        self.name = name
        self.image = image
        self.tileWidth = tileWidth
        self.tileHeight = tileHeight
        self.TilesetWidth = TilesetWidth
        self.TilesetHeight = TilesetHeight
        self.firstgid = firstgid
        self.tilesetContainer = tilesetContainer
        self.getAllTiles()

    def getAllTiles(self):
        tileCount = (self.TilesetWidth // self.tileWidth) * (self.TilesetHeight // self.tileHeight)
        for i in range(tileCount):
            tmp = self.getTile(i)
            self.tilesetContainer.addTile(self.firstgid + i, tmp)

    def getTile(self, tileNumber):
        return self.image.subsurface((tileNumber % (self.TilesetWidth//self.tileWidth)) * self.tileWidth, (tileNumber // (self.TilesetWidth//self.tileWidth)) * self.tileHeight, self.tileWidth, self.tileHeight)



