from engine.engine import *

class Enano(Actor):
    def __init__(self,x=0,y=0):
        Actor.__init__(self)
        self.loadImageFromSheet("pjs.png",0,2,config.SPRITE_WIDTH,config.SPRITE_HEIGHT)
        self.text2 = Text("Rolando Rivas Taxista")
        self.text2.moveSprite(self.x-int(self.text2.rect.width/2),self.y-16)
        self.add("name",self.text2,self.x-int(self.text2.rect.width/2),self.y-16)

    def handleEvent(self,event):
    	if (event['name']=="Move To Cell"):
    		move_able=self.moveTo(event['map_x'], event['map_y'], event['mapData'])
    		event['response']=move_able
    		return event