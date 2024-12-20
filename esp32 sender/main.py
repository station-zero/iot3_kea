import esp32
from nrf24l01 import NRF24L01
import BME280 
from machine import SPI, Pin, ADC, SoftI2C, deepsleep
from time import sleep
import struct
from cryptolib import aes
from esp32 import gpio_deep_sleep_hold

gpio_deep_sleep_hold(True)

UID = 1 

batt_pin = Pin(12, Pin.OUT, Pin.PULL_UP)
batt_pin.off()

MQ4 = ADC(Pin(26))
MQ4.atten(ADC.ATTN_11DB)
MQ4.width(ADC.WIDTH_12BIT)

batt = ADC(Pin(25,Pin.IN))
batt.atten(ADC.ATTN_11DB)
batt.width(ADC.WIDTH_12BIT)

on_pin = Pin(13,Pin.OUT)
on_pin.on()

sleep(5)

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)
bme = BME280.BME280(i2c=i2c)

csn = Pin(5, mode=Pin.OUT, value=1) # Chip Select Not
ce = Pin(14, mode=Pin.OUT, value=0)  # Chip Enable
payload_size2 = 32
LED_pin = Pin(4, Pin.OUT)
LED_pin.off()

send_pipe = b"\xE1\x11\x11\x11\x11"

def setup():
    print("Initialising the nRF24L0+ Module")
    nrf = NRF24L01(SPI(2, sck=Pin(18), mosi=Pin(23),miso=Pin(19)), csn, ce, payload_size=payload_size2)
    nrf.set_channel(76)
    nrf.open_tx_pipe(send_pipe)
    nrf.stop_listening()
    return nrf

aplha = ["0","1","2","3","4","5","6","7","8","9","b","h","P","a","x","|","."]
key = ["r","a","y","E","p","w","9","s","q","L","2","5","1","k","m","z","3"]

def cipher_encrypt(plain_text):
    str_len = len(plain_text)
    new_string = ""
    
    for char in plain_text:
        counter = 0
        for letter in aplha:
            if char == letter:
                new_string += str(key[counter])
            counter += 1
    return new_string
 
def send(nrf, msg):
    try:
        encoded_string = msg.encode()
        nrf.send(encoded_string)
        print("sent")
    except OSError:
        print("Sorry message not sent")
    
nrf = setup()

def batt_procent():
    bund = 920 #ADC værdi når batteri er på 3.2 V
    loft = 1780 #ADC værdi når batteri er på 4.2 V
    procent = round(((batt.read()-bund)/(loft-bund))*100)
    if procent > 100: #så procenter ikke går over 100
        procent = 100
    elif procent < 0: # så procenter ikke går under 0
        procent = 0
    else:
        pass
    return procent

def mq_procent():
    procent = int(round(3.24/3.3 * (MQ4.read()/4095)*100,0))
    return procent

LED_pin.on()

polution = mq_procent()
#    print(polution)
temp = bme.temperature
temp = temp.strip("C")
temp = int(round(float(temp),0))
#    hum = bme.humidity
pres = bme.pressure
pres = pres.strip("hPa")
pres = int(round(float(pres),0))

battery = batt_procent()
print(batt.read())
data = f"{UID}|{polution}|{temp}|{pres}|{battery}"

print("-------------")
print("Clear text: ", data)
print("encrypted: " + cipher_encrypt(data))
print("-------------")

send_data = cipher_encrypt((data))
send(nrf, send_data)
send(nrf, "JAER")

sleep(30)

LED_pin.off()
on_pin.off()

deepsleep(60000)
