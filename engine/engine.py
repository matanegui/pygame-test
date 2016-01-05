import pygame
from pygame.locals import *
import config
import os, sys
import pytmx
from pytmx.util_pygame import load_pygame
import math

""" 
    Helper functions for image loading.
"""
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

    @staticmethod
    def textHollow(font, message, fontcolor):
        notcolor = [c^0xFF for c in fontcolor]
        base = font.render(message, 0, fontcolor, notcolor)
        size = base.get_width() + 2, base.get_height() + 2
        img = pygame.Surface(size, 16)
        img.fill(notcolor)
        base.set_colorkey(0)
        img.blit(base, (0, 0))
        img.blit(base, (2, 0))
        img.blit(base, (0, 2))
        img.blit(base, (2, 2))
        base.set_colorkey(0)
        base.set_palette_at(1, notcolor)
        img.blit(base, (1, 1))
        img.set_colorkey(notcolor)
        return img

    @staticmethod
    def textOutline(font, message, fontcolor, outlinecolor):
        base = font.render(message, 0, fontcolor)
        outline = SpriteUtils.textHollow(font, message, outlinecolor)
        img = pygame.Surface(outline.get_size(), 16)
        img.blit(base, (1, 1))
        img.blit(outline, (0, 0))
        img.set_colorkey(0)
        return img

""" 
    Basic event specification class.
"""
class Event():
    def __init__(self,name,target=[],parameters={}):
        self.name=name;
        self.target=target
        self.parameters=parameters

""" 
    Basic GameObject structure.
    -Support for tree-like GameObject hierarchy
    -Overridable input processing and logic updating methods.
    -Support for event firing and handling along its hierarchy.
"""
class GameObject():
    
    def __init__(self,x=0,y=0):
        self.components = {}
        self.attributes={}
        self.spriteGroup = None
        self.parent = None
        self.process_input=False
        self.process_update=False
        self.process_events=False
        self.eventHandlers={}
    
    def add(self, ID, component, offset_x=0, offset_y=0):
        component.offset_x=offset_x
        component.offset_y=offset_y
        self.components[ID]=component;
        self.components[ID].parent=self

    def getComponent(self,ID):
        return self.components[ID]

    def getParent(self):
        return self.parent

    def getScene(self):
        if self.parent is None:
            return self
        else:
            return self.parent.getScene()

    def processInput(self, event):
        pass

    def update(self,delta):
        pass

    def draw(self):
        pass

    def fireEvent(self,event):
        scene=self.getScene()
        if scene:
            event=scene.sendEvent(event)
        return event
            

    def sendEvent(self,event):
        #no target means this is the wanted Game Object
        if not event['target']:
            for ID, component in self.components.iteritems():
                event=component.sendEvent(event)
            event=self.handleEvent(event)     
        else:
            current_target=self.components[event['target'][0]]
            if current_target:
                    event['target'].pop(0)
                    event=current_target.sendEvent(event)
        return event

    #Meant to ve overriden by inheriting classes for specific event handling
    def handleEvent(self,event):
        if (self.process_events):
            for eventName, handler in self.eventHandlers.iteritems():
                if (event['name']==eventName):
                    event=handler(event)
        return event

""" 
    A Sprite class; extends Game Object and pygame DirtySprite, adding drawing capabilities to the basic GO.
"""
class Sprite(GameObject,pygame.sprite.DirtySprite):
    
    def __init__(self,x=0,y=0):
        pygame.sprite.DirtySprite.__init__(self)
         
        GameObject.__init__(self)
        self.offset_x=0
        self.offset_y=0
        self.x=x
        self.y=y
    
    def add(self, ID, component, offset_x=0, offset_y=0):
        if (offset_x!=0 or offset_y!=0):
            component.offset_x=offset_x
            component.offset_y=offset_y
            component.moveSprite(offset_x,offset_y)
        for sprite in component.spriteGroup.sprites():
            if self.spriteGroup:    
                self.spriteGroup.add(sprite)
            else:
                self.spriteGroup=pygame.sprite.LayeredDirty(sprite)
            component.spriteGroup.remove(sprite)
        self.components[ID]=component
        self.components[ID].parent=self
        
    def loadImage(self,path):
        self.image = SpriteUtils.loadImage(path)
        self.rect=self.image.get_rect()
        self.rect.x=self.x
        self.rect.y=self.y
        self.spriteGroup=pygame.sprite.LayeredDirty(self)

    #Render using given image and rect
    def renderImage(self,image,rect):
        self.image = image
        colorkey = image.get_at((0,0))
        if (tuple(colorkey))==(0,0,0,255):
            image.set_colorkey(colorkey, RLEACCEL)
        self.rect=rect
        self.spriteGroup=pygame.sprite.LayeredDirty(self)

    def changeImage(self,image):
        self.image = image
        self.rect=self.image.get_rect()
        self.rect.x=self.x
        self.rect.y=self.y
        self.spriteGroup=pygame.sprite.LayeredDirty(self)

    def loadImageFromSheet(self,path,sheet_x,sheet_y,width,height):
        tiles=SpriteUtils.loadSpriteSheet(path,width, height)
        self.image=(tiles[sheet_x][sheet_y])
        self.rect=pygame.Rect(self.x*width,self.y*height,width,height)
        self.spriteGroup=pygame.sprite.LayeredDirty(self)

    def moveSprite(self,x,y):
        self.x=x
        self.y=y
        self.rect.x=x
        self.rect.y=y
        self.dirty=1
        for ID, component in self.components.iteritems():
            component.moveSprite(component.offset_x+x,component.offset_y+y)

    def moveSpriteRelative(self,x,y):
        self.x+=int(x)
        self.y+=int(y)
        self.rect.x+=int(x)
        self.rect.y+=int(y)     
        self.dirty=1
        for ID, component in self.components.iteritems():
            component.moveSpriteRelative(x,y)

    def draw(self, screen):
        if (self.spriteGroup is not None):
            self.spriteGroup.draw(screen)
        for ID, component in self.components.iteritems():
            component.draw(screen)

