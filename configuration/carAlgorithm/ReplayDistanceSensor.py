
from DistanceSensor import *

class ReplayDistanceSensor(DistanceSensor):
    """
        The replay distance sensor can measure distance in one direction.
        the sensor data is based on log data.
    """
    sleepIfSensorLoop = False

    def __init__(self, x,y,z, yaw, pitch):
        """
            % This model use a right hand coordinate system with z pointing upwards.
            x - The x position relative to center of gravity
            y - The y-position relative to center of gravity
            z - The z-position on the object it is located on.
            yaw - [rad] The angle relative to the object it is mounted on.
            pitch - [rad] The pitch angle of the sensor.
        """
        DistanceSensor.__init__(self, x, y,z, yaw, pitch)
        self.measurements = []
        self.datasetCounter = 0

    def addDataSetList(self, data):
        self.measurements.extend(data)

    def insertNewMeasurement(self, newMeasurement):
        self.measurements.append(newMeasurement)

    def loopMeasurements(self,trueFalse):
        self.sleepIfSensorLoop = trueFalse

    def takeMeasurement(self):
        """Fetch the next measurement """
        if self.sleepIfSensorLoop == True and len(self.measurements)+1 <= self.datasetCounter:
               time.sleep(2)
        self.datasetCounter = (self.datasetCounter + 1) % len(self.measurements)
        l = self.measurements[self.datasetCounter]
        self.setMeasurementAndCalculteXyzComponents(l)

    def __str__(self):
        return "ReplayDistanceSensor placement(%s,%s,%s), yaw = %s, pitch = %s, roll = %s - Measurement l=%s x=%s y=%s"%(self.placement.x,self.placement.y, self.placement.z, self.placement.yaw, self.placement.pitch, self.placement.roll,self.l, self.xy.x, self.xy.y )
