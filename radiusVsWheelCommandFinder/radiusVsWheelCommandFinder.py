import math
import sys, os
sys.path.insert(0, os.path.abspath('..'))

import pygame, pygbutton
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 350

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

import configuration.messageBrokerConfig as broker
import mapCreator.mqttDatapump as mqttDatapump
variablesPerRow = 2
MAX_DATA_LENGTH = 1000

class RadiusVsWheelCommandFinder:



    def __init__(self,subscriber, topic, car):
        self.topic = topic
        self.msgSubscriber = subscriber
        self.loadedData = {}
        self.DISPLAYSURFACE = ""
        self.car = car

    def main(self):
        dataload = mqttDatapump.MqttDatapump()
        dataload.startDatapump()
        
        STATE = 0
        prevDiffYaw = 0
        prevDist = 0
        prevTheta_w_deg = 0
        while 1:                
            if dataload.getDataLength() > 0:
                data = dataload.getData()
                self.car.insertMeasurements(data)
                self.car.nextIteration()
                #print("yaw = %.1f" % (self.car.slamAlgorithm.yawDiff))
                if 'theta_w_deg' in data:
                    print("data....")
                    # New wheel angle, start all over.
                    if prevTheta_w_deg != data['theta_w_deg']:
                        print("New theta_w_deg")
                        STATE = 0
                        prevTheta_w_deg = data['theta_w_deg']
                        
                    
                    # If we have gone one round, then start to measure radius
                    if STATE == 0 and abs(prevDiffYaw - self.car.slamAlgorithm.yawDiff)*180/math.pi > 360 :
                        STATE = 1
                        prevDiffYaw = self.car.slamAlgorithm.yawDiff
                        prevDist = data['l_car_mm']
                    if STATE == 1:
                        # We have that O = 2*pi*r -> R = O/2*pi 
                        O = data['l_car_mm'] - prevDist
                        yaw = abs(prevDiffYaw - self.car.slamAlgorithm.yawDiff)
                        if yaw > 0:
                            R = O/yaw
                            print("Radius@%.1f=%.1f" % (prevTheta_w_deg, R))
                        
            

if __name__ == '__main__':
    import masterConfig
    cmdSender = RadiusVsWheelCommandFinder(broker.msgPublisher,broker.robotInputQueue, car=masterConfig.car)
    cmdSender.main()
