# LIBRERIE #
import RPi.GPIO as GPIO
from time import sleep
import threading
import math
import numpy as np
import socket
from werkzeug.utils import secure_filename
from pathlib import Path
import websockets
import asyncio
import copy
from flask import Flask, render_template, jsonify, request
#-----------#

dir_path = str(Path(__file__).parent.resolve())

lock_termina = False
lock_pausa = False
lock_esegui_punta = threading.Lock()
lock_esegui = threading.Lock()

numero_istruzione = 0
# FLASK #
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = f"{dir_path}/folder_uploaded_file/"
app.config['MAX_CONTENT_PATH'] = 1024*1024*10 # 10 Mbyte

@app.route('/')
def ottieni_pagina_di_controllo():
    return render_template('index.html', dati = [comandi_parametri, extract_ip()])

@app.route('/comandi/<azione>', methods = ['GET', 'POST'])
def ricevi_comandi(azione):
    global lock_pausa
    global lock_termina
    global stato_assi
    try:
        if azione == "pausa":
            lock_pausa = True
            return("pausa")
        
        elif azione == "set-zero":
            for asse in stato_assi:
                stato_assi[asse]["stato_asse"] = 0
            return("set-zero")
        
        elif azione == "termina":
            lock_termina = True
            return("termina")

        elif azione == "riprendi":
            lock_pausa = False
            return("riprendi")

        elif azione == "upload":

            try:
                f = request.files['file_to_upload']
                f.save(f"{dir_path}/folder_uploaded_file/{secure_filename(f.filename)}")

                comandi_caricati = ""
                with open(f"{dir_path}/folder_uploaded_file/{f.filename}") as f:
                    comandi_caricati = f.read()

                return jsonify({"response":comandi_caricati})
            except:
                return "errore"
            

        elif azione == "esegui":
            global numero_istruzione

            lock_pausa = False

            comandi_ricevuti = eval(str(request.form).replace("ImmutableMultiDict", ""))[0][0]
            print(comandi_ricevuti)

            if lock_esegui.acquire(False):

                for i, comando_ricevuto in enumerate(comandi_ricevuti.split("\n")):

                    numero_istruzione = i

                    comando = comando_ricevuto.split("(")[0]
                    parametri = comando_ricevuto.split("(")[1].replace(")", "").split(",")

                    parametri = [int(a) for a in parametri]

                    comandi_funzioni[comando](parametri, "con_lock")

                numero_istruzione = 9999

                lock_termina = False

                lock_esegui.release()

                return jsonify({"stato_operazione":"esegui_finito"})

            return jsonify({"stato_operazione":"in_esecuzione"})

            

        elif azione == "esegui-punta":
            lock_pausa = True

            comandi_ricevuti = eval(str(request.form).replace("ImmutableMultiDict", ""))[0][0]
            print(comandi_ricevuti)

            if lock_esegui_punta.acquire(False):

                copia_stato_assi = copy.deepcopy(stato_assi)

                for comando_ricevuto in comandi_ricevuti.split("\n"):

                    comando = comando_ricevuto.split("(")[0]
                    parametri = comando_ricevuto.split("(")[1].replace(")", "").split(",")

                    parametri = [int(a) for a in parametri]

                    comandi_funzioni[comando](parametri, "senza_lock")

                for asse in copia_stato_assi:
                    GPIO.output(pins[asse]["dir"], copia_stato_assi[asse]["stato_direzione"])

                if not lock_esegui.locked(): lock_pausa = False
                    
                lock_termina = False
                
                lock_esegui_punta.release()

                return jsonify({"stato_operazione":"esegui_punta_finito"})

            return jsonify({"stato_operazione":"in_esecuzione"})


                        
    except:
        return "errore"


@app.route('/ottieni-dati/<dato>')
def ottieni_dati(dato):
    if dato == "assi":
        return jsonify(stato_assi)
    elif dato == "esecuzione-comando":
        return jsonify({"stato_esegui": lock_esegui.locked(), "stato_pausa": lock_pausa, "stato_termina": lock_termina, "stato_esegui_punta": lock_esegui_punta.locked()})
    elif dato == "numero-istruzione":
        return jsonify({"numero_istruzione": numero_istruzione})
