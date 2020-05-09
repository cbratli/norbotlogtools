import sqlite3
import time
import datetime
import math

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mqttDatapump

#from carAlgorithm.Car import *
import pygame
import sys

import os
basePath = os.path.abspath(os.path.join('..'))
sys.path.append(basePath) 


class MidlePointEditor:
    def __init__(self,car):
        self.car = car
        self.selectedMidlePoint = -1
        
    def keydown(self,evt):
        if(evt[pygame.K_DELETE]): self.deletePoint() 
        if(evt[pygame.K_RIGHT]): self.movePointXY(5,0) 
        if(evt[pygame.K_LEFT]): self.movePointXY(-5,0)
        if(evt[pygame.K_UP]): self.movePointXY(0,0-5)
        if(evt[pygame.K_DOWN]): self.movePointXY(0,5)

    def mouseEvents(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            index = self.car.slamAlgorithm.getMidlePointClosestToMapScreenPosition(pos)
            print("Mouse pressed : pos %d, %d" % (pos[0],pos[1]) )
            print("MidlePoint: %d" % (index ))
            self.selectedMidlePoint = index
            
    def deletePoint(self):
        if self.selectedMidlePoint > -1:
            self.car.slamAlgorithm.removeMidlePoint(self.selectedMidlePoint)
        self.selectedMidlePoint = -1

    def movePointXY(self,x,y):
        if self.selectedMidlePoint > -1:
            pos = self.car.slamAlgorithm.midlePoints[self.selectedMidlePoint]
            #self.car.slamAlgorithm.midlePoints[self.selectedMidlePoint] = (pos[0]+x, pos[1]+y)
            self.car.slamAlgorithm.setMidlePointPosition(self.selectedMidlePoint,(pos[0]+x, pos[1]+y))
            
            #lines = [pos,pos]
            #pygame.draw.lines(self.screen, (0,0,0), False, lines, 1)
            #lines = [self.car.slamAlgorithm.midlePoints[self.selectedMidlePoint],self.car.slamAlgorithm.midlePoints[self.selectedMidlePoint] ]
            #pygame.draw.lines(self.screen, blue, False, lines, 1)

class SensorPlotter(object):
    screenX = 1000
    screenY = 1000

    def __init__(self, car, simulateForwardSpeed=True, rotateCar=True):
        self.simulateForwardSpeed = simulateForwardSpeed
        self.rotateCar = rotateCar
        #self.foundMap = np.zeros([self.screenX,self.screenY,3], np.uint8)
        self.car = car
        
        self.midlePointEditor = MidlePointEditor(car)
        self.currentMode = self.midlePointEditor

    def playback(self):
        self.plotCar()

    def keydown(self,evt):
        self.currentMode.keydown(evt)
        if(evt[pygame.K_s]): self.car.slamAlgorithm.saveMap();print("Map saved")
        if(evt[pygame.K_l]): self.car.slamAlgorithm.loadMap('filename');print("Map loaded")
        if(evt[pygame.K_r]): self.car.slamAlgorithm.redrawMap(); print("Redrawing map")

    def mouseEvents(self,event):
        self.currentMode.mouseEvents(event)
    
        
    def plotCar(self):
        pygame.init()

        #dataload = dataloaderSqlite3.Dataloader('rodlog.db')
        #dataload = logReaderAmqp.LogReaderAmqp()
        dataload = mqttDatapump.MqttDatapump()
        dataload.startDatapump()


        red = (255,0,0)
        green = (0,255,0)
        blue = (0,0,255)
        darkBlue = (0,0,128)
        white = (255,255,255)
        black = (0,0,0)
        pink = (255,200,200)

        screenX = self.screenX
        screenY = self.screenY

        screen = pygame.display.set_mode((screenX,screenY))
        self.screen = screen

        from time import sleep
        # We have 1000 pixels in x and 480 pixels in y. The measurements are in mm. Assume each pixel on the screen 1 cm -> 10 m screen.
        # so a sensor value of 1000 must must be scaled to 100.
        #time.sleep(15)
        

        carX = self.screenX/2/self.car.slamAlgorithm.scale
        carY = self.screenY/2/self.car.slamAlgorithm.scale        
        
        self.car.x = carX;
        self.car.y = carY;
        
        dT = 10e-3
        from numpy import zeros

        myfont = pygame.font.SysFont("monospace", 15)
        
        print ("Waiting for data...")
        while dataload.getDataLength() < 2:
            keys = pygame.key.get_pressed()
            event = pygame.event.poll()
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()
            #print("Waiting for data")
            #print(x, y)
            self.keydown(keys)
            self.mouseEvents(event)
            
            pygame.surfarray.blit_array(screen,self.car.slamAlgorithm.foundMap)
            pygame.display.update()
        
        data = dataload.getData()
        self.car.insertMeasurements(data)
        
        
        speed = 0
        yaw_rad = 0.0
        for i in range(1,dataload.getDataLength()+100000):
            
            keys = pygame.key.get_pressed()
            #event = pygame.event.poll()
            ev = pygame.event.get()
            
            for event in ev:
                if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                    pygame.quit()
                    sys.exit()
                self.keydown(keys)
                self.mouseEvents(event)
        
            datapumped = 0
            while dataload.getDataLength() > 2 and datapumped < 100:
                datapumped += 1
                data = dataload.getData()
                
                self.car.insertMeasurements(data)
                self.car.nextIteration()
               
            if datapumped > 10:
                print ("Datapumped %d" % datapumped)
               
            screen.fill(black)

            # Plot the car on the map inside the SLAM algorithm
            r = 0
            g = 0 #1
            b = 1
            #self.plotPoint(car.x,car.y,r,g,b)
            
            # Plot the MAP from the slam algorithm.
            pygame.surfarray.blit_array(screen,self.car.slamAlgorithm.foundMap)
            #pygame.surfarray.blit_array(screen,self.foundMap)

            #pygame.draw.lines(screen, pink, False, [(car.x*self.car.slamAlgorithm.scale,car.y*self.car.slamAlgorithm.scale),(car.x*self.car.slamAlgorithm.scale+1,car.y*self.car.slamAlgorithm.scale+1)], 1)


            # Draw what the sensors see.
            yBias = 0
            for (sensorKeyName,lines) in self.car.dsLines_carFrame.items():
                yBias +=20;
                #print lines

                #l = lines[0]
                l = lines
                p0 = l[0]
                p1 = l[1]
                p0_0 = p0[0]*self.car.slamAlgorithm.scale
                p0_1 = p0[1]*self.car.slamAlgorithm.scale
                p1_0 = p1[0]*self.car.slamAlgorithm.scale
                p1_1 = p1[1]*self.car.slamAlgorithm.scale
                lines = [(p0_0,p0_1),(p1_0, p1_1) ]
                #pygame.draw.lines(screen, pink, False, lines, 1)
                pygame.draw.lines(screen, pink, False, lines, 1)

                #yawToUse = 0.0001/180.0*math.pi+self.car.yaw+self.car.ds[sensorKeyName].placement.yaw
                yawToUse = self.car.yaw+self.car.ds[sensorKeyName].placement.yaw
                maxLength = 250000.0
                # The output is in the map frame.
                (dist,hitX,hitY) = self.car.slamAlgorithm.castSingleRay(yawToUse, maxLength)
                
                lines = [(p0_0,p0_1),(hitX, hitY) ]
                pygame.draw.lines(screen, green, False, lines, 1)
                lengthText = "Dist = %.2f, distX = %.2f, distY = %.2f, i=%i   " % (dist,p0_0 - hitX, p0_1 - hitY,i)
                #print lengthText
                label = myfont.render(lengthText , 1, (255,255,0))
                screen.blit(label, (100, 50+yBias))
        
            # render text
            yawText = "%.3f" % (self.car.yaw)
            label = myfont.render(yawText , 1, (255,255,0))
            yBias +=20;
            screen.blit(label, (100, 50+yBias))
            yBias +=20;
            yawText = "yawDiff = %.3f" % (self.car.slamAlgorithm.yawDiff)
            label = myfont.render(yawText , 1, (255,255,0))
            screen.blit(label, (100, 50+yBias))
            yBias +=20;
            yawText = "carX=%.0f   - carY = %.0f" % (self.car.x, self.car.y)
            label = myfont.render(yawText , 1, (255,255,0))
            screen.blit(label, (100, 50+yBias))

            pos = pygame.mouse.get_pos()
            mapPos = self.car.slamAlgorithm.getMapPosFromScreenPos(pos)
            yBias +=20;
            yawText = "mouseX=%.0f   - mouseY = %.0f (Map position %d %d)" % (pos[0],pos[1], mapPos[0], mapPos[1])
            label = myfont.render(yawText , 1, (255,255,0))
            screen.blit(label, (100, 50+yBias))
            
            
            prevPoint = self.car.slamAlgorithm.midlePoints[0]
            for midlePoint in self.car.slamAlgorithm.midlePoints:
                print("Drawing line...")
                # Scale the points....
                
                lines = [prevPoint,midlePoint]
                #pygame.draw.lines(screen, pink, False, lines, 1)
                pygame.draw.lines(screen, pink, False, lines, 1)

                
                prevPoint = midlePoint
                

            pygame.display.update()
            
    def plotPoint(self,x,y,r,g,b):
            x = x*self.car.slamAlgorithm.scale
            y = y*self.car.slamAlgorithm.scale
            if x > 0 and x < self.car.slamAlgorithm.foundMap.shape[0] and y>0 and y < self.car.slamAlgorithm.foundMap.shape[1]:
                self.car.slamAlgorithm.foundMap[x,y,0] = int(255*r)
                self.car.slamAlgorithm.foundMap[x,y,1] = int(255*g)
                self.car.slamAlgorithm.foundMap[x,y,2] = int(255*b)

    def plotPointFromLine(self,l,r,g,b):
            p0 = l[0]
            p1 = l[1]
            p0_0 = p0[0]
            p0_1 = p0[1]
            p1_0 = p1[0]
            p1_1 = p1[1]
            self.plotPoint(0,0,p1_0,p1_1,r,g,b)



if __name__ == '__main__':

    import masterConfig
    sensorPlotter = SensorPlotter(car=masterConfig.car)
    sensorPlotter.playback()
