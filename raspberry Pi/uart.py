
#UART
#TX = GPIO14
#RX = GPIO15

import serial
import time
import requests
from datetime import datetime

ser = serial.Serial(
  port='/dev/ttyS0',
  baudrate = 9600,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS
)

id = ""
polution = ""
pressure = ""
temp = ""
battery = ""

def upload():
	time = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')

	url = 'https://runtime.pythonanywhere.com/data'
	pw = "fisk123"
	
	myobj = {'pw':pw,'id': id,'polution':polution,'temp':temp,'pressure':pressure,'time':time,'battery':battery}

	x = requests.post(url, json = myobj)

	print(x.text)

while True:
	data = ser.readline().decode("utf-8").strip()

	if len(data) > 6:
		print(data)
		d = data.split("|")
		id = d[0]
		polution = d[1]
		temp = d[2]
		pressure = d[3]
		battery = d[4]
		upload()

