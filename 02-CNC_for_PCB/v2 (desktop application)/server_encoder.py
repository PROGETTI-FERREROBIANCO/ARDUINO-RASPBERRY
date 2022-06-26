import socket as sck
import threading as thr
import RPi.GPIO as GPIO
from time import sleep
import serial


SPOSTAMENTO_ESEGUITO = 50

pico = None

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


    if asse == "Y": # l'asse Y presenta dei problemi elettrici e vengono compensati così:
        return muovi_motore_con_encorder(index, asse, spostamento, velocita)
    else:
        if not stato_assi[asse]["stato_finecorsa"][index]:
            GPIO.output(pins[asse]["pul"], GPIO.HIGH)
            sleep(velocita)
            GPIO.output(pins[asse]["pul"], GPIO.LOW)
            sleep(velocita)

            stato_assi[asse]["stato_asse"]+= spostamento
        return "nessuno"



def muovi_motore_con_encorder(index, asse, spostamento, velocita):
    global stato_assi

    errore = "nessuno"

    valore_encoder2 = 0
    valore_encoder1 = 0

    if not stato_assi[asse]["stato_finecorsa"][index]:

        try:
            pico.write(f"invia;".encode())
            run = True
            s = ""
            while run:
                ch = pico.read().decode() 
                if ch != "\n" and ch != "\r":
                    if ch == ";":
                        run = False
                    else:
                        s += ch

            valore_encoder1 = int(s)
        except:
            errore = "Errore pico"
            errore += f" - {connessione_pico()}"
            

        GPIO.output(pins[asse]["pul"], GPIO.HIGH)
        sleep(velocita)
        GPIO.output(pins[asse]["pul"], GPIO.LOW)
        sleep(velocita)



        try:
            pico.write(f"invia;".encode())
            run = True
            s = ""
            while run:
                ch = pico.read().decode() 
                if ch != "\n" and ch != "\r":
                    if ch == ";":
                        run = False
                    else:
                        s += ch

            valore_encoder2 = int(s)
        except:
            errore = "Errore pico"
            errore += f" - {connessione_pico()}"


        if abs(valore_encoder2-valore_encoder1) > SPOSTAMENTO_ESEGUITO:
            stato_assi[asse]["stato_asse"]+= spostamento
        else:
            return muovi_motore_con_encorder(index, asse, spostamento, velocita)

    return errore



def connessione_pico():
    global pico

    try: pico.close()
    except: pass

    try: 
        pico = serial.Serial(port='/dev/ttyACM0', baudrate=115200)
        sleep(3)
    except: return "Pico non connesso"

    return "nessuno"
    



def muovi_motori(index1, index2, asse1, asse2, spostamento1, spostamento2, velocita):
    errore = muovi_motore(index1, asse1, spostamento1, velocita)
    errore += f" - {muovi_motore(index2, asse2, spostamento2, velocita)}"
    return errore


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
        errore = "nessuno"
        try:
            self.connection.sendall(f"{str(stato_assi)}|{errore}".encode())
        except:
            self.running = False

        while self.running:
            try:
                receive = self.connection.recv(4096).decode()

                errore = "nessuno"

                if receive != "":
                    receive = receive.split("|")
                    if receive[0] == "muovi_motore":
                        errore = muovi_motore(int(float(receive[1])), receive[2], int(float(receive[3])), float(receive[4]))
                    elif receive[0] == "muovi_motori":
                        errore = muovi_motori(int(float(receive[1])),int(float(receive[2])), receive[3], receive[4], int(float(receive[5])), int(float(receive[6])), float(receive[7]))
                    elif receive[0] == "verifica_direzione":
                        verifica_direzione(receive[1], int(float(receive[2])))
                    elif receive[0] == "set_zero":
                        stato_assi["X"]["stato_asse"] = 0
                        stato_assi["Y"]["stato_asse"] = 0
                        stato_assi["Z_DX"]["stato_asse"] = 0
                        stato_assi["Z_SX"]["stato_asse"] = 0
                    self.connection.sendall(f"{str(stato_assi)}|{errore}".encode())
                else:
                    self.running = False
            except:
                pass


            
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
    connessione_pico()

    controllo_finecorsa = ControlloFinecorsa()
    controllo_finecorsa.start()

    s = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    s.bind(("0.0.0.0", 5000))

    s.listen()
    while True:
        try:
            connection, address = s.accept()
            client = ClientManager(connection, address, len(allClient))
            allClient.append(client)
            client.start()
        except:
            pass
        
if __name__ == "__main__":
    main()