from engine import *
from gui import Text
import config

"""Actor; a game entity with attributes and moving and interactions capabilities"""
class Actor(Sprite):
    
    def __init__(self,x=0,y=0):
        Sprite.__init__(self,x,y)
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

    #Color an actor
    def colorSprite(self, colorName):
        arr = pygame.surfarray.pixels3d(self.image)
        colors = config.UNIT_COLORS[colorName]
        if colors is not None:
            for row in range(len(arr)):
                for cell in arr[row]:
                    color = (cell[0],cell[1],cell[2])
                    if color == (255,255,255):
                        cell[0],cell[1],cell[2]=colors["primary"][0],colors["primary"][1],colors["primary"][2]
                    elif color == (155,173,183):
                        cell[0],cell[1],cell[2]=colors["secondary"][0],colors["secondary"][1],colors["secondary"][2]


class Character(Actor):
    def __init__(self,name,color,x=0,y=0):
        Actor.__init__(self)
        self.process_events=True
        self.loadImageFromSheet("pjs.png",0,2,config.SPRITE_WIDTH,config.SPRITE_HEIGHT)
        self.char_name = Text(name,bold=True,outlined=True)
        self.char_name.moveSprite(self.x+int(self.rect.width/2)-int(self.char_name.rect.width/2),self.y-16)
        self.add("name",self.char_name,+int(self.rect.width/2)-int(self.char_name.rect.width/2),self.y-16)
        self.colorSprite(color)
        self.process_input=True
        

    def moveToCell(self,map_x,map_y,mapData):
        return self.moveTo(map_x,map_y, mapData)

    def processInput(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN: #click
            evx,evy= event.pos
            if self.rect.collidepoint(evx,evy):
                return True