import math
import sys, os
sys.path.insert(0, os.path.abspath('..'))

import pygame, pygbutton
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 520
WINDOWHEIGHT = 350

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

import commandConfig
import configuration.messageBrokerConfig as broker
buttonsPerRow = 2

class CommandSender:

    def __init__(self,publisher, topic):
        self.topic = topic
        self.msgPublisher = publisher

    def main(self):
        windowBgColor = WHITE

        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        
        WINDOWHEIGHT = math.floor((len(commandConfig.commands)-1)/buttonsPerRow)*50+130
        
        DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Command sender')

        buttonName = "button"
        i = 0
        buttons = []
        allButtons = []
        buttonCmd = {}
        allButtonNames = []
        
        myfont = pygame.font.SysFont("monospace", 15)
        
        yawText = "Topic: %s" % (self.topic)
        label = myfont.render(yawText , 1, (255,255,0))
        DISPLAYSURFACE.blit(label, (10, 10))
        
        for (command, valueType, description) in commandConfig.commands:
            print(command)
            print(valueType)
            print(description)
            xBias = 210* (i%buttonsPerRow)
            yBias = 50* math.floor(i/buttonsPerRow)
            i = i + 1
            btnName = "buttonName%s" % i
            cmd = "%s = pygbutton.PygButton((50+%d, 50+%d, 200, 30), '%s') " %  (btnName,xBias, yBias, description )
            exec(cmd)
            allButtons.append(eval(btnName))
            allButtonNames.append(btnName)
            buttonCmd[btnName] = (command, valueType, description)

        while True: # main game loop
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                
                for btnName in allButtonNames:
                    cmd = '%s.handleEvent(event)' % btnName
                    if 'click' in eval(cmd):
                        print("Button clicked: %s" % btnName)
                        (cmd, valueType, description) = buttonCmd[btnName]
                        print("Sending :%s" % cmd)
                        self.msgPublisher.publishMessage(self.topic, "%s\n" % cmd)


            for b in allButtons:
                b.draw(DISPLAYSURFACE)

            pygame.display.update()
            FPSCLOCK.tick(FPS)


if __name__ == '__main__':
    
    cmdSender = CommandSender(broker.msgPublisher,broker.robotInputQueue)
    cmdSender.main()