#-----------#

# COSTANTI e VARIABILI GLOBALI #
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


PAUSA_TRA_IMPULSI = 0.001
N_PUNTI_ARCO = 100
ALZA_PUNTA = -500 #sempre negativo
ABBASSA_PUNTA = 500 #sempre positivo
#-----------#

# CREAZIONE WEBSOCKET #
class MyWsServer(threading.Thread):
    def __init__(self, address, port):
        super().__init__()
        self.port = port
        self.address = address

    def run(self):
        loop = asyncio.new_event_loop()
        ws_server = websockets.serve(self.invia_dati_aggiornamento, self.address, self.port,
                                     ping_timeout=None, ping_interval=None, loop=loop)
        loop.run_until_complete(ws_server)
        loop.run_forever()

    async def invia_dati_aggiornamento(self, websocket, path):
        n_istr_precedente = numero_istruzione
        s_assi_precedente = {}
        while True:
            
            n_istr_attuale = numero_istruzione
            if n_istr_precedente != n_istr_attuale:
                await websocket.send(f"numero_istruzione#{n_istr_attuale}")
                n_istr_precedente = n_istr_attuale
            
            s_assi_attuale = copy.deepcopy(stato_assi)
            
            if s_assi_attuale != s_assi_precedente:
                #come vengono inviati i dati→  valori_attuali:x%y%z @ finecorsa:x%y%z
                await websocket.send(f'stato_assi#{s_assi_attuale["X"]["stato_asse"]}%{s_assi_attuale["Y"]["stato_asse"]}%{s_assi_attuale["Z_DX"]["stato_asse"]}#'+
                f'{s_assi_attuale["X"]["stato_finecorsa"][0]}%{s_assi_attuale["X"]["stato_finecorsa"][1]}%'+
                f'{s_assi_attuale["Y"]["stato_finecorsa"][0]}%{s_assi_attuale["Y"]["stato_finecorsa"][1]}%'+
                f'{s_assi_attuale["Z_DX"]["stato_finecorsa"][0]}%{s_assi_attuale["Z_DX"]["stato_finecorsa"][1]}')
                s_assi_precedente = copy.deepcopy(s_assi_attuale)
            

#---------------------#

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:       
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

