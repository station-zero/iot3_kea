from nrf24l01 import NRF24L01
from machine import SPI, Pin, UART
from time import sleep
import struct

aplha = ["0","1","2","3","4","5","6","7","8","9","b","h","P","a","x","|","."]
key = ["r","a","y","E","p","w","9","s","q","L","2","5","1","k","m","z","3"]

csn = Pin(5, mode=Pin.OUT, value=1) # Chip Select Not
ce = Pin(14, mode=Pin.OUT, value=0)  # Chip Enable
payload_size2 = 32

pipe = b"\xE1\x11\x11\x11\x11"

port = 2
speed = 9600
uart = UART(port, speed, tx=16, rx=17, bits=8, parity=None, stop=1) # UART objekt


def cipher_decrypt(encrypt_text):
    str_len = len(encrypt_text)
    new_string = ""
    
    for char in encrypt_text:
        counter = 0
        for cipher in key:
            if char == cipher:
                new_string += str(aplha[counter])
            counter += 1
    return new_string

def setup():
    print("Initialising the nRF24L0+ Module")
    nrf = NRF24L01(SPI(2, sck=Pin(18), mosi=Pin(23),miso=Pin(19)), csn, ce, payload_size=payload_size2)
    nrf.set_channel(76)
    nrf.open_tx_pipe(pipe)
    nrf.start_listening()
    print("ready")
    return nrf

nrf = setup()
while True:
    if nrf.any():
        package = nrf.recv()       
        msg = str(package.decode("utf-8"))
        print("Dette er den krypteret besked " + msg)
        print("Dette er den dekrypteret besked " + cipher_decrypt(msg))
        
        uart.write(cipher_decrypt(msg) + "\n")
        