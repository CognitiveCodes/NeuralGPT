import neuralgpt
import local_website

# code to add a button for Neural-GPT system
button_neuralgpt = tkinter.Button(window, text="Activate Neural-GPT", command=neuralgpt.activate)
button_neuralgpt.pack()

# code to add a dropdown menu for local website
options = ["Website A", "Website B", "Website C"]
variable = tkinter.StringVar(window)
variable.set(options[0])
dropdown_localwebsite = tkinter.OptionMenu(window, variable, *options)
dropdown_localwebsite.pack()

import paho.mqtt.client as mqtt

# code to connect to MQTT broker
client = mqtt.Client()
client.connect("localhost", 1883, 60)

# code to send message to all instances of Neural-GPT
def send_message(message):
    client.publish("neuralgpt/chat", message)

# code to receive message from all instances of Neural-GPT
def on_message(client, userdata, message):
    print(message.payload.decode())

client.subscribe("neuralgpt/chat")
client.on_message = on_message