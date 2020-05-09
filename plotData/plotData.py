import sys
import os

configPath = os.path.abspath(os.path.join('..', 'configuration'))
sys.path.append(configPath) 
configPath = os.path.abspath(os.path.join('..', 'mqttLogger'))
sys.path.append(configPath) 
import sqlite3
import time
import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



import time
import dataloaderSqlite3MqttMessage as dataloaderSqlite3
import paho.mqtt.client as mqtt
import json
import getopt
import MessageTypeMqtt as MessageType

#utilitiesPath = os.path.abspath(os.path.join('..', 'utilities'))
#sys.path.append(utilitiesPath) 

import messageBrokerConfig as broker


class PlotData:
    messageSeperator =  b'\n\n\n*'
    def __init__(self, argv, msgSubscriber = broker.msgSubscriber):  
        self.broker = broker
        
        logFilename = argv[0]
        print(logFilename)
        dataload = dataloaderSqlite3.Dataloader(logFilename)
            
            
        print('Data records available: %d' % dataload.getDataLength() )
        dataArray = {}
        jsonTextUtf8 = ""
        for i in range(1,dataload.getDataLength()):
            data = dataload.getData()
            msg = data['message']
                
            messages = msg.split(self.messageSeperator)
            #print ("*********** Number of messages = %d " % len(messages))
            for jsonText in messages:
                if len(jsonText.strip()) < 2:
                    continue
                #print(m.strip())
                #print(dir(msg.payload))
                #print (msg.payload)
                #print ("DECODING DATA")
            
                #json.dumps(data['message'])
                try:
                    jsonTextUtf8 = jsonText.decode('utf-8')
                except:
                    print("Could not decode message")
                #print ("*****DATA DECODED")
                #print (data.strip())
                #decodedMessage = json.loads(data.strip())
                #print(jsonTextUtf8)
                try:
                    decodedMessage = json.loads(jsonTextUtf8.strip())
                    # Adda all values to array
                    for (k,v) in decodedMessage.items():
                        if k not in dataArray:
                            dataArray[k] = []
                            print(k)
                        dataArray[k].append(v)
                            
                except:
                    print("Error")
                    pass
            
            #(rc, mid) = client.publish(data['msgToTopic'],jsonText, qos=1)
            #(rc, mid) = client.publish('CyborgProtoOut',jsonText, qos=1)
            
        
        
        graphArray = []

        

        
                
        fig = plt.figure()

        ax1 = fig.add_subplot(2,1,1, axisbg='white')
        ax1.plot(dataArray["t_ms"], dataArray["theta_w_deg"], 'c', linewidth=3.3)
        #ax1.plot(dataArray["t_ms"], left2_mm, 'm', linewidth=3.3)
        ax1.set_title('wheelAngle(cyan) left2_mm(magenta)', color = 'c')
        ax1.set_xlabel('Time [s]')
        ax1.set_ylabel('Wheel angle [deg]')

        ax2 = fig.add_subplot(2,1,2, axisbg='white',sharex=ax1)
        ax2.plot(dataArray["t_ms"], dataArray["theta_w_deg"], 'c', linewidth=3.3)
        #ax2.set_title('Weight', color = 'c')
        ax2.set_xlabel('Time [s]')
        ax2.set_ylabel('theta [deg]')
        rect = fig.patch

       

        #



       

        

        

        

        plt.show()


if __name__ == '__main__':
    logPlayback = PlotData(sys.argv[1:])
    #logPlayback.sendLog('rodlog.db')
