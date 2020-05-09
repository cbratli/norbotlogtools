from OrientedPoint import *
from Point import *
import math
class DistanceSensor(object):
    """
        The distance sensor is an abstract class, it does not know how to
        take a measurement
    """
    
    def __init__(self, x,y,z,yaw_rad, pitch_rad):
        """
            % This model use a right hand coordinate system with z pointing upwards.
            x - [mm] The x position relative to center of gravity
            y - [mm] The y-position relative to center of gravity
            z - [mm] The z-position on the object it is located on.
            yaw_rad [rad] - The yaw angle relative to the object it is mounted on.
            pitch_rad [rad]- The pitch angle of the sensor. Not used yet.
        """

        self.placement = OrientedPoint(x,y,z,yaw_rad,pitch_rad)
        self.xy = Point()   # The xy component of measurement l. 
        self.l = 0          # The distance measurement
        
    def takeMeasurement(self):
        """Fetch the next measurement """
        raise Exception('DistanceSensor does not know how to takeMeasurement')

    def setMeasurementAndCalculteXyzComponents(self,l):
            self.xy.y = math.cos(float(self.placement.yaw)/180.0*math.pi)*float(l)
            self.xy.x = math.sin(float(self.placement.yaw)/180.0*math.pi)*float(l)
            self.l = l


    def __str__(self):
        return "DistanceSensor placement(%s,%s,%s), yaw = %s, pitch = %s, roll = %s - Measurement l=%s x=%s y=%s" % (self.placement.x,self.placement.y, self.placement.z, self.placement.yaw, self.placement.pitch, self.placement.roll,self.l, self.xy.x, self.xy.y)
        
