import pygame
from pygame.locals import *
import config
import os, sys
import pytmx
from pytmx.util_pygame import load_pygame
import math

#Funciones helper para tratar con sprites
class SpriteUtils:
    #Helper function de carga
    @staticmethod
    def loadImage(name, colorkey=None):
            fullname = os.path.join('images', name)
            try:
                image = pygame.image.load(fullname).convert()
            except pygame.error:
                print ('Cannot load image:', name)
                raise SystemExit
            image = image.convert()
            if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey, RLEACCEL)
            return image

    @staticmethod
    def loadSpriteSheet(name, width, height, colorkey=-1):
        fullname = os.path.join('images', name)
        image = pygame.image.load(fullname).convert()
        if colorkey is not None:
                if colorkey is -1:
                    colorkey = image.get_at((0,0))
                image.set_colorkey(colorkey, RLEACCEL)
        image_width, image_height = image.get_size()
        tile_table = []
        
        for tile_y in range(0, image_height//height):
            line = []
            tile_table.append(line)
            for tile_x in range(0, image_width//width):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table

#Basic GameObject structure.
class GameObject(pygame.sprite.DirtySprite):
    
    def __init__(self,x=0,y=0):
        pygame.sprite.Sprite.__init__(self)
        self.spriteGroup = None 
        self.children = {}
        self.parent = None
        self.process_input=False
        self.process_update=False
        self.offset_x=0
        self.offset_y=0
        self.x=x
        self.y=y
    
    def add(self, name, child, offset_x=0, offset_y=0):
        child.offset_x=offset_x
        child.offset_y=offset_y
        self.children[name]=child;
        self.children[name].parent=self

    def getChild(self,name):
        return self.children[name]

    def getParent(self):
        return self.parent

    def getScene(self):
        if self.parent is None:
            return self
        else:
            return self.parent.getScene()
        
    def loadImage(self,path):
        self.image = SpriteUtils.loadImage(path)
        self.rect=self.image.get_rect()
        self.rect.x=self.x
        self.rect.y=self.y
        self.spriteGroup=pygame.sprite.RenderUpdates(self)

    def changeImage(self,image):
        self.image = image
        self.rect=self.image.get_rect()
        self.rect.x=self.x
        self.rect.y=self.y
        self.spriteGroup=pygame.sprite.RenderUpdates(self)

    def loadImageFromSheet(self,path,sheet_x,sheet_y,width,height):
        tiles=SpriteUtils.loadSpriteSheet(path,width, height)
        self.image=(tiles[sheet_x][sheet_y])
        self.rect=pygame.Rect(self.x*width,self.y*height,width,height)
        self.spriteGroup=pygame.sprite.RenderUpdates(self)

    def moveSprite(self,x,y):
        self.x=x
        self.y=y
        self.rect.x=x
        self.rect.y=y
        self.dirty=1
        for name, child in self.children.iteritems():
            child.moveSprite(child.offset_x+x,child.offset_y+y)

    def moveSpriteRelative(self,x,y):
        self.x+=int(x)
        self.y+=int(y)
        self.rect.x+=int(x)
        self.rect.y+=int(y)     
        self.dirty=1
        for name, child in self.children.iteritems():
            child.moveSpriteRelative(x,y)

    def draw(self, screen):
    	if (self.spriteGroup is not None):
    		changed=self.spriteGroup.draw(screen)
        for name, child in self.children.iteritems():
            child.draw(screen)

    def processInput(self, event):
        pass

    def update(self,delta):
        pass



"""Basic Scene structure; contains methods for drawing, updating and input handling."""
class Scene(GameObject):
    def __init__(self,screen):
        GameObject.__init__(self)
        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0,0,0))
        self.dirties=[]
    
    def processInput(self, event):
        for name, child in self.children.iteritems():
            if child.process_input:
                child.processInput(event)

    def update(self,delta):
        for name, child in self.children.iteritems():
            if child.process_update:
                child.update(delta)

    def draw(self, screen):
        #Default: children render
        screen.blit(self.background, (0,0))
        for name, child in self.children.iteritems():
            child.draw(screen) 
        pygame.display.flip()
               
        

    def switchToScene(self, next_scene):
        self.next = next_scene

