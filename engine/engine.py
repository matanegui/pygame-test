import pygame
from pygame.locals import *
import config
import os, sys
import math
import warnings


"""
    Helper functions for image loading.
"""
class SpriteUtils:

    #Load sprite from file
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

    #Load sprite from spritesheet
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

    #Draw hollow text
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

    #Draw outlined text
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

    def remove(self,ID):
        self.components.pop(ID)

    def getComponent(self,ID):
        try:
            component=self.components[ID]
        except KeyError, e:
            component=None
        return component

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

    def __init__(self,x=0,y=0,layer=0):
        pygame.sprite.DirtySprite.__init__(self)
        self.layer=layer
        GameObject.__init__(self)
        self.offset_x=0
        self.offset_y=0
        self.x=x
        self.y=y
        self.rect = pygame.Rect(self.x,self.y,0,0)

    def add(self, ID, component, offset_x=0, offset_y=0):
        if (offset_x!=0 or offset_y!=0):
            component.offset_x=offset_x
            component.offset_y=offset_y
            component.moveSprite(self.x+offset_x,self.y+offset_y)
        if component.spriteGroup:                           #CHEQUEAR SI NO ES MEJOR INICIALIZAR EL SPRITEGROUP EN GAMEOBJECT!
            for sprite in component.spriteGroup.sprites():
                if self.spriteGroup:
                    self.spriteGroup.add(sprite, layer=sprite.layer)
                else:
                    self.spriteGroup=pygame.sprite.LayeredDirty(sprite)
                #component.spriteGroup.remove(sprite)
        self.components[ID]=component
        self.components[ID].parent=self

    def remove(self,ID):
        component = self.components[ID]
        if component.spriteGroup:
            for sprite in component.spriteGroup.sprites():
                self.spriteGroup.remove(sprite)
        self.components.pop(ID)



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
        self.rect=pygame.Rect(self.x,self.y,width,height)
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
    def getClassOriginal(classname):
        for path in config.COMPONENT_MODULES:
            parts = path.split('.')
            module = ".".join(parts[:-1])
            m = __import__( module )
            for comp in parts[1:]:
                if m is not None:
                    try:
                        m = getattr(m, comp)
                    except AttributeError:
                        pass
            if m is not None:
                try:
                    m = getattr(m, classname)
                    return m
                except AttributeError:
                    pass

    #Instantiate class with extending parameter
    @staticmethod
    def getGameObject(classname,base_class='GameObject',args={}, params=[]):
       ParentClass=GameObjectFactory.getClassOriginal(base_class)
       if ParentClass is not None:
           Class=type(classname, (ParentClass,), args)
           return Class(*params)
       else:
           return None


"""Basic Scene structure; contains methods for drawing, updating and input handling."""
class Scene(Sprite):
    def __init__(self,screen):
        GameObject.__init__(self)
        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill((39,40,34))
        self.dirties=[]

    def processInput(self, event):
        handled=False
        for ID, component in self.components.items():
            if component.process_input and not handled:
                handled=component.processInput(event)
                if handled is None:
                    handled=False

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
