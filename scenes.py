import pygame
from engine.engine import *

class MainScene(Scene):

    def __init__(self,screen):
        Scene.__init__(self,screen)

        #Mapita  
        self.map=Tilemap()
        self.map.loadTMXMap("data/map.tmx")
        self.add("map",self.map)
        #Enano
        self.enano = Enano()
        self.add("enano",self.enano)
        #Selector
        self.selector=MapCursor(self.map)
        self.add("selector",self.selector)

class MapCursor(GameObject):

    def __init__(self,mapData, x=0,y=0):
        GameObject.__init__(self)
        self.process_input=True 
        self.images={}
        self.images['red']=SpriteUtils.loadImage("selector.png")
        self.images['green']=SpriteUtils.loadImage("selector_green.png")
        self.images['cross']=SpriteUtils.loadImage("selector_cross.png")
        self.enabled=True
        self.loadImage("selector_green.png")
        self.map_x=0
        self.map_y=0
        self.mapData=mapData

    def switchEnabled(self,solid):
        if solid=='true':
            self.enabled=False
            self.changeImage(self.images['red'])
        else:
            self.enabled=True
            self.changeImage(self.images['green'])

    def processInput(self,event):
        if event.type == pygame.MOUSEMOTION:
            evx,evy= event.pos
            map_x=evx//config.SPRITE_WIDTH
            map_y=evy//config.SPRITE_HEIGHT
            if not (self.map_x==map_x and self.map_y==map_y):
                self.map_x=map_x
                self.map_y=map_y
                self.moveSprite(self.map_x*config.SPRITE_WIDTH,self.map_y*config.SPRITE_HEIGHT)
                self.switchEnabled(self.mapData.getTileProperty(self.map_x, self.map_y,'solid'))  
        if event.type == pygame.MOUSEBUTTONUP and self.enabled:
            move_able=self.getParent().getChild("enano").moveTo(self.map_x, self.map_y, self.mapData)
            if not move_able:
                self.changeImage(self.images['cross'])

class Enano(Actor):
    def __init__(self,x=0,y=0):
        Actor.__init__(self)
        self.loadImageFromSheet("pjs.png",0,2,config.SPRITE_WIDTH,config.SPRITE_HEIGHT)
        self.text2 = Text("Roberto Rivas Taxista")
        self.text2.moveSprite(self.x-int(self.text2.rect.width/2),self.y-16)
        self.add("name",self.text2,self.x-int(self.text2.rect.width/2),self.y-16)

