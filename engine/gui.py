from engine import *
from glyph import Editor, Glyph, Macros

"""A class for the instancing and rendering of simple text"""
class Text(Sprite):
    
    def __init__(self,text,x=0,y=0,font=config.DEFAULT_FONT_PATH,size=config.DEFAULT_FONT_SIZE, rgb=(255,255,255), outlined=False, bold=False):
        Sprite.__init__(self,x,y,layer=10)
        #texto a renderizar
        self.font = pygame.font.Font(font, size)
        if bold:
            self.font.set_bold(True)
        if outlined:
            self.text=SpriteUtils.textOutline(self.font, text, rgb, (1,1,1))
        else:
            self.text = self.font.render(text, True, rgb)
        self.image = self.text
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.spriteGroup=pygame.sprite.LayeredDirty(self)

"""Glyph powered textbox. Work in progress"""
class TextBox(Sprite):
    def __init__(self,text,x=0,y=0,width=200,height=200,font=config.DEFAULT_FONT_PATH,size=config.DEFAULT_FONT_SIZE, rgb=(255,255,255)):
        #Glyph variables
        Sprite.__init__(self,x,y)
        self.x=x
        self.y=y
        self.entries={}
        Macros['red'] = ('color', (255, 0, 0))
        self.font = pygame.font.Font(font, size)
        self.args={'bkg'       : (30, 30, 30),'color'     : (255, 255, 255),'font'      : self.font,'spacing'   : 0}
        height=self.heightCalculation(text)
        self.glyph = Glyph(Rect(x+10, y+6, width, height), ncols=1, **self.args)
        self.entries['0']=text
        self.glyph.input(self.entries['0'])
        self.glyph.update()
        #Draw background and border
        self.drawBox()
        #Process input for link processing
        self.process_input=True

    def heightCalculation(self,text):
        words_per_line=6
        lines=0
        total_words = len(text.split())
        print (total_words)
        height = 16 * (total_words/words_per_line)
        if (height<16):
            height=16
        return height


    def drawBox(self):
        self.image = pygame.Surface((self.glyph.rect.width+20,self.glyph.rect.height+12))
        self.image.fill((30, 30, 30))
        pygame.draw.rect(self.image,(255,255,255),self.image.get_rect(),1)
        inner_rect=self.image.get_rect()
        inner_rect.x, inner_rect.y, inner_rect.width, inner_rect.height= inner_rect.x+4, inner_rect.y+4, inner_rect.width-8, inner_rect.height-8
        pygame.draw.rect(self.image,(255,255,255),inner_rect,1)
        self.image.blit(self.glyph.image,(10,6))
        self.rect=self.image.get_rect()
        self.rect.x,self.rect.y = self.x,self.y 
        self.spriteGroup=pygame.sprite.LayeredDirty(self)

    def addMacro(self, name, argument):
        Macros[name]=argument

    def addEntry(self, name, text):
        self.entries[name]=text

    def processInput(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            posx,posy=event.pos
            link = self.glyph.get_collisions(event.pos)
            if link:
                self.glyph.clear()
                self.glyph.input(self.entries[link], justify = 'justified') 
                self.glyph.update()
                self.drawBox()
            if self.rect.collidepoint(posx,posy):
                return True