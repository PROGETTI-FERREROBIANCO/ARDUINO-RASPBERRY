import socket as sck
import threading as thr
import RPi.GPIO as GPIO
from time import sleep


allClient = []

pins = {
    "X":{
        "finecorsa": [27, 17], # destra , sinistra
        "pul": 5,
        "dir": 19
         },
    "Y":{
        "finecorsa": [3, 4], # alto , basso
        "pul": 26,
        "dir": 6
        },
    "Z_DX":{
        "finecorsa": [2, 22], # alto , basso
        "pul": 10,
        "dir": 13
        },
    "Z_SX":{
        "finecorsa": [2, 22], # alto , basso
        "pul": 11,
        "dir": 9
        }
    }

stato_assi = {
    "X":{
        "stato_asse": 0,
        "stato_finecorsa": [False, False],
        "stato_direzione": True
         },
    "Y":{
        "stato_asse": 0,
        "stato_finecorsa": [False, False],
        "stato_direzione": True
        },
    "Z_DX":{
        "stato_asse": 0,
        "stato_finecorsa": [False, False],
        "stato_direzione": True
        },
    "Z_SX":{
        "stato_asse": 0,
        "stato_direzione": True
        }
    }
stato_assi["Z_SX"]["stato_finecorsa"] = stato_assi["Z_DX"]["stato_finecorsa"] # in modo che si sincronizzino insieme



def verifica_direzione(asse, spostamento):
    if spostamento >= 0:
        stato_assi[asse]["stato_direzione"] = True
        GPIO.output(pins[asse]["dir"], GPIO.HIGH)
    else:
        stato_assi[asse]["stato_direzione"] = False
        GPIO.output(pins[asse]["dir"], GPIO.LOW)

def muovi_motore(index, asse, spostamento, velocita):
    global stato_assi

    if not stato_assi[asse]["stato_finecorsa"][index]:
        GPIO.output(pins[asse]["pul"], GPIO.HIGH)
        sleep(velocita)
        GPIO.output(pins[asse]["pul"], GPIO.LOW)
        sleep(velocita)

        stato_assi[asse]["stato_asse"]+= spostamento



def muovi_motori(index1, index2, asse1, asse2, spostamento1, spostamento2, velocita):
    global stato_assi

    if not stato_assi[asse1]["stato_finecorsa"][index1] and not stato_assi[asse2]["stato_finecorsa"][index2]:
        GPIO.output(pins[asse1]["pul"], GPIO.HIGH)
        GPIO.output(pins[asse2]["pul"], GPIO.HIGH)
        sleep(velocita)
        GPIO.output(pins[asse1]["pul"], GPIO.LOW)
        GPIO.output(pins[asse2]["pul"], GPIO.LOW)
        sleep(velocita)

        stato_assi[asse1]["stato_asse"]+= spostamento1
        stato_assi[asse2]["stato_asse"]+= spostamento2


def controllo_finecorsa_asse(asse):
    global stato_assi
    for i in range(0,2):
        if GPIO.input(pins[asse]["finecorsa"][i]) == 1:
            stato_assi[asse]["stato_finecorsa"][i] = False
        else:
            stato_assi[asse]["stato_finecorsa"][i] = True


class ControlloFinecorsa(thr.Thread):
    def __init__(self):
        thr.Thread.__init__(self)
        self.running = True
        
    def run(self):
        while self.running:
            controllo_finecorsa_asse("X")
            controllo_finecorsa_asse("Y")
            controllo_finecorsa_asse("Z_DX")

class ClientManager(thr.Thread):
    def __init__(self, connection, address, nome ):
        thr.Thread.__init__(self)
        self.nome = nome
        self.connection = connection
        self.address = address
        self.running = True
    #OVERRIDE
    def run(self):
        global stato_assi
        self.connection.sendall(str(stato_assi).encode())
        while self.running:
            receive = self.connection.recv(4096).decode()

            if receive != "":
                receive = receive.split("|")
                if receive[0] == "muovi_motore":
                    muovi_motore(int(float(receive[1])), receive[2], int(float(receive[3])), float(receive[4]))
                elif receive[0] == "muovi_motori":
                    muovi_motori(int(float(receive[1])),int(float(receive[2])), receive[3], receive[4], int(float(receive[5])), int(float(receive[6])), float(receive[7]))
                elif receive[0] == "verifica_direzione":
                    verifica_direzione(receive[1], int(float(receive[2])))
                elif receive[0] == "set_zero":
                    stato_assi["X"]["stato_asse"] = 0
                    stato_assi["Y"]["stato_asse"] = 0
                    stato_assi["Z_DX"]["stato_asse"] = 0
                    stato_assi["Z_SX"]["stato_asse"] = 0
                self.connection.sendall(str(stato_assi).encode())
            else:
                self.running = False


            
def settaggio_motori():
    GPIO.setmode(GPIO.BCM)  #tipo di riferimento, numerazione della cpu
    GPIO.setwarnings(False)
    for asse in pins:
        GPIO.setup(pins[asse]["finecorsa"][0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pins[asse]["finecorsa"][1], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pins[asse]["pul"], GPIO.OUT)
        GPIO.setup(pins[asse]["dir"], GPIO.OUT)


def main():
    settaggio_motori()

    controllo_finecorsa = ControlloFinecorsa()
    controllo_finecorsa.start()

    s = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    s.bind(("0.0.0.0", 5000))

    s.listen()
    while True:
        connection, address = s.accept()
        client = ClientManager(connection, address, len(allClient))
        allClient.append(client)
        client.start()
        
if __name__ == "__main__":
    main()
