import sqlite3
import time
import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pygame
import sys
import math
import os

configPath = os.path.abspath(os.path.join('..', 'carAlgorithm'))
sys.path.append(configPath) 

from ReplayDistanceSensor import *

class Rimfakse(object):
    """"
        A car has sensors. (you need to define them here)
        A travelled distance (for instance one or more encoders or )
        A model (bicycle or Differential Drive)
        A heading measurement or estimate
        It has an algorithm (slam algorithm)
        
        
        If setting up a new car, please revise the following methods:
        * __init__
        * _distanceSensorSetup
        * insertMeasurments
        
    """
    
    FRONT_1 = "l_f1_mm"
    RIGHT_1 = "l_r1_mm"
    LEFT_1 = "l_l1_mm"
    
    def __init__(self, x,y, yaw):
        self.x = x
        self.y = y
        self.yaw = yaw
        
        self.robotOutputQueue = "norbot/folkrace/rimfakse/out"
        self.robotInputQueue = "norbot/folkrace/rimfakse/in"
        
        self.ds = {}    # Distance sensors.
        self._distanceSensorSetup() # Distance sensors in the distane sensor frame.
        self.midlePoint =(x,y)  # TODO: Replace this with None, since we have to use the sensors.
        self.midlePoints = []

        import SimpleSlam
        self.slamAlgorithm = SimpleSlam.SimpleSlam(self)
        self.slamAlgorithm.addRightSensor(self.RIGHT_1)
        self.slamAlgorithm.addLeftSensor(self.LEFT_1)



        self.dsLines_carFrame = {}   # The distance sensor lines in the car frame.
        self.l_car_mm = None
        self.prev_l_car_mm = None
        
    def insertMeasurements(self,data):
        """This method takes inn all available measurements and distributes them to the correct
        sensors and estimates the car will need"""
        
        # Insert all distance measurements.
        for key in data.keys():
            if key in self.ds:
                self.ds[key].insertNewMeasurement(data[key])
        
        if 'yaw_car_deg' in data:
            yaw_deg = data['yaw_car_deg']
            self.yaw = (yaw_deg)/180.0*3.14159 #- 3.141592/2
        else:
            print("yaw not found")
                
        self.prev_l_car_mm = self.l_car_mm
        if 'l_car_mm' in data:
            dT = 20e-3 # Use the information in data
            self.l_car_mm = float(data['l_car_mm'])
            
            # Is it first iteration?
            if self.prev_l_car_mm == None:
                self.prev_l_car_mm = self.l_car_mm
            
        else:
            print("l_car_mm not present")
        
        # Note that since the encoder is only counting up, we need to make this delta negative
        # if we have negative pwm to motor.
        if self.l_car_mm != None and self.prev_l_car_mm != None:
            self.delta_l_mm = self.l_car_mm - self.prev_l_car_mm
        else:    
            self.delta_l_mm = 0
        
    def _distanceSensorSetup(self):

        xCenter = 20.0*1;
        self.ds[self.LEFT_1] = ReplayDistanceSensor(xCenter+40,7.75,0,-45.0/180.0*math.pi,0)
        self.ds[self.RIGHT_1] = ReplayDistanceSensor(xCenter+40,-7.75,0,45.0/180.0*math.pi,0)
        self.ds[self.FRONT_1] = ReplayDistanceSensor(xCenter+20,0,0,105.0/180.0*math.pi,0)


    def getDistanceSensors(self):
        pass

    def nextIteration(self):
        # Every dT timestep, we run this loop,
        # this loop reads the sensors. (And we may have real sensors or fake sensors(that replay recorded sensor data or simulated data))
        #
        # The read sensor data is fed to the slamAlgorithm
        #

        # Read yaw
        # Read distance measurements.

        self._readDistanceMeasurements()
        self._calculateCarFrameCoordinateXy()
        self._calculateCarPositionInMapFrame()
        self.slamAlgorithm.iterate()

    def _calculateCarPositionInMapFrame(self):
        self.x = self.x + math.cos(self.yaw) * self.delta_l_mm
        self.y = self.y + math.sin(self.yaw) * self.delta_l_mm
        
    def _readDistanceMeasurements(self):
        for (sensorKeyName,sensor) in self.ds.items():
            sensor.takeMeasurement()
            
    def _calculateCarFrameCoordinateXy(self):
        """ Applies the cars rotation, and calculates the sensors xy-position in the car frame."""

        for (sensorKeyName,sensor) in self.ds.items():
            # First rotate the position of the sensor. p0
            # Second rotate the measured distance
            # add position p0 to measured distance rotated, and we get p1

            
            # Note that this is note done yet, since we need to rotate with both x and y.
            #sensorPosY_mapFrame = math.cos(self.yaw+sensor.yaw/180.0*math.pi)*float(sensor.position.x)
            #sensorPosX_mapFrame = math.sin(self.yaw+sensor.yaw/180.0*math.pi)*float(sensor.position.y)
            p = self.xyCarFramePointToMapFrameVector(sensor.placement)
            sensorPosY_mapFrame = p.y
            sensorPosX_mapFrame = p.x

        
            sensorHitY_sensorFrame = math.cos(self.yaw+sensor.placement.yaw+ 3.141592/2)*float(sensor.l)
            sensorHitX_sensorFrame = math.sin(self.yaw+sensor.placement.yaw+ 3.141592/2)*float(sensor.l)


            sensorHitY_mapFrameVector = sensorHitY_sensorFrame - sensorPosY_mapFrame
            sensorHitX_mapFrameVector = sensorHitX_sensorFrame + sensorPosX_mapFrame

            self.dsLines_carFrame[sensorKeyName] = [(self.x+sensorPosX_mapFrame,self.y+sensorPosY_mapFrame),(sensorHitX_mapFrameVector+self.x, self.y-sensorHitY_mapFrameVector)]
    def xyCarFramePointToMapFrameVector(self, point):
        y = (-math.cos(self.yaw + 3.141592/2) * point.x + math.sin(self.yaw+ 3.141592/2) * point.y)
        x = -((-math.sin(self.yaw + 3.141592/2) * point.x - math.cos(self.yaw + 3.141592/2) * point.y))
        #print "yaw=%s" % self.yaw
        #print "sx=%s sy=%s" % (x,y)
        p = Point(x,y,0)
        return p;
         
    def distance_e(self):
        # Estimate What we expect the distance measurements to see
        pass
    
            

if __name__ == '__main__':
    pass