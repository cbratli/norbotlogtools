import numpy as np
import math
from Point import *

class SimpleSlam(object):
    """
        This is a first version of a slam algorithm I have been thinking of.
        Trying a simple solution first before going to more advanced solutions.

        The slam algorithm currently knows of all sensors on the car.
        (Could be given the sensors it should use.)

        The algorithm can be outlined as follows:
        1. Gather the "foundMap" by using the sensors pointing at 70 degrees.
        - Dont compensate, use the simulation model when gathering, so we get the built-in model error onto the map.
        - IF the current model can not be run in open-loop, see if we can imrove the model.
        - While gathering the map, draw lines between the points, so the track gets "closed"

        2. While gathering the map, try to use the soft sensors (estimates). If they see walls that corresponds
            to measurements
                a. Compensate for errors.
                b. stop map gathering, if we have softsensors for a long period (or the track is closed.)


        3. If map gathering is stopped. We are in location mode.
            a) We need to verify that we have the right yaw.
            b) We need to compensate for errors.
            c) We need an estimate of variance of correct position.
                - This increases with excessive speeds.
                - If the vehicle roll gets larger than a threshold
                - If the vehicles pitch gets larger than a big threshold.
                - ?? If all sensors cant see anything. ?? Problem in big rooms.
                Currently the location method is not known.

    """

    def __init__(self, car):
        """
            
        """
        self.mapDone = False   # When the map has been created, the mapDone variable will be true.
        self.autoScale = True  # Autoscale is slow.
        self.scale = 1  # 0.1 means Car is in mm, map is in cm.
        self.car = car
        self.mapWidth = 1000
        self.mapHeight = 1000
        
        self.foundMap = np.zeros([self.mapWidth,self.mapHeight,3], np.uint8)

        self.prevPointLeft = (0,0)
        self.prevPointRight = (0,0)
        self.iterationCounter = 0
        self.prevYaw = None
        self.yawDiff = 0

        self.castedRay = {}
        self.rightSensorNames = []
        self.leftSensorNames = []
        
        self.leftPoints = []
        self.rightPoints = []
        self.midlePoints = []   # The points in the midle.
        self.addMidlePoints = True  # The first round, we add midlepoints.
        
        self.biasX = 0
        self.biasY = 0
        
        self.maxX = 0
        self.minX = self.mapWidth
        self.maxY = 0
        self.minY = self.mapHeight
        

        # fill the edges of the map.
        for i in range(1,1000):
            self.foundMap[i,0,1] = int(255.0*0.5)
            self.foundMap[i,self.mapHeight-1,2] = int(255.0*0.5)
            self.foundMap[self.mapWidth-1,i,1] = int(255.0*0.5)
            self.foundMap[0,i,1] = int(255.0*0.5)

    def getAngleBetween0And2pi(self,angle):
        numberOf2Pis = math.floor(float(angle)/(2.0*math.pi))
        angle = angle-2.0*math.pi*numberOf2Pis
        return angle
   
    def packData(self):
        data = {}
        data["LEFT"] = self.leftPoints
        data["RIGHT"] = self.rightPoints
        data["SCALE"] = self.scale
        data["MIDLEPOINTS"] = self.midlePoints
        data["BIAS"] = (self.biasX, self.biasY)
        
        return data
    
    def unpackData(self,data):
        self.autoScale = False  # since we dont save max/min values.
        self.leftPoints = data["LEFT"]
        self.rightPoints = data["RIGHT"]
        self.scale = data["SCALE"]
        self.midlePoints = data["MIDLEPOINTS"]
        (biasX, biasY) = data["BIAS"]
        
        # We need to move the car to the bias posisiton, so add missing bias.
        self.car.x += biasX-self.biasX
        self.car.y += biasY-self.biasY
        self.biasX = biasX
        self.biasY = biasY
        
        
    def saveMap(self):
        import pickle
        
        data = self.packData()
        
        with open('map.pickle', 'wb') as f:
            pickle.dump(data, f)
        
    def loadMap(self,filename):
        import pickle
        with open('map.pickle', 'rb') as f:
            data = pickle.load(f)
            self.unpackData(data)
        self.mapDone = True # To disable mapping
        
        self.redrawMap()
     
    def setMidlePointPosition(self,index,newPosition):
        self.midlePoints[index] = newPosition
        self.redrawMap()
     
    def getMidlePointClosestToMapScreenPosition(self,pos):
        index = -1
        minDist = 100000    # Large dummyvalue
        for i in range(len(self.midlePoints)):
            dist = self.getDistance(self.getMapPosFromScreenPos(pos), self.midlePoints[i])
            if minDist > dist:
                minDist = dist
                index = i
                print ("%d - minDist=%.0f", (i, minDist))
        return index        

    def removeMidlePoint(self, selectedMidlePoint):
        self.midlePoints.pop(selectedMidlePoint)
        self.redrawMap()
    
        
    def getDistance(self,pos1,pos2):
        """ pos1 and pos2 are tubles with (x,y)"""
        dX = float(pos1[0]-pos2[0])
        dY = float(pos1[1]-pos2[1])

        dist = math.ceil(math.sqrt(dX*dX+dY*dY))
        return dist
            
    def getMapPosFromScreenPos(self,pos):
        # Returns the map position given the screen position
        # Inputs pos, a tuple with 2 elements (x,y)
        return (pos[0]/self.scale, pos[1]/self.scale)
    

    def castSingleRay(self,yaw, maxLength):
        """ Return a ray hit coordinate for the foundMap
            yaw - The angle of the sensor.
            (We also need sensor placment)
        """
        #print ("yaw %s" % yaw)
	
        rayAngle = self.getAngleBetween0And2pi(yaw)
        #print ("rayAngle %s" % rayAngle)
        #// moving right/left? up/down? Determined by which quadrant the angle is in.
        right = (rayAngle > 2.0*math.pi * 0.75 or rayAngle < 2.0*math.pi * 0.25)
        up = (rayAngle < 0 or rayAngle > math.pi);

        #// only do these once
        angleSin = math.sin(rayAngle);
        angleCos = math.cos(rayAngle);

	
        dist = 1500000000;	#// the distance to the block we hit. Dummy value < 0
        xHit = 8000; 	#// the x and y coord of where the ray hit the block
        yHit = 8000;

