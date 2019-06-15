#MQTT for device to device communication
#https://tutorials-raspberrypi.com/raspberry-pi-mqtt-broker-client-wireless-communication/
#https://pypi.org/project/paho-mqtt/#id3
#sudo pip install paho-mqtt

import paho.mqtt.client as mqtt
import time
import random
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn	
import os
from gtts import gTTS
 
MQTT_SERVER = "localhost"
MQTT_TOPIC = "facial/ownerdetected"
nano_msg = "noresults"

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)

needwater = False
SystemTime = time.localtime()
hour = SystemTime.tm_hour
starttime = time.time()
endtime = time.time()
asks = ['I am feeling dry can someone water me?','Thanks can I have another?','Water, I need Water.','Hey, Hey, I need you.','Hi, Do not forget about me. ','Help, Help. ','Come here, please. ','A hum','Can I have some water please ','You know I can see you right?']
i = 0
#Premake speech audio files
for speech in asks:
	tts = gTTS(text=(speech+"."), lang="en-us", slow = False)
	tts.save("ask"+str(i)+".mp3")
	i=i+1
	time.sleep(10)
	print(speech)

 
# The callback for when the client receives a CONNACK response from the Nano facial recognition server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	global nano_msg
	print(msg.topic+" "+str(msg.payload))
	nano_msg = str(msg.payload)
	#Update Plant program on status of Owner presence.
 

def speak(message):
	global asks
	
	print(asks[message])
	os.system("ffplay -nodisp -autoexit ask"+str(message)+".mp3")
 


def main():
	global needwater
	global starttime
	global endtime
	global asks
	global nano_msg
	
	if nano_msg == "b'ownerfound'":
		speakup = True
	else:
		speakup = False
	SystemTime = time.localtime()
	hour = SystemTime.tm_hour
	if hour > 18 and hour < 20:
		speakup = True
	length = len(asks)-3
	setpoint = 1300 #moisture setpoint 1300
	if needwater == False:
		if chan.value > setpoint:
			#Ask for water
			needwater = True
			starttime = time.time()
			speak(0)

	elif speakup == True:
		endtime = time.time()
		beenwaiting = endtime - starttime
		ranint = random.randint(0,length) + 2
		if beenwaiting > 180: #Adjust time for speaking frequency.
			speak(ranint)
			starttime = time.time()
		if chan.value < 1260:#moisture happy level 1260
			needwater = False
			speak(1)
	if needwater == True:
		if chan.value < 1060:#moisture happy level 1260
			needwater = False
			speak(1)
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(MQTT_SERVER, 1883, 60)
client.loop_start() #Listen for messages from Nano
			
while True:
	global nano_msg
	print(nano_msg)
	print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
	time.sleep(10)
	
	main()

