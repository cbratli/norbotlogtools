from Point import *
class OrientedPoint(Point):
    """
        a three dimensional point
    """
    

    def __init__(self, x=0,y=0,z=0, yaw=0, pitch = 0, roll = 0):
        self.yaw = float(yaw)
        self.pitch = float(pitch)
        self.roll = float(roll)
        Point.__init__(self, x, y,z)
        
    def __str__(self):
        return "OritentedPoint(%s,%s,%s), yaw = %s, pitch = %s, roll = %s"%(self.x,self.y, self.z, self.yaw, self.pitch, self.roll)
