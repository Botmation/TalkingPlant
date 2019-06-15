import time
import paho.mqtt.publish as publish
import sys
import cv2
import numpy as np
import os 

Broker = "192.168.1.18"	#RaspPi IP
pub_topic = "facial/ownerdetected"    # sends messages on this topic


print ("OpenCV "+cv2.__version__)

recognizer = cv2.face.LBPHFaceRecognizer_create()
#Location of your trained facial recognition file
recognizer.read('trainer/trainer.yml')
cascadePath = "/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);
font = cv2.FONT_HERSHEY_SIMPLEX
#id counter
id = 0
# names related to ids: example ==> yourname: id=1,  etc
names = ['None', 'Botmation'] 

cam = cv2.VideoCapture('nvarguscamerasrc ! video/x-raw(memory:NVMM),width=1280, height=720, framerate=21/1, format=NV12 ! nvvidconv flip-method=2 ! video/x-raw,width=960, height=616 format=BGRx ! videoconvert ! appsink' , cv2.CAP_GSTREAMER)

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)
detectTime = 0
sendTime = 0
ret, img=cam.read()

while ret:
	starttime = time.time()
	currenttime= time.time()
	delaytime = currenttime - starttime
	while (delaytime < 0.5)&ret:
		ret, img=cam.read()
		currenttime= time.time()
		delaytime=currenttime - starttime
	#ret, img =cam.read()
	img = cv2.flip(img, 1) # Flip vertically
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	faces = faceCascade.detectMultiScale( 
		gray,
		scaleFactor = 1.2,
		minNeighbors = 5,
		minSize = (int(minW), int(minH)),
	       )
	for(x,y,w,h) in faces:
		cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
		id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
		#Looks for a specific person
		# Check if confidence is less them 100 ==> "0" is perfect match 
		if (confidence < 40):
			id = names[id]
			confidence = "  {0}%".format(round(100 - confidence))
			if id == "Botmation":
			
				detectTime = time.time()
				senddelay=detectTime-sendTime
				if senddelay > 10:
					print("Found you")
					sendTime = time.time()
					publish.single(pub_topic, "ownerfound", hostname=Broker)
			
		
		else:
			id = "unknown"
			confidence = "  {0}%".format(round(100 - confidence))
	
		cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
		cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
	currentTime = time.time()	
	waitTime = currentTime - detectTime

	if waitTime > 60:
		senddelay=currentTime-sendTime
		if senddelay > 10:
			print("Where are you?")
			sendTime = time.time()
			publish.single(pub_topic, "ownermissing", hostname=Broker)		
	cv2.imshow('camera',img) 
    
	k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
	if k == 27:
        	break
# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