def settaggio_motori():
    GPIO.setmode(GPIO.BCM)  #tipo di riferimento, numerazione della cpu
    GPIO.setwarnings(False)
    for asse in pins:
        GPIO.setup(pins[asse]["finecorsa"][0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pins[asse]["finecorsa"][1], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pins[asse]["pul"], GPIO.OUT)
        GPIO.setup(pins[asse]["dir"], GPIO.OUT)
        

"""
INIZIO FUNZIONI PER MUOVERE I MOTORI
"""

def muovi_motore_con_lock(index, asse, spostamento):

    while lock_pausa: pass

    return muovi_motore_senza_lock(index, asse, spostamento)

def muovi_motore_senza_lock(index, asse, spostamento):
    global stato_assi

    if not lock_termina and not stato_assi[asse]["stato_finecorsa"][index]:
        GPIO.output(pins[asse]["pul"], GPIO.HIGH)
        sleep(PAUSA_TRA_IMPULSI)
        GPIO.output(pins[asse]["pul"], GPIO.LOW)
        sleep(PAUSA_TRA_IMPULSI)
        stato_assi[asse]["stato_asse"]+= spostamento
        return True
    return False

def muovi_motori_con_lock(indexs, assi, spostamenti):

    while lock_pausa: pass

    return muovi_motori_senza_lock(indexs, assi, spostamenti)

def muovi_motori_senza_lock(indexs, assi, spostamenti):
    global stato_assi

    if not lock_termina and not stato_assi[assi[0]]["stato_finecorsa"][indexs[0]] and not stato_assi[assi[1]]["stato_finecorsa"][indexs[1]]:
        GPIO.output(pins[assi[0]]["pul"], GPIO.HIGH)
        GPIO.output(pins[assi[1]]["pul"], GPIO.HIGH)
        sleep(PAUSA_TRA_IMPULSI)
        GPIO.output(pins[assi[0]]["pul"], GPIO.LOW)
        GPIO.output(pins[assi[1]]["pul"], GPIO.LOW) 
        sleep(PAUSA_TRA_IMPULSI)

        stato_assi[assi[0]]["stato_asse"]+= spostamenti[0]
        stato_assi[assi[1]]["stato_asse"]+= spostamenti[1]
        return True
    return False



"""
FINE FUNZIONI PER MUOVERE I MOTORI
"""


def verifica_direzione(asse, spostamento):
    if spostamento >= 0:
        stato_assi[asse]["stato_direzione"] = True
        GPIO.output(pins[asse]["dir"], GPIO.HIGH)
        sleep(PAUSA_TRA_IMPULSI)
        return 0
    else:
        stato_assi[asse]["stato_direzione"] = False
        GPIO.output(pins[asse]["dir"], GPIO.LOW)
        sleep(PAUSA_TRA_IMPULSI)
        return 1


def muovi_due_motori(comandi, tipo_funzione_muovi_motore):
    
    asse = []
    spostamento = []
    index = []

    for comando in comandi.split("#"):
        asse.append(comando.split(":")[0])
        spostamento.append(int(comando.split(":")[1]))
        index.append(verifica_direzione(asse[-1], spostamento[-1]))
    
    #il maggiore è sempre in posizione 0
    if abs(spostamento[0]) < abs(spostamento[1]):
        spostamento[0], spostamento[1] = spostamento[1], spostamento[0]
        asse[0], asse[1] = asse[1], asse[0]
        index[0], index[1] = index[1], index[0]
    
    if spostamento[1] == 0:
        for _ in range(abs(spostamento[0])): eval(f"muovi_motore_{tipo_funzione_muovi_motore}")(index[0], asse[0], abs(spostamento[0])//spostamento[0]) #1 motore
    elif spostamento[0] == spostamento[1]:
        for _ in range (abs(spostamento[0])):
            eval(f"muovi_motori_{tipo_funzione_muovi_motore}")(index, asse, [abs(spostamento[0])//spostamento[0], abs(spostamento[1])//spostamento[1]]) #2 motori
    else: 
        #------CALCOLI-------#
        spostamento_arrotondato = round(spostamento[0]/abs(spostamento[1]))*abs(spostamento[1])
        impulsi_arrotondati = abs(spostamento_arrotondato)//abs(spostamento[1])
        differenza_impulsi = spostamento[0] - spostamento_arrotondato
        ogni_quanto_impulso = 0
        if differenza_impulsi != 0:
            ogni_quanto_impulso = abs(spostamento_arrotondato)//abs(differenza_impulsi)
        #--------------------#

        for a in range (abs(spostamento[1])):
            for i in range (impulsi_arrotondati):
                if i == impulsi_arrotondati//2:
                    eval(f"muovi_motori_{tipo_funzione_muovi_motore}")(index, asse, [abs(spostamento[0])//spostamento[0], abs(spostamento[1])//spostamento[1]]) #2
                else: eval(f"muovi_motore_{tipo_funzione_muovi_motore}")(index[0], asse[0], abs(spostamento[0])//spostamento[0]) #1
                
                if ogni_quanto_impulso!= 0 and (i+a*impulsi_arrotondati)%ogni_quanto_impulso == 0 and differenza_impulsi!=0:
                    eval(f"muovi_motore_{tipo_funzione_muovi_motore}")(index[0], asse[0], differenza_impulsi//abs(differenza_impulsi)) #1
                    differenza_impulsi -= differenza_impulsi//abs(differenza_impulsi)
                
    
                
        
"""

   _____ ____  __  __          _   _ _____ _____ 
  / ____/ __ \|  \/  |   /\   | \ | |  __ \_   _|
 | |   | |  | | \  / |  /  \  |  \| | |  | || |  
 | |   | |  | | |\/| | / /\ \ | . ` | |  | || |  
 | |___| |__| | |  | |/ ____ \| |\  | |__| || |_ 
  \_____\____/|_|  |_/_/    \_\_| \_|_____/_____|
                                                                                             

"""

def vai_incrementale(parametri, tipo_funzione_muovi_motore):
    parametri = [round(float(i)) for i in parametri]

    coordx = parametri[0]
    coordy = parametri[1]
    coordz = parametri[2]

    print(f"coordinate########## X:{coordx} - Y: {coordy}")
    """movimento asse z"""
    muovi_due_motori(f"Z_SX:{coordz}#Z_DX:{coordz}", tipo_funzione_muovi_motore)
    """----------------"""
    """movimento asse x-y"""
    muovi_due_motori(f"X:{coordx}#Y:{coordy}", tipo_funzione_muovi_motore)
    """----------------"""
    print(f'X:{stato_assi["X"]["stato_asse"]} -  Y:{stato_assi["Y"]["stato_asse"]} - Z:{stato_assi["Z_SX"]["stato_asse"]}')
    

def vai_lineare(parametri, tipo_funzione_muovi_motore):
    parametri = [round(float(i)) for i in parametri]

    coordx = parametri[0]
    coordy = parametri[1]
    coordz = parametri[2]

    vai_incrementale([-(stato_assi["X"]["stato_asse"]-coordx), -(stato_assi["Y"]["stato_asse"]-coordy), -(stato_assi["Z_SX"]["stato_asse"]-coordz)], tipo_funzione_muovi_motore)


def arco(parametri, tipo_funzione_muovi_motore):
    parametri = [round(float(i)) for i in parametri]

    raggio = parametri[0]
    angolo_iniziale = math.radians(parametri[1])
    angolo_finale = math.radians(parametri[2])

    coordx_centro = stato_assi["X"]["stato_asse"]
    coordy_centro = stato_assi["Y"]["stato_asse"]
    coordz = stato_assi["Z_SX"]["stato_asse"]

    #da controllare  se è +1 o -1 per alzarlo
    """dal centro dell'arco, mi alzo un po' la z e mi sposto in un punto della circonferenza"""
    vai_incrementale([raggio*np.cos(angolo_iniziale),raggio*np.sin(angolo_iniziale), ALZA_PUNTA], tipo_funzione_muovi_motore)
    vai_incrementale([0, 0, ABBASSA_PUNTA], tipo_funzione_muovi_motore)
    """---------------------------"""
    """disegno l'arco"""
    for ang in np.linspace(angolo_iniziale,angolo_finale,int((angolo_finale-angolo_iniziale)*100)):
        vai_lineare([coordx_centro+raggio*np.cos(ang), coordy_centro+raggio*np.sin(ang), coordz], tipo_funzione_muovi_motore)
    """---------------------------"""
    """dal centro dell'arco, mi alzo un po' la z e mi sposto in un punto della circonferenza"""
    vai_lineare([coordx_centro, coordy_centro, stato_assi["Z_SX"]["stato_asse"]+ALZA_PUNTA], tipo_funzione_muovi_motore)
    vai_incrementale([0, 0, ABBASSA_PUNTA], tipo_funzione_muovi_motore)
    """---------------------------"""

def segmento(parametri, tipo_funzione_muovi_motore):
    parametri = [round(float(i)) for i in parametri]

    lunghezza = parametri[0]
    inclinazione = math.radians(parametri[1])

    vai_incrementale([lunghezza*np.cos(inclinazione), lunghezza*np.sin(inclinazione), 0], tipo_funzione_muovi_motore)

def collegamento(parametri, tipo_funzione_muovi_motore):
    parametri = [round(float(i)) for i in parametri]

    coordx_centro = stato_assi["X"]["stato_asse"]
    coordy_centro = stato_assi["Y"]["stato_asse"]

    lunghezza = parametri[0]
    larghezza = parametri[1]
    inclinazione = math.radians(parametri[2])
    angolo = np.degrees(np.arctan(-1/(np.tan(inclinazione))))

    vai_incrementale([0,0,ALZA_PUNTA], tipo_funzione_muovi_motore)
    segmento([larghezza/2,angolo], tipo_funzione_muovi_motore)

    vai_incrementale([0,0,ABBASSA_PUNTA], tipo_funzione_muovi_motore)
    segmento([lunghezza, parametri[2]], tipo_funzione_muovi_motore) #disegniamo il primo segmento

    vai_incrementale([0,0,ALZA_PUNTA], tipo_funzione_muovi_motore)
    segmento([-larghezza,angolo], tipo_funzione_muovi_motore)

    vai_incrementale([0,0,ABBASSA_PUNTA], tipo_funzione_muovi_motore)
    segmento([lunghezza, 180+parametri[2]], tipo_funzione_muovi_motore)

    vai_lineare([coordx_centro, coordy_centro, stato_assi["Z_SX"]["stato_asse"]+ALZA_PUNTA], tipo_funzione_muovi_motore)
    vai_incrementale([0, 0, ABBASSA_PUNTA], tipo_funzione_muovi_motore)


def foro(parametri, tipo_funzione_muovi_motore):
    parametri = [round(float(i)) for i in parametri]

    profondita = parametri[0]

    vai_incrementale([0,0,profondita], tipo_funzione_muovi_motore)
    




comandi_parametri = {
    "vai_lineare": ["coordx","coordy","coordz"],
    "vai_incrementale": ["coordx","coordy","coordz"],
    "arco": ["raggio","angolo_iniziale","angolo_finale"],
    "segmento": ["lunghezza", "inclinazione"],
    "collegamento": ["lunghezza","larghezza","inclinazione"],
    "foro": ["profondita"]
}
comandi_funzioni = {
    "vai_lineare": vai_lineare,
    "vai_incrementale": vai_incrementale,
    "arco": arco,
    "segmento": segmento,
    "collegamento": collegamento,
    "foro": foro
}


"""

  ______ _____ _   _ ______    _____ ____  __  __          _   _ _____ _____ 
 |  ____|_   _| \ | |  ____|  / ____/ __ \|  \/  |   /\   | \ | |  __ \_   _|
 | |__    | | |  \| | |__    | |   | |  | | \  / |  /  \  |  \| | |  | || |  
 |  __|   | | | . ` |  __|   | |   | |  | | |\/| | / /\ \ | . ` | |  | || |  
 | |     _| |_| |\  | |____  | |___| |__| | |  | |/ ____ \| |\  | |__| || |_ 
 |_|    |_____|_| \_|______|  \_____\____/|_|  |_/_/    \_\_| \_|_____/_____|
                                                                             
                                                                             
"""

def controllo_finecorsa_asse(asse):
    global stato_assi
    for i in range(0,2):
        if GPIO.input(pins[asse]["finecorsa"][i]) == 1:
            stato_assi[asse]["stato_finecorsa"][i] = False
        else:
            stato_assi[asse]["stato_finecorsa"][i] = True

def azzeramento_motori():
    verifica_direzione("X", -1)
    verifica_direzione("Y", -1)
    verifica_direzione("Z_DX", 1)
    verifica_direzione("Z_SX", 1)

    stato = True
    while stato != False:
        stato = np.logical_or(np.logical_or(np.logical_or(muovi_motore_con_lock(1,"X",0), muovi_motore_con_lock(1,"Y",0)), muovi_motore_con_lock(0,"Z_SX",0)), muovi_motore_con_lock(0,"Z_DX",0)) 
        # da testare i finecorsa

class ControlloFinecorsa(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        
    def run(self):
        while self.running:
            controllo_finecorsa_asse("X")
            controllo_finecorsa_asse("Y")
            controllo_finecorsa_asse("Z_DX")


def main():
    settaggio_motori()

    controllo_finecorsa = ControlloFinecorsa()
    controllo_finecorsa.start()
    
    azzeramento_motori()
    print("Motori settati correttamente!\n ################## Pronto all'uso ###################")

    thread_in = MyWsServer('0.0.0.0', 5678)
    thread_in.start()

    app.run(host='0.0.0.0')
                
            

if __name__ == '__main__':
    main()