"""Basic tilemap, TMX loaded, pytmx powered"""
class Tilemap(GameObject):

    def __init__(self):
        GameObject.__init__(self)
        self.spriteGroup = pygame.sprite.Group()
        self.data = None
        self.width=0
        self.height=0

    #Full TMX map loading (includes tile properties)
    def loadTMXMap(self,path):
        self.data = load_pygame(path)
        #definir mapita
        self.width=self.data.width
        self.height=self.data.height
        for idx, idy, image in self.data.layers[0].tiles():
                tile = pygame.sprite.Sprite()
                tile.image=image.convert()
                tile.rect=pygame.Rect(idx*self.data.tilewidth,idy*self.data.tileheight,self.data.tilewidth,self.data.tileheight)
                self.spriteGroup.add(tile) #Agregar al grupo

    #Returns property/value dict of specified tile
    def getTileProperties(self,x,y,z=0):
        if (x>=0 and x<self.width and y>=0 and y<self.height):
            return self.data.get_tile_properties(x, y, layer)
        else:
            return None

    #Return the value of a specified tile property; None if there is no such property
    def getTileProperty(self,x,y,prop,z=0):
        if (x>=0 and x<self.width and y>=0 and y<self.height):
            tileData=self.data.get_tile_properties(x, y, z)
            if tileData is None or not prop in tileData:
                return None
            else:
                return tileData[prop]

    #True if x,y pair is a valid map position
    def isValidTile(self,x,y):
        if (x>=0 and x<self.width and y>=0 and y<self.height):
            return True
        else:
            return False

    #Gets valid neighbor position for a certain tile
    def getNeighbors(self,map_x,map_y,movement_check=False):
        neighbors=[]
        if self.isValidTile(map_x-1,map_y) and (not movement_check or self.getTileProperty(map_x-1,map_y,'solid')!='true'):
            neighbors.append({'x':map_x-1,'y':map_y})
        if self.isValidTile(map_x-1,map_y-1) and (not movement_check or self.getTileProperty(map_x-1,map_y-1,'solid')!='true'):
            neighbors.append({'x':map_x-1,'y':map_y-1})
        if self.isValidTile(map_x,map_y-1) and (not movement_check or self.getTileProperty(map_x,map_y-1,'solid')!='true'):
            neighbors.append({'x':map_x,'y':map_y-1})
        if self.isValidTile(map_x+1,map_y-1) and (not movement_check or self.getTileProperty(map_x+1,map_y-1,'solid')!='true'):
            neighbors.append({'x':map_x+1,'y':map_y-1})
        if self.isValidTile(map_x+1,map_y) and (not movement_check or self.getTileProperty(map_x+1,map_y,'solid')!='true'):
            neighbors.append({'x':map_x+1,'y':map_y})
        if self.isValidTile(map_x+1,map_y+1) and (not movement_check or self.getTileProperty(map_x+1,map_y+1,'solid')!='true'):
            neighbors.append({'x':map_x+1,'y':map_y+1})
        if self.isValidTile(map_x,map_y+1) and (not movement_check or self.getTileProperty(map_x,map_y+1,'solid')!='true'):
            neighbors.append({'x':map_x,'y':map_y+1})
        if self.isValidTile(map_x-1,map_y+1) and (not movement_check or self.getTileProperty(map_x-1,map_y+1,'solid')!='true'):
            neighbors.append({'x':map_x-1,'y':map_y+1})
        return neighbors

    #Mahattan distance between two points, used as heuristic in A* pathfinding
    def getManhattanDistance(self,current,goal):
        return abs(goal['x'] - current['x']) + abs(goal['y'] - current['y'])

    #A* pathfinding. Returns list of {x,y} pairs specifying best path
    #Actors can move using such lists with the MoveTo function.
    def AStarPathfinding(self,start_x,start_y,map_x,map_y):
        start={'x':start_x,'y':start_y}
        startCode="x"+str(start['x'])+"y"+str(start['y'])
        goal={'x':map_x,'y':map_y}
        frontier = []
        frontier.append({'element':start,'priority':0})
        came_from={}
        cost_so_far={}
        came_from[startCode]=start
        cost_so_far[startCode]=0
        while frontier:
            frontier.sort(key=lambda k: k['priority'])
            current = frontier.pop(0)['element']
            currentCode="x"+str(current['x'])+"y"+str(current['y'])
            
            if (current['x']==goal['x'] and current['y']==goal['y']):
                break

            for next in self.getNeighbors(current['x'],current['y'],True):
                nextCode="x"+str(next['x'])+"y"+str(next['y'])
                new_cost=cost_so_far[currentCode]+1
                if not nextCode in cost_so_far or (new_cost < cost_so_far[nextCode]):
                    cost_so_far[nextCode]=new_cost
                    priority = new_cost + self.getManhattanDistance(next,goal)
                    frontier.append({'element':next,'priority':priority})
                    came_from[nextCode]=current
        #reconstruct path
        actual = goal
        path = [actual]
        while not (actual['x']==start['x'] and actual['y']==start['y']):
            currentCode="x"+str(actual['x'])+"y"+str(actual['y'])
            try:
                actual=came_from[currentCode]
            except KeyError:
                break
            path.append(actual)
        path.reverse()
        path.pop(0)
        return path

"""Actor; a game entity with attributes and moving and interactions capabilities"""
class Actor(GameObject):
    
    def __init__(self):
        GameObject.__init__(self)
        self.process_input=False
        self.process_update=True
        self.pos_x=0;
        self.pos_y=0;
        self.last_move_time=0.0
        self.speed=0.05  #Step delay
        self.path=[]

    def update(self,delta):
        if len(self.path)!=0:
            if (self.last_move_time>=self.speed):
                step=self.path.pop(0)
                self.last_move_time=0.0
                self.moveSprite(step['x']*config.SPRITE_WIDTH,step['y']*config.SPRITE_HEIGHT)
                self.pos_x=step['x']
                self.pos_y=step['y']
            else:
                self.last_move_time+=delta

    #Movement function following a path; returns True if movement is possible, False otherwise
    def moveTo(self,map_x,map_y,mapData):
        self.path=mapData.AStarPathfinding(self.pos_x,self.pos_y,map_x,map_y)
        self.dest_x=map_x*mapData.data.tilewidth
        self.dest_y=map_y*mapData.data.tileheight
        if self.path:
            return True
        else:
            return False

"""A class for the instancing and rendering of text"""
class Text(GameObject):
    
    def __init__(self,text,x=0,y=0,font=config.DEFAULT_FONT_PATH,size=config.DEFAULT_FONT_SIZE, rgb=(255,255,255)):
        GameObject.__init__(self,x,y)
        self.font = pygame.font.Font(font, size)
        self.text = self.font.render(text, True, rgb)
        self.image = self.text
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.spriteGroup=pygame.sprite.RenderPlain(self)


