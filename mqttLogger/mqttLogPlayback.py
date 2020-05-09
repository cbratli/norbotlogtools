
# The legacy log pusher, reads old log messasage dump files
# convert them to json, and push them via AMQP


# Read all data, as own dictionaries.
# create dictionary(object), and dump it to json.
# push the data via AMQP

import time
import dataloaderSqlite3MqttMessage as dataloaderSqlite3
import paho.mqtt.client as mqtt
import json
import sys
import os
import getopt
import MessageTypeMqtt as MessageType
configPath = os.path.abspath(os.path.join('..', 'configuration'))
sys.path.append(configPath) 

#utilitiesPath = os.path.abspath(os.path.join('..', 'utilities'))
#sys.path.append(utilitiesPath) 

import messageBrokerConfig as broker


class MqttLogPlayback:

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

    def __init__(self, argv, msgSubscriber = broker.msgSubscriber):  
        self.broker = broker
        self.messageRepository = MessageType.MessageTypeMqtt()
        # Enable killing from another window
        # kill -s SIGINT pid
        # get pid for instance by using
        # ps -ef |grep python
        self.msgSubscriber = msgSubscriber
        ip = '127.0.0.1'
    
        self.filename = None
        self.printUsage()
        print (argv)
        try:
            opts, args = getopt.getopt(argv,"f",["filename="])
            #opts, args = getopt.getopt(argv,"f:h:p:d:l",["filename=","host=","port=", "directory="])
        except getopt.GetoptError:
            self.printUsage()
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-p', '--port'):
                port = arg
            elif opt in ("-h", "--host"):
                ip = arg
            elif opt in ("-f", "--filename"):
                self.filename = arg
                print("FOUND FILENAME :%s" % self.filename)
            elif opt in ("-d", "--directory"):
                directory = arg
            elif opt in ("-l"):
                loopData = True

        if self.filename == None:
            self.printUsage()
            print("Program needs a filename....")
            import sys
            sys.exit(1)
            
        self.sendLog(self.filename)
            
    def printUsage(self):
        print ("Usage:")
        print ("mqttLogPlayback [-f filename] [-h hostIp] [-p portNumber] ")
        print ("or")
        print ("mqttLogPlayback --filenme filename")
        print ("Example:")
        print ("%s --filename rodlog.db" % sys.argv[0])
        
        

    def sendLog(self,logFilename):
        print("Opening database file: %s" % logFilename)
        client = mqtt.Client()
        client.on_connect = self.on_connect
        #client.on_message = on_message
        client.username_pw_set(broker.username, broker.password)
        client.connect(broker.host, broker.port, 60)
        client.loop_start()
        # send a message


        dataload = dataloaderSqlite3.Dataloader(logFilename)
        
	    
        print('Data records available: %d' % dataload.getDataLength() )
        for i in range(1,dataload.getDataLength()):
            data = dataload.getData()
                        
            jsonText = data['message'] #json.dumps(data['message'])
            time.sleep(0.042)  # For now, we use sleep.
            (rc, mid) = client.publish(data['msgToTopic'],jsonText, qos=1)
            #(rc, mid) = client.publish('CyborgProtoOut',jsonText, qos=1)
            

if __name__ == '__main__':
    logPlayback = MqttLogPlayback(sys.argv[1:])
    #logPlayback.sendLog('rodlog.db')

