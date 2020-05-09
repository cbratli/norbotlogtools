import paho.mqtt.client as mqtt
import json
import os
#lib_path = os.path.abspath(os.path.join('..', '..', '..', 'lib'))
configPath = os.path.abspath(os.path.join('..', 'configuration'))
import sys
sys.path.append(configPath) 

import messageBrokerConfig as broker 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(broker.robotOutputQueue)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    messages = msg.payload.split(b"\n\n\n*")
    for m in messages:
        if len(m.strip()) < 2:
            continue
        #print(m.strip())
        try:
            json.loads(m.strip())
            print("Message Succeeded")
        except:
            print("*********** MESSAGE FAILED **************")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(broker.username, broker.password)
client.connect(broker.host, broker.port, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
