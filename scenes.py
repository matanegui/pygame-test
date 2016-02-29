import pygame
from engine import *
from engine.gui import *
from engine.map import *
from engine.actors import *

class GameScene(Scene):

    def __init__(self,screen):
        Scene.__init__(self,screen)

        #Mapita
        self.map=Tilemap(24,24)
        self.map.loadTMXMap("data/map3.tmx")
        self.add("map",self.map)
        #Selector
        self.selector=MapCursor(self.map)
        self.add("selector",self.selector)
        #Playable Character
        self.enano=Character("Pituto","white")
        self.add("pc",self.enano)
        self.enano.positionInMap(1,4)
        #Npc
        self.npc=GameObjectFactory.getGameObject("che","Character",{},["Jorgito", "red"])
        self.add("npc",self.npc)
        self.npc.positionInMap(8,12)

    def processInput(self,event):
        Scene.processInput(self,event)
        if event.type == pygame.MOUSEMOTION:
            evx,evy= event.pos
            if self.map.rect.collidepoint(evx,evy):
                self.add("selector",self.selector)
            else:
                if self.getComponent("selector") is not None:
                    self.remove("selector")
        return True

class MapCursor(Sprite):

    def __init__(self,mapData, x=0,y=0):
        Sprite.__init__(self)
        self.process_input=True
        self.images={}
        self.images['red']=SpriteUtils.loadImage("selector.png")
        self.images['green']=SpriteUtils.loadImage("selector_green.png")
        self.images['cross']=SpriteUtils.loadImage("selector_cross.png")
        self.canMove=True
        self.loadImage("selector_green.png")
        self.map_x=0
        self.map_y=0
        self.mapData=mapData

    def switchMoveStatus(self,solid):
        if solid=='true':
            self.canMove=False
            self.changeImage(self.images['red'])
        else:
            self.canMove=True
            self.changeImage(self.images['green'])

    def processInput(self,event):
        if event.type == pygame.MOUSEMOTION:
            evx,evy= event.pos
            map_x, map_y = self.mapData.positionToMapCoordinates(evx,evy)
            if not (self.map_x==map_x and self.map_y==map_y):
                self.map_x=map_x
                self.map_y=map_y
                rx,ry = self.mapData.mapCoordinatesToPosition(map_x,map_y)
                self.moveSprite(rx,ry)
                self.switchMoveStatus(self.mapData.getTileProperty(self.map_x, self.map_y,'solid'))
        if event.type == pygame.MOUSEBUTTONDOWN and self.canMove:
            move_able=self.getScene().getComponent("pc").moveToCell(self.map_x,self.map_y,self.mapData)
            if not move_able:
                self.changeImage(self.images['cross'])
            return True
