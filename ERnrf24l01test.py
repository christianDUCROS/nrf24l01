"""module (A)  / module (B)
    parametrer le module A ou B
    parametrer le canal
    parametrer la puissance et la vitesse
    fonctions disponibles : emission()
                            attente_reception()
                            attente_reception_timeout()
    programme principal:
        test emission
        test emisison x tentatives 
        test reception
"""

import usys
import utime
from machine import Pin, SPI, SoftSPI
import nrf24l01 
from micropython import const

# Responder pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Responder pauses an additional _RESPONER_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) initiator time to get into receive mode. The
# initiator may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_RESPONDER_SEND_DELAY = const(10)

if usys.platform == "esp32":  # Software SPI
    spi = SoftSPI(sck=Pin(25), mosi=Pin(33), miso=Pin(32))
    cfg = {"spi": spi, "csn": 26, "ce": 27}
elif usys.platform == "rp2":  # Hardware SPI with explicit pin definitions
    spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))
    cfg = {"spi": spi, "csn": 5, "ce": 6}
else:
    raise ValueError("Unsupported platform {}".format(usys.platform))

csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
spi = cfg["spi"]
nrf = nrf24l01.NRF24L01(spi, csn, ce, payload_size=8)
nrf.set_channel(46) #entre 0 et 125
nrf.set_power_speed(nrf24l01.POWER_3, nrf24l01.SPEED_250K) 

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

#module A ou B
module = 'A'
if module =='A' : 
    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
else :
    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])

nrf.start_listening()

def emission(message): #emission et renvoi de la réussite 
    # stop listening and send packet
    nrf.stop_listening()
    message_str = str(message)
    try:
        nrf.send(message_str.encode())
        etat = 1 # Envoi valide 
    except OSError:
        etat = 0 # Erreur envoi
    # start listening  pour accusé de reception
    nrf.start_listening()
    utime.sleep_ms(_RX_POLL_DELAY)
    return etat

def attente_reception(): # boucle infinie d'attente de datas
    nrf.start_listening()
    while True:  
        while nrf.any():
            message = nrf.recv()
            message = message.decode()
            utime.sleep_ms(_RX_POLL_DELAY)
            return message


def attente_reception_timeout(timeout = 250): #attente reception durant  250ms sinon timeout
    nrf.start_listening()
    start_time = utime.ticks_ms()
    while True:  
        while nrf.any():
            message = nrf.recv()
            message = message.decode()
            utime.sleep_ms(_RX_POLL_DELAY)
            return message
        if utime.ticks_diff(utime.ticks_ms(), start_time) > timeout :
            return "Timeout"




print("NRF24L01 test module loaded")
print("NRF24L01 pinout for test:")
print("    CE on", cfg["ce"])
print("    CSN on", cfg["csn"])
print("    SPI on", cfg["spi"])

#test d'émission
compteur = 0

while True : 
    compteur += 1
    print (compteur)
    etat = emission(compteur)
    print('état',etat)

'''
#test d'émission x tentatives 
compteur = 0

while True : 
    compteur += 1
    print (compteur)
    etat = 0
    while not etat : 
        etat = emission(compteur)
'''

'''
#test reception
while True : 
    #--------reception --------
    message = attente_reception_timeout() 
    print('message_recu', message)
'''

