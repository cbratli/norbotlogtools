import paho.mqtt.client as mqtt
import json
import os

class MqttPublisher:

    def __init__(self, host, username, password, publishToQueue,  port):
        self.client = ""        
        self.host=host
        self.username=username
        self.password=password
        self.publishToQueue = publishToQueue
        self.port = port
        self._createClientAndConnect()
        
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
                
    def _createClientAndConnect(self):
        import paho.mqtt.client as mqtt
        self.client = mqtt.Client() # Note that this is not abstracted, since
                                # an abstraction here only make the code harder to read.
        self.client.on_connect = self.on_connect
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.host, self.port, 60)
        
    
    def publishMessage(self, topic, data):
        self.client.publish(topic,data, qos=1)  
        self.client.loop()

if __name__ == '__main__':
    lib_path = os.path.abspath(os.path.join('..', '..', '..', 'lib'))
    configPath = os.path.abspath(os.path.join('..', 'configuration'))
    import sys
    sys.path.append(configPath) 

    import messageBrokerConfig as broker
    