# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()


import network
from time import sleep

ssid = 'YOUR_SSID'
password = 'YOUR_PASSWORD'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

tentativi = 0
while tentativi < 5:
    if station.isconnected() == False:
        print("Non collegato al WiFi")
    else:
        print('Connection successful')
        print(station.ifconfig())
        break
    tentativi += 1
    sleep(1)

