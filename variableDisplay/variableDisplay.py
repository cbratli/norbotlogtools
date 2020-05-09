import math
import sys, os
sys.path.insert(0, os.path.abspath('..'))

import pygame, pygbutton
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

import variableDisplayConfig
import configuration.messageBrokerConfig as broker
import mapCreator.mqttDatapump as mqttDatapump
variablesPerRow = 2
MAX_DATA_LENGTH = 100

class VariableDisplay:



    def __init__(self,subscriber, topic):
        self.topic = topic
        self.msgSubscriber = subscriber
        self.loadedData = {}
        self.DISPLAYSURFACE = ""

    def main(self):
        dataload = mqttDatapump.MqttDatapump()
        dataload.startDatapump()

        windowBgColor = WHITE

        pygame.init()
        FPSCLOCK = pygame.time.Clock()        
        WINDOWHEIGHT = 500
        DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.DISPLAYSURFACE = DISPLAYSURFACE
        pygame.display.set_caption('Variable display')

        myfont = pygame.font.SysFont("monospace", 18)
                
        while True: # main game loop
            for event in pygame.event.get(): # event handling loop
                 if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                        
            if dataload.getDataLength() > 1:
                data = dataload.getData()
                self.addData(data)
            
            DISPLAYSURFACE.fill(BLACK)
            
            self.plotAndPopTopic()
            i = 0
            for key in self.loadedData.keys():
                xBias = 300* (i%variablesPerRow)
                yBias = 30* math.floor(i/variablesPerRow)
                yawText = "%s : %s" % (key, self.loadedData[key][-1])
                label = myfont.render(yawText , 1, (255,255,0))
                DISPLAYSURFACE.blit(label, (10+xBias, 60+yBias))
                i = i + 1

            pygame.display.update()
            #FPSCLOCK.tick(FPS)

    def plotAndPopTopic(self):
        myfont = pygame.font.SysFont("monospace", 18)
        key = 'topic'
        if key in self.loadedData:
            topic = self.loadedData[key]
            yawText = "%s : %s" % (key, self.loadedData[key][-1])
            label = myfont.render(yawText , 1, (255,255,255))
            self.DISPLAYSURFACE.blit(label, (100, 10))
            self.loadedData.pop(key)
            
    def addData(self,data):
        for key in data.keys():
            if key in self.loadedData:
                self.loadedData[key].append(data[key])
                if len(self.loadedData[key]) > MAX_DATA_LENGTH:
                    self.loadedData[key].pop(0)
                    print("Popping data")
            else:
                self.loadedData[key] = []
                self.loadedData[key].append(data[key])
            

if __name__ == '__main__':
    
    cmdSender = VariableDisplay(broker.msgPublisher,broker.robotInputQueue)
    cmdSender.main()
