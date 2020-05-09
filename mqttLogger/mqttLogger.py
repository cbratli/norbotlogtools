import signal
import time
import sqlite3
import time
import datetime
import sys
import traceback
import queue
import threading
import MessageTypeMqtt as MessageType


import sys
import os
configPath = os.path.abspath(os.path.join('..', 'configuration'))
sys.path.append(configPath) 
#utilitiesPath = os.path.abspath(os.path.join('..', 'utilities'))
#sys.path.append(utilitiesPath) 
import messageBrokerConfig as broker

class MqttLogger:

    def __init__(self, msgSubscriber = broker.msgSubscriber):        
        self.messageRepository = MessageType.MessageTypeMqtt()
        # Enable killing from another window
        # kill -s SIGINT pid
        # get pid for instance by using
        # ps -ef |grep python
        self.msgSubscriber = msgSubscriber
        
        #signal.signal(signal.SIGINT, self.signal_handler) # Ctrl-C signal 2
        #signal.signal(signal.SIGQUIT, self.signal_handler)
        
    def printSucessfullAndFailedDecoding(self, client, userdata, msg):
        "the client and userdata is there to be able to use function as callback."
        print ("Successrate (%d/%d) " % (self.successfullDecode, self.successfullDecode+ self.failedDecode))  


    def input_handler(self, arg1, stop_event):
        import time
        import pygame
        pygame.init()
        while not self.stop_event.is_set():
            time.sleep(.1)
            for event in pygame.event.get(): # event handling loop
                print(event.type)
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.stop_event.set()
                    pygame.quit()
                    time.sleep(3)
                    import sys
                    sys.exit(0)
                    

            
            
    
    def signal_handler(self,signal,frame):
        print('Exiting gently....')
        self.stop_event.set()

    def startLogServer(self):
        print("Starting log server...")
        self.q = queue.Queue()
        self.stop_event = threading.Event()
        
        self.t = threading.Thread(target=self.dbLoggingThread, args=('',self.stop_event))
        self.t.setDaemon(True)
        self.t.start()
        
        self.t2 = threading.Thread(target=self.input_handler, args=('',self.stop_event))
        self.t2.setDaemon(True)
        self.t2.start()
        
        
        #self.msgSubscriber.subscribeRaw(broker.msgSubscriber.printSucessfullAndFailedDecoding)
        self.msgSubscriber.subscribeRaw(broker.msgSubscriber.printSucessfullAndFailedDecoding)
        self.msgSubscriber.subscribeRaw(self.on_message)
        
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        #self.msgSubscriber.startAndLoopForever()
        self.msgSubscriber.loop_start()
        while (not self.stop_event.is_set()):
            pass
        time.sleep(1)
        
    def on_message(self,client, userdata, msg):
        self.q.put([msg.topic, msg.payload])            
        #print("Data:%s" % (msg.payload))
    
    def dbLoggingThread(self, arg1 ,stop_event):
        """ This is the main loop. it loops forever"""
        print("Connecting to database....")
        self.conn = sqlite3.connect('rodlog.db')
        print("Connected to database")

        cursor = self.conn.cursor()
        self.messageRepository.initialize(self.conn,cursor)
        
        while (not self.stop_event.is_set()):
           
            try:
                if self.q.qsize() >= 100:
                    print("qsize= %i" % (self.q.qsize()))
                messages = []
                while self.q.qsize() >= 1:
                    if self.stop_event.is_set():
                        print("***************")
                    else:
                        print("OK")
                    response = self.q.get()
                    #print(response.strip())
                    messages.append(response)
                    self.q.task_done()
                self.logMessage(messages, cursor)
            except Exception as e:
                print ("Exception while writing to db." + str(e))
        self.closeConnection()
        print("Connection closed")
        pass
    def closeConnection(self):
        self.conn.close()
        self.conn.close()


    def logMessage(self, messages, cursor):
        """ This function splits and logs the message """
        
        message1Tupples = []                                    
        
        if len(messages) > 0:
            print ("-Writing %d messages" % len(messages) )
        for message in messages:
            try:
                self.messageRepository.saveMessage(message)
            except:
                print ("Unexpected error:", sys.exc_info()[0])
                tb = traceback.format_exc()
                print(tb)
                pass

        # Write the messageTupples To Disk
            self.messageRepository.writeRecordsToDatabase(self.conn, cursor);
        
    
if __name__ == '__main__':
    autoLog = MqttLogger()
    autoLog.startLogServer()
    pass

