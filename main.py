# This Python file uses the following encoding: utf-8

import os, sys
import pygame


from scenes import MainScene

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

#Juego
class PyGame:
	
	def __init__(self):
		#Pygame init
		pygame.init()
		#Posicion de la ventana
		os.environ['SDL_VIDEO_WINDOW_POS'] = str(500) + "," + str(200)
		self.screen = pygame.display.set_mode((960,540))
		self.currentScene=MainScene(self.screen)

	#Main loop. Delegates everything on running scene
	def MainLoop(self):
	    #Main loop
		clock=pygame.time.Clock()
		loop=True
		FPS=30
		second=float(1000)
		while loop:
			delta=clock.tick(FPS)/second
			for event in pygame.event.get():
				self.currentScene.processInput(event)
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
					sys.exit()
			self.currentScene.update(delta)
			self.currentScene.draw(self.screen)



if __name__ == "__main__":
    MainWindow = PyGame()
    MainWindow.MainLoop()