"""
Game Object factory; searches both instanced components and XML archives for the searched component.
"""
class GameObjectFactory():

    def __init__():
        pass

    #Get coded class by name
    @staticmethod
    def getClass(classname):
        for path in config.COMPONENT_MODULES:
            parts = path.split('.')
            module = ".".join(parts[:-1])
            m = __import__( module )
            for comp in parts[1:]:
                try:
                    m = getattr(m, classname)
                    return m
                except AttributeError:
                    pass          

    #Instantiate class with extending parameter
    @staticmethod
    def getGameObject(classname,base_class='GameObject',args={}):
       ParentClass=GameObjectFactory.getClass(base_class)
       Class=type(classname, (ParentClass,), args)
       return Class()



"""Basic Scene structure; contains methods for drawing, updating and input handling."""
class Scene(Sprite):
    def __init__(self,screen):
        GameObject.__init__(self)
        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill((39,40,34))
        self.dirties=[]
    
    def processInput(self, event):
        for ID, component in self.components.iteritems():
            if component.process_input:
                component.processInput(event)

    def update(self,delta):
        for ID, component in self.components.iteritems():
            if component.process_update:
                component.update(delta)

    def draw(self, screen):
        #Default: components render
        self.spriteGroup.clear(screen,self.background)
        rects=self.spriteGroup.draw(screen) 
        pygame.display.update(rects)

    def switchToScene(self, next_scene):
        self.next = next_scene

"""Basic tile object"""
class Tile(Sprite):
    def __init__(self):
        Sprite.__init__(self)

"""Basic tilemap, TMX loaded, pytmx powered"""
class Tilemap(Sprite):

    def __init__(self):
        Sprite.__init__(self)
        self.tileOrder=[]
        self.data = None
        self.width=0
        self.height=0

    #Full TMX map loading (includes tile properties)
    def loadTMXMap(self,path):
        self.data = load_pygame(path)
        #definir mapita
        self.width=self.data.width
        self.height=self.data.height
        layersAmount=len(self.data.layers)
        for idz in range(layersAmount):
            for idx, idy, image in self.data.layers[idz].tiles():
                    tile = Tile()
                    tile.renderImage(image.convert(),pygame.Rect(idx*self.data.tilewidth,idy*self.data.tileheight,self.data.tilewidth,self.data.tileheight))
                    tileID="x"+str(idx)+"y"+str(idy)+"z"+str(idz)
                    self.tileOrder.append(tileID)
                    self.add(tileID,tile)

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
        if self.isValidTile(map_x-1,map_y) and (not movement_check or self.getTileProperty(map_x-1,map_y,'solid',1)!='true'):
            neighbors.append({'x':map_x-1,'y':map_y})
        if self.isValidTile(map_x-1,map_y-1) and (not movement_check or self.getTileProperty(map_x-1,map_y-1,'solid',1)!='true'):
            neighbors.append({'x':map_x-1,'y':map_y-1})
        if self.isValidTile(map_x,map_y-1) and (not movement_check or self.getTileProperty(map_x,map_y-1,'solid',1)!='true'):
            neighbors.append({'x':map_x,'y':map_y-1})
        if self.isValidTile(map_x+1,map_y-1) and (not movement_check or self.getTileProperty(map_x+1,map_y-1,'solid',1)!='true'):
            neighbors.append({'x':map_x+1,'y':map_y-1})
        if self.isValidTile(map_x+1,map_y) and (not movement_check or self.getTileProperty(map_x+1,map_y,'solid',1)!='true'):
            neighbors.append({'x':map_x+1,'y':map_y})
        if self.isValidTile(map_x+1,map_y+1) and (not movement_check or self.getTileProperty(map_x+1,map_y+1,'solid',1)!='true'):
            neighbors.append({'x':map_x+1,'y':map_y+1})
        if self.isValidTile(map_x,map_y+1) and (not movement_check or self.getTileProperty(map_x,map_y+1,'solid',1)!='true'):
            neighbors.append({'x':map_x,'y':map_y+1})
        if self.isValidTile(map_x-1,map_y+1) and (not movement_check or self.getTileProperty(map_x-1,map_y+1,'solid',1)!='true'):
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

    def draw(self,screen):
        for ID in self.tileOrder:
            self.components[ID].draw(screen)  

"""Actor; a game entity with attributes and moving and interactions capabilities"""
class Actor(Sprite):
    
    def __init__(self):
        Sprite.__init__(self)
        self.process_input=False
        self.process_update=True
        self.pos_x=0;
        self.pos_y=0;
        self.pos_z=1
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
                self.fireEvent({"name": "Step Over", "target": ["map","x"+str(step['x'])+"y"+str(step['y'])+"z0"]})
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
class Text(Sprite):
    
    def __init__(self,text,x=0,y=0,font=config.DEFAULT_FONT_PATH,size=config.DEFAULT_FONT_SIZE, rgb=(255,255,255)):
        Sprite.__init__(self,x,y)
        #texto a renderizar
        self.font = pygame.font.Font(font, size)
        self.font.set_bold(True)
        self.text=SpriteUtils.textOutline(self.font, text, rgb, (1,1,1))
        #self.text = self.font.render(text, True, rgb)
        self.image = self.text
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.spriteGroup=pygame.sprite.LayeredDirty(self)



