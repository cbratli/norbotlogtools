import paho.mqtt.client as mqtt
import json
#lib_path = os.path.abspath(os.path.join('..', '..', '..', 'lib'))
lib_path = os.path.abspath(os.path.join('..', 'configuration'))
import 
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("CyborgProtoOut")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    messages = msg.payload.split("\n\n\n*")
    print("------- messages ------", len(messages))
    for m in messages:
        if len(m.strip()) < 2:
            continue
        print(m.strip())
        json.loads(m.strip())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set('cyborg', 'cyborg')
client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
