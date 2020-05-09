import paho.mqtt.client as mqtt
import json
import os
#lib_path = os.path.abspath(os.path.join('..', '..', '..', 'lib'))
#configPath = os.path.abspath(os.path.join('..', 'configuration'))
#import sys
#sys.path.append(configPath) 

#import messageBrokerConfig as broker
class MqttSubscriber:

    messageSeperator =  b'\n\n\n*'
    def __init__(self, host, username, password, subscribeToQueue,  port):
        self.client = ""
        self.rawCallbacks = []
        self.decodedCallbacks = []
        self.successfullDecode = 0
        self.failedDecode = 0
        
        self.host=host
        self.username=username
        self.password=password
        self.subscribeToQueue = subscribeToQueue
        self.port = port
        

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):

        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(self.subscribeToQueue)

    def subscribeRaw(self, callback):
        self.rawCallbacks.append(callback)
        """ A raw subscription returns the raw message """
        pass

    def subscribeDecoded(self, callback):
        self.decodedCallbacks.append(callback)

        """ A decoded subscription return the decoded message """
        pass
        

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        for fn in self.rawCallbacks:
            fn(client,userdata, msg)

        #print(msg.topic+" "+str(msg.payload))
        messages = msg.payload.split(self.messageSeperator)
        #print ("*********** Number of messages = %d " % len(messages))
        for m in messages:
            if len(m.strip()) < 2:
                continue
            #print(m.strip())
            #print(dir(msg.payload))
            #print (msg.payload)
            #print ("DECODING DATA")
            try:
                data = m.decode('utf-8')
            except:
                print("Could not decode message")
            #print ("*****DATA DECODED")
            #print (data.strip())
            #decodedMessage = json.loads(data.strip())
            try:
                decodedMessage = json.loads(data.strip())
                # Here I will need an adapter.
                self.successfullDecode += 1
                for fn in self.decodedCallbacks:
                    fn(msg.topic, decodedMessage)
                #print "Message Succeeded"
            except:
                try:
                    print("FAILED:%s" % data.strip())
                except:
                    pass
                self.failedDecode += 1
                #print("*********** MESSAGE FAILED **************")
                
    def _createClientAndConnect(self):
        import paho.mqtt.client as mqtt
        self.client = mqtt.Client() # Note that this is not abstracted, since
                                # an abstraction here only make the code harder to read.
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.host, self.port, 60)

    def startAndLoopForever(self):
        self._createClientAndConnect()

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.client.loop_forever()
        
    def loop_start(self):
        self._createClientAndConnect()
        # Non-Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        self.client.loop_start()
    

    def printSucessfullAndFailedDecoding(self, client, userdata, msg):
        "the client and userdata is there to be able to use function as callback."
        print ("JSON decode successrate (%d/%d) " % (self.successfullDecode, self.successfullDecode+ self.failedDecode))

    def printDecodedMessages(self, topic,decodedMessage):
        "the client and userdata is there to be able to use function as callback."
        print ("%s wrote JSON: %s " % (topic, json.dumps(decodedMessage)))          

if __name__ == '__main__':
    lib_path = os.path.abspath(os.path.join('..', '..', '..', 'lib'))
    configPath = os.path.abspath(os.path.join('..', 'configuration'))
    import sys
    sys.path.append(configPath) 

    import messageBrokerConfig as broker
    
    #mqttReader = MqttSubscriber()  # note broker.msgSubscriber can be mqttReader.
    broker.msgSubscriber.subscribeRaw(broker.msgSubscriber.printSucessfullAndFailedDecoding)
    broker.msgSubscriber.subscribeDecoded(broker.msgSubscriber.printDecodedMessages)
    broker.msgSubscriber.startAndLoopForever()