##	// first check against the vertical map/wall lines
##	// we do this by moving to the right or left edge of the block we're standing in
##	// and then moving in 1 map unit steps horizontally. The amount we have to move vertically
##	// is determined by the slope of the ray, which is simply defined as sin(angle) / cos(angle).
##
        slope = angleSin / angleCos 	##// the slope of the straight line made by the ray
        if right:
            dX = 1.0
        else:
            dX = -1.0
        dY = dX * slope; 		#// how much to move up or down


            #// starting horizontal position, at one of the edges of the current map block
        if right:
            x = math.ceil(self.carX_mapScale())
        else:
            x = math.floor(self.carX_mapScale())
        
        y = self.carY_mapScale() + (x - self.carX_mapScale()) * slope;			##// starting vertical position. We add the small horizontal step we just made, multiplied by the slope.
            #print ("y: %.2f" % y)
            #print ("y_mapScale: %.2f" % self.carY_mapScale())
            #print ("y_car: %.2f" % self.car.y)
            
            # We only need to check with the resolution of the map
        while (x >= 0 and x < self.mapWidth and y >= 0 and y < self.mapHeight):
            #wallX = math.floor(x + (right ? 0 : -1));
            wallX = math.floor(x);
            if right == False:
                wallX = wallX - 1
            wallY = math.floor(y);

            #is this point inside a wall block?

            #distX = (x - self.carX_mapScale())/self.scale;
            #distY = (y - self.carY_mapScale())/self.scale;
            #distMaxCheck = math.sqrt(distX*distX + distY*distY);	#// the distance from the player to this point, squared.
            #if distMaxCheck > maxLength:
            #    dist = maxLength*maxLength
            #    break    
            
            terrainHeight = self.foundMap[wallX,wallY,0]+self.foundMap[wallX,wallY,1]
            if ( terrainHeight > 0):
                
                distX = (x - self.carX_mapScale())/self.scale;
                distY = (y - self.carY_mapScale())/self.scale;
                dist = distX*distX + distY*distY;	# the distance from the player to this point, squared.

                xHit = x;	#// save the coordinates of the hit. We only really use these to draw the rays on minimap.
                yHit = y;

                #print ("Halfways: xHit=%d yHit=%d" % (xHit, yHit))
                break;
                
            
            x += dX;
            y += dY;


    ##	// now check against horizontal lines. It's basically the same, just "turned around".
    ##	// the only difference here is that once we hit a map block, 
    ##	// we check if there we also found one in the earlier, vertical run. We'll know that if dist != 0.
    ##	// If so, we only register this hit if this distance is smaller.
    ##
        slope = angleCos / angleSin;
        if up:
            dY = -1.0
            y = math.floor(self.carY_mapScale())
        else:
            dY = 1.0
            y = math.ceil(self.carY_mapScale())
        dX = dY * slope;
        
        x = self.carX_mapScale() + (y - self.carY_mapScale()) * slope;
    ##
        while (x >= 0 and x < self.mapWidth and y >= 0 and y < self.mapHeight):

            #wallY = Math.floor(y + (up ? -1 : 0));
            wallY = math.floor(y)
            if up:
                wallY = wallY - 1.0
            
            wallX = math.floor(x);
            terrainHeight = self.foundMap[wallX, wallY,0] + self.foundMap[wallX, wallY,1]
            if (terrainHeight > 0):	
                #var notMySelf = terrainHeight & car.carId;	
                distX = (x - self.carX_mapScale())/self.scale
                distY = (y - self.carY_mapScale())/self.scale
                blockDist = distX*distX + distY*distY

                # If this direction is shorter, then use that.
                if (dist<=0 or blockDist < dist):
                    dist = blockDist;
                    xHit = x;
                    yHit = y;
        
                break
                
            #distX =( x - self.carX_mapScale())/self.scale;
            #distY = (y - self.carY_mapScale())/self.scale;
            #distMaxCheck = distX*distX + distY*distY;	#// the distance from the player to this point, squared.
            #if distMaxCheck > maxLength*maxLength:
            #    dist = maxLength*maxLength
            #    break    
        
            x += dX;
            y += dY;

        xHitSensor = xHit
        yHitSensor = yHit
        #print ("xHitSensor %d, yHitSenor %d" % (xHit, yHit))

        dist_mm = math.sqrt(dist);
        #print ("Done: xHitSensor=%d yHitSensor=%d" % (xHit, yHit))
        return 	(dist_mm, xHitSensor, yHitSensor)


    def carY_mapScale(self):
        return self.car.y*self.scale    # convert from mm to cm

    def carX_mapScale(self):
        return self.car.x*self.scale
    
    def iterate(self):
        """Fetch the next measurement """
        self.iterationCounter = self.iterationCounter + 1
        self.addSensorDataToMap()
        self.calculateTotalYawDiff(self.car.yaw)
        yaw = 15.0/180.0*math.pi
        maxLength = 15000
        #(dist, distX, distY) = self.castSingleRay(yaw+self.car.yaw, maxLength)
        #self.midlePoints.append(self.car.getMidlePoint())
        

    def __str__(self):
        return "SimpleSlam"


    def plotPoint(self,x,y,r,g,b):
            x = x*self.scale
            y = y*self.scale
            if x > 0 and x < self.foundMap.shape[0] and y > 0 and y < self.foundMap.shape[1]: 
                self.foundMap[x,y,0] = int(255*r)
                self.foundMap[x,y,1] = int(255*g)
                self.foundMap[x,y,2] = int(255*b)

    def plotLine(self,l,r,g,b):
        p0 = l[0]
        p1 = l[1]
        dX = float(p1[0]-p0[0])
        dY = float(p1[1]-p0[1])

        dist = math.ceil(math.sqrt(dX*dX+dY*dY))

        if dist > 0:
            addX = dX/dist
            addY = dY/dist
        else:
            addX = dX
            addY = dY

            
        distX = 0
        distY = 0
        
        p0 = l[0]
        p1 = l[1]
        p0_0 = p0[0]
        p0_1 = p0[1]
        p1_0 = p1[0]
        p1_1 = p1[1]
        self.plotPoint(p0_0,p0_1,r,g,b)
        self.plotPoint(p1_0,p1_1,r,g,b)
        for i in range(1,int(dist)):
            distX = distX+addX
            distY = distY+addY
            self.plotPoint(p0_0+math.floor(distX),p0_1+math.floor(distY),r,g,b)

        

        # Now fill points for every line.

    def plotPointFromLine(self,l,r,g,b):
        p0 = l[0]
        p1 = l[1]
        p0_0 = p0[0]
        p0_1 = p0[1]
        p1_0 = p1[0]
        p1_1 = p1[1]
        self.plotPoint(p1_0,p1_1,r,g,b)
        
        
    def calculateTotalYawDiff(self,yaw):
        """Used to see when we have gone 360 degrees"""
        if self.prevYaw == None:
            self.prevYaw = self.car.yaw
        yawDiff = yaw - self.prevYaw
        
        # yaw went from zero to 360 or below.
        if yawDiff > math.pi:
            yawDiff = yaw - 2*math.pi - self.prevYaw
        
        # yaw went from 360 to zero.
        if yawDiff < -math.pi:
            yawDiff = yaw + 2*math.pi - self.prevYaw
        
        self.yawDiff += yawDiff
        self.prevYaw = self.car.yaw

    def addRightSensor(self, rightSensorName):
        self.rightSensorNames.append(rightSensorName)
        pass
    
    def addLeftSensor(self,leftSensorName):
        self.leftSensorNames.append(leftSensorName)
    
    
    def addBias(self,xBias, yBias):
    
            self.car.y += yBias
            self.minY += yBias
            self.maxY += yBias
            self.car.x += xBias
            self.minX += xBias
            self.maxX += xBias
            self.biasX += xBias
            self.biasY += yBias
        
            for i in range(len(self.midlePoints)):
                p1 = self.midlePoints[i]
                self.midlePoints[i] = (p1[0]+xBias, p1[1]+ yBias)
                
            for i in range(len(self.rightPoints)):
                p1 = self.rightPoints[i]
                self.rightPoints[i] = (p1[0]+xBias, p1[1]+ yBias)
            
            for i in range(len(self.leftPoints)):
                p1 = self.leftPoints[i]
                self.leftPoints[i] = (p1[0]+xBias, p1[1]+ yBias)
                
            
            for sensorName in self.car.dsLines_carFrame.keys():
                l = self.car.dsLines_carFrame[sensorName]
                p1 = l[1]
                l[1] = (p1[0]+xBias, p1[1]+yBias)
                self.car.dsLines_carFrame[sensorName] = l
    
    def checkScale(self):
        """ TODO: Also use bias """
        
        if self.minX*self.scale < 30:
            self.addBias(200,0)
            self.redrawMap()
        
        if self.minY*self.scale < 30:
            self.addBias(0,200)
            self.redrawMap()
        
        
        if self.maxX* self.scale > self.mapWidth:
            self.scale = self.scale/2
            print("Changeing scale to : %.3f", self.scale)
            self.redrawMap()
        if self.maxY*self.scale > self.mapHeight:
            self.scale = self.scale/2
            print("Changeing scale to : %.3f", self.scale)
            self.redrawMap()
            
        
        
    
    def updateMaxLimits(self,p1):
        if p1[0] > self.maxX:
            self.maxX = p1[0]
            self.checkScale()
        if p1[0] < self.minX:
            self.minX = p1[0]
            self.checkScale()

        if p1[1] > self.maxY:
            self.maxY = p1[1]
            self.checkScale()
        if p1[1] < self.minY:
            self.minY = p1[1]
            self.checkScale()
    
    def addRightPointIfDistanceIsOk(self,p1):
        if len(self.rightPoints) == 0:
            self.rightPoints.append(p1)
        
        dist = self.getDistance(self.rightPoints[-1],p1)
        if dist > 30:
            self.rightPoints.append(p1)
            self.updateMaxLimits(p1)

    def addLeftPointIfDistanceIsOk(self,p1):
        if len(self.leftPoints) == 0:
            self.leftPoints.append(p1)
       
        dist = self.getDistance(self.leftPoints[-1],p1)
        
        if dist > 30:
            self.leftPoints.append(p1)
            self.updateMaxLimits(p1)
            
        
        # If we have more than 50 points (30*20=600mm length), we may complete the map.
        # Use the 3'rd point, so we are 90 mm inside.
        if len(self.leftPoints) > 90:
            dist = self.getDistance(self.leftPoints[2],p1)
            if dist < 30 and self.mapDone == False:
                self.mapDone = True
                self.leftPoints.append(self.leftPoints[0])
                if len(self.rightPoints) > 1:
                    self.rightPoints.append(self.rightPoints[0])    # Also add rightPoints :-)


    def redrawMap(self):
        self.foundMap = np.zeros([self.mapWidth,self.mapHeight,3], np.uint8)
        if len(self.rightPoints) > 1:
            r = 0
            g = 1
            b = 0
            prevP = self.rightPoints[0]
            
            for p in self.rightPoints:
                self.plotLine( [prevP, p],r,g,b)
                prevP = p
            
        if len(self.leftPoints) > 1:
            r = 1
            g = 0
            b = 0
            prevP = self.leftPoints[0]
            for p in self.leftPoints:
                self.plotLine( [prevP, p],r,g,b)
                prevP = p
                
                
        if len(self.midlePoints) > 0:
            r = 1
            g = 0
            b = 0
            for p in self.midlePoints:
                self.plotPoint(p[0],p[1],0,0,1)
            
    def putLinesOntoMap(self):
        
        if len(self.rightPoints) > 1:
            r = 0
            g = 1
            b = 0
            prevP = self.rightPoints[-2]
            p = self.rightPoints[-1]
            self.plotLine( [prevP, p],r,g,b)
            #for p in self.rightPoints:
            #    self.plotLine( [prevP, p],r,g,b)
            #    prevP = p
            
        if len(self.leftPoints) > 1:
            r = 1
            g = 0
            b = 0
            prevP = self.leftPoints[-2]
            p = self.leftPoints[-1]
            self.plotLine( [prevP, p],r,g,b)


    def addSensorDataToMap(self):
        maxLength = 200000
        maxSensorValueToCount = 1400
        
        self.castedRay = {}
        for sensorName in self.rightSensorNames:
            #self.plotLine([(10,10),(10000,10000)],230,150,80)
            if self.car.ds[sensorName].l < maxSensorValueToCount:
                l=self.car.dsLines_carFrame[sensorName]
                r = 0
                g = 1
                b = 0
                if abs(self.yawDiff)*180/math.pi < 400 and self.mapDone == False:
                    if self.prevPointRight[1] > 0:
                        if self.autoScale:
                            self.addRightPointIfDistanceIsOk(l[1])
                        else:
                            self.plotLine( [(self.prevPointRight[0], self.prevPointRight[1]), l[1]],r,g,b)
                self.prevPointRight = l[1]
                # Cast a ray in the same direction as the measurement
                (dist,hitX,hitY) = self.car.slamAlgorithm.castSingleRay(self.car.yaw+self.car.ds[sensorName].placement.yaw, maxLength)
                self.castedRay[sensorName] = (dist, hitX,hitY)
                #self.plotPointFromLine(l,r,g,b)
            
        for sensorName in self.leftSensorNames:
            if self.car.ds[sensorName].l < maxSensorValueToCount:
                l = self.car.dsLines_carFrame[sensorName]
                r = 1
                g = 0
                b = 0
                if abs(self.yawDiff)*180/math.pi < 400 and self.mapDone == False:
                    if self.prevPointLeft[1] > 0:
                        if self.autoScale:
                            self.addLeftPointIfDistanceIsOk(l[1])
                        else:
                            self.plotLine( [(self.prevPointLeft[0], self.prevPointLeft[1]), l[1]],r,g,b)
                self.prevPointLeft = l[1]
                (dist,hitX,hitY) = self.car.slamAlgorithm.castSingleRay(self.car.yaw+self.car.ds[sensorName].placement.yaw, maxLength)
                self.castedRay[sensorName] = (dist, hitX,hitY)
                #self.plotPointFromLine(l,r,g,b)

        if self.rightSensorNames[0] in self.castedRay   and self.leftSensorNames[0] in self.castedRay:
            sensorName = self.rightSensorNames[0]
            (dist,hitX,hitY) = self.castedRay[sensorName]
            l_car_m = self.car.ds[sensorName].l
            diff_right = l_car_m - dist
            sensorName = self.leftSensorNames[0]
            (dist,hitX,hitY) = self.castedRay[sensorName]
            l_car_m = self.car.ds[sensorName].l
            diff_left = l_car_m - dist
             
            # To adjust, we need to have the same sign.
            if (diff_left > 0 and diff_right < 0) or (diff_left < 0 and diff_right > 0) and abs(self.yawDiff)*180/math.pi > 400:
                # If they are almost eqully off, then its a high probability that its a good measurement.
                #print("diff_left=%s  (abs(diff_left)-abs(diff_right))=%.1f" % (diff_left,abs(diff_left)-abs(diff_right)))
                if abs(diff_left)-abs(diff_right) < 300:
                    # Assuming both sensor have the same yaw (or oppsosite)
                    yaw = self.car.yaw + self.car.ds[sensorName].placement.yaw
                    
                    # Automatic correction.
                    self.car.x = self.car.x - math.cos(yaw) * diff_left*0.01
                    self.car.y = self.car.y - math.sin(yaw) * diff_left*0.01
                    #print("Correcting position: diff_left = %s, car.x = %.2f, car.y=%.2f        math.cos(yaw)= %.2f, math.sin(yaw)=%.2f" % (diff_left, self.car.x, self.car.y,math.cos(yaw), math.sin(yaw)))
                
                pass
            
            if diff_left < 0 and diff_right < 0:
                pass
        
        self._addMidPoint()
        
        
        self.putLinesOntoMap()
    
    def _addMidPoint(self):
     # Rules for adding a point.
        # 1. Distance from previous point is atleast 10 cm.
        # 2. When we have two points, the next point must be inside +-80 degrees from the line the two previous points are creating.
        # 3. When we have gone at least 250 degrees, we start to calculate the distance from the first point. If distance is less than 20 cm,
        #           we stop collecting points.
        # 4. In the future, it may be that we will
        
        if self.addMidlePoints == False:
            return
        
        lengthMidles = len(self.midlePoints)
        
        if len(self.midlePoints) == 0:
            self.midlePoints.append(self.car.midlePoint)
            print("ADDING FIRST POINT *************************")
        else:
                
            if abs(self.yawDiff)*180/math.pi > 250:
                
                prevPoint = self.midlePoints[0]
                dist = math.sqrt(math.pow(prevPoint[0] - self.car.midlePoint[0],2) + math.pow(prevPoint[1] - self.car.midlePoint[1],2))
                if dist < 300:
                    self.addMidlePoints = False
                    # Here we can do some postprocessing.

            # Only add point if it is more than XX cm from the previous point
            prevPoint = self.midlePoints[-1]
            dist = math.sqrt(math.pow(prevPoint[0] - self.car.midlePoint[0],2) + math.pow(prevPoint[1] - self.car.midlePoint[1],2))
            print("Dist midlePoint %d - x0:%d y0:%d -x1:%d y1:%d " % (dist, prevPoint[0], prevPoint[1], self.car.midlePoint[0], self.car.midlePoint[1]))
            if dist > 300:
                self.midlePoints.append(self.car.midlePoint)



        
        # Have we added a point?
        if lengthMidles < len(self.midlePoints):
            self.plotPoint(self.car.midlePoint[0],self.car.midlePoint[1],0,0,1)