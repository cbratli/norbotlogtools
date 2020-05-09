
username = "norbot"
password = "Pass4norbot"


robotOutputQueue = "norbot/folkrace/#"

robotOutputQueue = "norbot/folkrace/rimfakse/out"
robotInputQueue = "norbot/folkrace/rimfakse/in"

#robotInputQueue = "norbot/folkrace/cyborgproto/in"
#robotOutputQueue = "norbot/folkrace/cyborgproto/out"

#robotInputQueue = "norbot/folkrace/diffbot/in"
#robotOutputQueue = "norbot/folkrace/diffbot/out"


host = "localhost"
port = 1883


#cars[robotOutputQueue] = Car(0,0,0)



# We encourge all norbot robots to use this base queue.
# Then we can for instance have one logger that lags all robots in one log file,
# and we can for instance plot all cars on the same map. (currently we have some 
# problems with compass direction and location)
#baseQueue = "norbot/cyborgProto/"

import os
configPath = os.path.abspath(os.path.join('..', 'utilities'))
import sys
sys.path.append(configPath)
import mqttSubscriber
msgSubscriber = mqttSubscriber.MqttSubscriber(host=host, username=username, password=password, subscribeToQueue = robotOutputQueue, port = port)
import mqttPublisher
msgPublisher = mqttPublisher.MqttPublisher(host=host, username=username, password=password, publishToQueue = robotInputQueue, port = port)




# xCenter = 20.0*1;
# ds[self.LEFT_1] = ReplayDistanceSensor(xCenter+2,5,7.75,-15.0/180.0*math.pi,0)
# ds[self.LEFT_2] = ReplayDistanceSensor(xCenter+10,21.26,0,-45.0/180.0*math.pi,0)
# ds[self.LEFT_3] = ReplayDistanceSensor(xCenter+23.3,29,0,-70.0/180.0*math.pi,0)
# ds[self.RIGHT_1] = ReplayDistanceSensor(xCenter+2,-7.75,0,15.0/180.0*math.pi,0)
# ds[self.RIGHT_2] = ReplayDistanceSensor(xCenter+10,-21.26,0,45.0/180.0*math.pi,0)
# ds[self.RIGHT_3] = ReplayDistanceSensor(xCenter+23.3,-29,0,70.0/180.0*math.pi,0)
