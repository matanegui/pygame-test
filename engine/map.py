from engine import *
import pytmx
from pytmx.util_pygame import load_pygame

"""Basic tile object"""
class Tile(Sprite):
    def __init__(self):
        Sprite.__init__(self)

"""Basic tilemap, TMX loaded, pytmx powered"""
class Tilemap(Sprite):

    def __init__(self):
        Sprite.__init__(self)
        self.tileOrder=[]
        self.layer=1000
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
