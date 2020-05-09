import signal
import time
import sqlite3
import time
import datetime
import sys
import traceback
import queue
import threading
import json

import sys
import os
configPath = os.path.abspath(os.path.join('..', 'configuration'))
sys.path.append(configPath) 
utilitiesPath = os.path.abspath(os.path.join('..', 'utilities'))
sys.path.append(utilitiesPath) 
import messageBrokerConfig as broker


class MqttDatapump:

    def __init__(self, msgSubscriber = broker.msgSubscriber):        
        # Enable killing from another window
        # kill -s SIGINT pid
        # get pid for instance by using
        # ps -ef |grep python
        self.msgSubscriber = msgSubscriber
        self.q = queue.Queue()        
        #signal.signal(signal.SIGINT, self.signal_handler) # Ctrl-C signal 2
        #signal.signal(signal.SIGQUIT, self.signal_handler)
        
    def printSucessfullAndFailedDecoding(self, client, userdata, msg):
        "the client and userdata is there to be able to use function as callback."
        print ("Successrate (%d/%d) " % (self.successfullDecode, self.successfullDecode+ self.failedDecode))  

    def startDatapump(self):
        print ("Starting datapump")
        #self.msgSubscriber.subscribeRaw(broker.msgSubscriber.printSucessfullAndFailedDecoding)
        self.msgSubscriber.subscribeDecoded(self.on_message)        
        self.msgSubscriber.loop_start() 
        #self.msgSubscriber.startAndLoopForever()

    # create a function which is called on incoming messages
    def on_message(self, topic,decodedMessage):
    
        decodedMessage['topic'] = topic
        self.q.put(decodedMessage)
        #print ("Queue size: %d" % self.q.qsize())
        
    def getData(self):
        while self.q.qsize() <= 0:
          print('No data')
        
        response = self.q.get()
        self.q.task_done()
        return response
        
    def getDataLength(self):
        return self.q.qsize()

        
    
if __name__ == '__main__':
    datapump = MqttDatapump()
    datapump.startDatapump()
    pass

