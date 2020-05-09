class Point(object):
    """
        a three dimensional point
    """
    
    x = 0
    y = 0
    z = 0

    def __init__(self, x=0,y=0,z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
        return "Point(%s,%s,%s)"%(self.x,self.y, self.z)
