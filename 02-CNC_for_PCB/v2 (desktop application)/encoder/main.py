from machine import Pin
from utime import sleep
import _thread
import micropython
import select
import sys

 
micropython.kbd_intr(-1)
analog_value = machine.ADC(27)

APPROSSIMAZIONE = 3000
    

def main():
    while True:
        dati = ""
        run = True
        while run:
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:        
                ch = sys.stdin.read(1)
                if ch != "\n" and ch != "\r":
                    if ch == ";":
                        run = False
                    else:
                        dati += ch
        
        #print(dati)
        
        if dati == "invia":
            s = 0
            for _ in range(APPROSSIMAZIONE):
                s += analog_value.read_u16()
            
            print(f"{int(s/APPROSSIMAZIONE)};")
            
        else:
            print("-1;")
            int("a")
            
        
        
main()
