import PySimpleGUI as sg
import socket as sck
import threading as thr
import shelve
import turtle
from time import sleep
import math
import numpy as np
import datetime
from pathlib import Path
import platform

s = None

dir_path = str(Path(__file__).parent.resolve())
if str(platform.system()) != "Windows":
    dir_path += "/"
else: dir_path += "\\"


lista_step = []

incremento_x_step = 0
incremento_y_step = 0
incremento_z_step = 0

# ________________________________
window_spcb = None
# ---
window_simulazione = None
canvas_simulazione = None
a_turtle_simulazione = None
# ---
window_stampa = None
canvas_stampa = None
a_turtle_stampa = None
esegui_incremento = None
# ---
window_gestione_manuale = None
# ________________________________


conversione_unita_di_misura = {
    "cmm": 1,
    "dmm": 10,
    "mm": 100,
    "cm": 1000,
    "dm": 10000
}




settings = shelve.open(f'{dir_path}app_settings')

settings["filename"] = None
settings["stato_connessione"] = "NON CONNESSO"

"""
settings["ip"] = "192.168.1.51"
settings["porta"] = 5000
settings["numero_punti_arco"] = 100
settings["pen_up_punta"] = -500
settings["pen_down_punta"] = 500
settings["unita_di_misura"] = "cmm"
settings["velocita_disegno"] = 10
settings["proporzione_disegno"] = 10
settings["numero_step_singolo_movimento"] = 10
"""


"""

   _____ ____  __  __          _   _ _____ _____ 
  / ____/ __ \|  \/  |   /\   | \ | |  __ \_   _|
 | |   | |  | | \  / |  /  \  |  \| | |  | || |  
 | |   | |  | | |\/| | / /\ \ | . ` | |  | || |  
 | |___| |__| | |  | |/ ____ \| |\  | |__| || |_ 
  \_____\____/|_|  |_/_/    \_\_| \_|_____/_____|
                                                                                             

"""

lock_termina = thr.Lock()
lock_pausa = thr.Lock()
lock_pausa_istruzione = thr.Lock()


stato_assi = {}

stato_assi_simulazione = {
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
stato_assi_simulazione["Z_SX"]["stato_finecorsa"] = stato_assi_simulazione["Z_DX"]["stato_finecorsa"] # in modo che si sincronizzino insieme


"""
INIZIO FUNZIONI PER MUOVERE I MOTORI
"""

def verifica_direzione(asse, spostamento, dict_da_usare):
    global stato_assi
    global stato_assi_simulazione

    if dict_da_usare == "stato_assi":

        try:
            s.sendall(f"verifica_direzione|{asse}|{spostamento}".encode())
            
            ms = s.recv(4096).decode()
            stato_assi = eval(ms.split("|")[0])
            if ms.split("|")[1] != "nessuno":
                save_log(ms.split("|")[1])

        except:
            settings["stato_connessione"] = "ERRORE"
            save_log("Errore con la connessione")

        aggiorna_text()
    else:
        pass

    if spostamento >= 0: return 0
    else: return 1


# STAMPA
def muovi_motore_con_lock(index, asse, spostamento, dict_da_usare):
    while lock_pausa.locked() and not lock_termina.locked(): pass
    muovi_motore_senza_lock(index, asse, spostamento, dict_da_usare)

def muovi_motore_senza_lock(index, asse, spostamento, dict_da_usare):
    global stato_assi
    global stato_assi_simulazione
    global lock_pausa
    global lock_termina


    if dict_da_usare == "stato_assi":
        if not lock_termina.locked():
            velocita = settings["velocita_disegno"]

            try:
                s.sendall(f"muovi_motore|{index}|{asse}|{spostamento}|{velocita}".encode())
                ms = s.recv(4096).decode()
                stato_assi = eval(ms.split("|")[0])
                if ms.split("|")[1] != "nessuno":
                    save_log(ms.split("|")[1])
            except:
                settings["stato_connessione"] = "ERRORE"
                save_log("Errore con la connessione")

            if(stato_assi["Z_SX"]["stato_asse"] > 0): a_turtle_stampa.pencolor("#ff0000") # red
            elif(stato_assi["Z_SX"]["stato_asse"] < 0): a_turtle_stampa.pencolor("#00ff00") # green
            elif(stato_assi["Z_SX"]["stato_asse"] == 0): a_turtle_stampa.pencolor("#0000ff") # blue
            a_turtle_stampa.goto(stato_assi["X"]["stato_asse"]*settings["proporzione_disegno"]/100, stato_assi["Y"]["stato_asse"]*settings["proporzione_disegno"]/100)

            aggiorna_text()

    else:
        if not lock_termina.locked():
            sleep(settings["velocita_disegno"])
            stato_assi_simulazione[asse]["stato_asse"]+= spostamento

            if(stato_assi_simulazione["Z_SX"]["stato_asse"] > 0): a_turtle_simulazione.pencolor("#ff0000") # red
            elif(stato_assi_simulazione["Z_SX"]["stato_asse"] < 0): a_turtle_simulazione.pencolor("#00ff00") # green
            elif(stato_assi_simulazione["Z_SX"]["stato_asse"] == 0): a_turtle_simulazione.pencolor("#0000ff") # blue
            a_turtle_simulazione.goto(stato_assi_simulazione["X"]["stato_asse"]*settings["proporzione_disegno"]/100, stato_assi_simulazione["Y"]["stato_asse"]*settings["proporzione_disegno"]/100)


def muovi_motori_con_lock(indexs, assi, spostamenti, dict_da_usare):
    while lock_pausa.locked() and not lock_termina.locked(): pass
    muovi_motori_senza_lock(indexs, assi, spostamenti, dict_da_usare)

def muovi_motori_senza_lock(indexs, assi, spostamenti, dict_da_usare):
    global stato_assi
    global stato_assi_simulazione
    global lock_termina
    global lock_pausa


    if dict_da_usare == "stato_assi":
        if not lock_termina.locked():
            velocita = settings["velocita_disegno"]

            try:
                s.sendall(f"muovi_motori|{indexs[0]}|{indexs[1]}|{assi[0]}|{assi[1]}|{spostamenti[0]}|{spostamenti[1]}|{velocita}".encode())
                ms = s.recv(4096).decode()
                stato_assi = eval(ms.split("|")[0])
                if ms.split("|")[1] != "nessuno":
                    save_log(ms.split("|")[1])
            except:
                settings["stato_connessione"] = "ERRORE"
                save_log("Errore con la connessione")


            if(stato_assi["Z_SX"]["stato_asse"] > 0): a_turtle_stampa.pencolor("#ff0000") # red
            elif(stato_assi["Z_SX"]["stato_asse"] < 0): a_turtle_stampa.pencolor("#00ff00") # green
            elif(stato_assi["Z_SX"]["stato_asse"] == 0): a_turtle_stampa.pencolor("#0000ff") # blue
            a_turtle_stampa.goto(stato_assi["X"]["stato_asse"]*settings["proporzione_disegno"]/100, stato_assi["Y"]["stato_asse"]*settings["proporzione_disegno"]/100)

            aggiorna_text()
    else:
        if not lock_termina.locked():
            sleep(settings["velocita_disegno"])

            stato_assi_simulazione[assi[0]]["stato_asse"]+= spostamenti[0]
            stato_assi_simulazione[assi[1]]["stato_asse"]+= spostamenti[1]

            if(stato_assi_simulazione["Z_SX"]["stato_asse"] > 0): a_turtle_simulazione.pencolor("#ff0000") # red
            elif(stato_assi_simulazione["Z_SX"]["stato_asse"] < 0): a_turtle_simulazione.pencolor("#00ff00") # green
            elif(stato_assi_simulazione["Z_SX"]["stato_asse"] == 0): a_turtle_simulazione.pencolor("#0000ff") # blue
            a_turtle_simulazione.goto(stato_assi_simulazione["X"]["stato_asse"]*settings["proporzione_disegno"]/100, stato_assi_simulazione["Y"]["stato_asse"]*settings["proporzione_disegno"]/100)




"""
FINE FUNZIONI PER MUOVERE I MOTORI
"""


def muovi_due_motori(comandi, tipo_funzione_muovi_motore, dict_da_usare):
    
    asse = []
    spostamento = []
    index = []

    for comando in comandi.split("#"):
        asse.append(comando.split(":")[0])
        spostamento.append(int(comando.split(":")[1]))
        index.append(verifica_direzione(asse[-1], spostamento[-1], dict_da_usare))
    
    #il maggiore è sempre in posizione 0
    if abs(spostamento[0]) < abs(spostamento[1]):
        spostamento[0], spostamento[1] = spostamento[1], spostamento[0]
        asse[0], asse[1] = asse[1], asse[0]
        index[0], index[1] = index[1], index[0]
    
    if spostamento[1] == 0:
        for _ in range(abs(spostamento[0])): eval(f"muovi_motore_{tipo_funzione_muovi_motore}")(index[0], asse[0], abs(spostamento[0])//spostamento[0], dict_da_usare) #1 motore
    elif spostamento[0] == spostamento[1]:
        for _ in range (abs(spostamento[0])):
            eval(f"muovi_motori_{tipo_funzione_muovi_motore}")(index, asse, [abs(spostamento[0])//spostamento[0], abs(spostamento[1])//spostamento[1]], dict_da_usare) #2 motori
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
                    eval(f"muovi_motori_{tipo_funzione_muovi_motore}")(index, asse, [abs(spostamento[0])//spostamento[0], abs(spostamento[1])//spostamento[1]], dict_da_usare) #2
                else: eval(f"muovi_motore_{tipo_funzione_muovi_motore}")(index[0], asse[0], abs(spostamento[0])//spostamento[0], dict_da_usare) #1
                
                if ogni_quanto_impulso!= 0 and (i+a*impulsi_arrotondati)%ogni_quanto_impulso == 0 and differenza_impulsi!=0:
                    eval(f"muovi_motore_{tipo_funzione_muovi_motore}")(index[0], asse[0], differenza_impulsi//abs(differenza_impulsi), dict_da_usare) #1
                    differenza_impulsi -= differenza_impulsi//abs(differenza_impulsi)
                
    



def vai_incrementale(parametri, tipo_funzione_muovi_motore, dict_da_usare):
    parametri = [round(float(i)) for i in parametri]

    coordx = parametri[0]
    coordy = parametri[1]
    coordz = parametri[2]

    #print(f"coordinate########## X:{coordx} - Y: {coordy}")
    """movimento asse z"""
    muovi_due_motori(f"Z_SX:{coordz}#Z_DX:{coordz}", tipo_funzione_muovi_motore, dict_da_usare)
    """----------------"""
    """movimento asse x-y"""
    muovi_due_motori(f"X:{coordx}#Y:{coordy}", tipo_funzione_muovi_motore, dict_da_usare)
    """----------------"""
    #print(f'X:{stato_assi["X"]["stato_asse"]} -  Y:{stato_assi["Y"]["stato_asse"]} - Z:{stato_assi["Z_SX"]["stato_asse"]}')
    

def vai_lineare(parametri, tipo_funzione_muovi_motore, dict_da_usare):
    parametri = [round(float(i)) for i in parametri]

    coordx = parametri[0]
    coordy = parametri[1]
    coordz = parametri[2]

    if dict_da_usare == "stato_assi":
        vai_incrementale([-(stato_assi["X"]["stato_asse"]-coordx), -(stato_assi["Y"]["stato_asse"]-coordy), -(stato_assi["Z_SX"]["stato_asse"]-coordz)], tipo_funzione_muovi_motore, dict_da_usare)
    else:
        vai_incrementale([-(stato_assi_simulazione["X"]["stato_asse"]-coordx), -(stato_assi_simulazione["Y"]["stato_asse"]-coordy), -(stato_assi_simulazione["Z_SX"]["stato_asse"]-coordz)], tipo_funzione_muovi_motore, dict_da_usare)


def arco(parametri, tipo_funzione_muovi_motore, dict_da_usare):
    parametri = [round(float(i)) for i in parametri]

    raggio = parametri[0]
    angolo_iniziale = math.radians(parametri[1])
    angolo_finale = math.radians(parametri[2])

    if dict_da_usare == "stato_assi":
        coordx_centro = stato_assi["X"]["stato_asse"]
        coordy_centro = stato_assi["Y"]["stato_asse"]
        coordz = stato_assi["Z_SX"]["stato_asse"]
    else:
        coordx_centro = stato_assi_simulazione["X"]["stato_asse"]
        coordy_centro = stato_assi_simulazione["Y"]["stato_asse"]
        coordz = stato_assi_simulazione["Z_SX"]["stato_asse"]

    #da controllare  se è +1 o -1 per alzarlo
    """dal centro dell'arco, mi alzo un po' la z e mi sposto in un punto della circonferenza"""
    vai_incrementale([raggio*np.cos(angolo_iniziale),raggio*np.sin(angolo_iniziale), settings["pen_up_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    vai_incrementale([0, 0, settings["pen_down_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    """---------------------------"""
    """disegno l'arco"""
    for ang in np.linspace(angolo_iniziale,angolo_finale,int((angolo_finale-angolo_iniziale)*100)):
        vai_lineare([coordx_centro+raggio*np.cos(ang), coordy_centro+raggio*np.sin(ang), coordz], tipo_funzione_muovi_motore, dict_da_usare)
    """---------------------------"""
    """dal centro dell'arco, mi alzo un po' la z e mi sposto in un punto della circonferenza"""
    if dict_da_usare == "stato_assi":
        vai_lineare([coordx_centro, coordy_centro, stato_assi["Z_SX"]["stato_asse"]+settings["pen_up_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    else:
        vai_lineare([coordx_centro, coordy_centro, stato_assi_simulazione["Z_SX"]["stato_asse"]+settings["pen_up_punta"]], tipo_funzione_muovi_motore, dict_da_usare)

    vai_incrementale([0, 0, settings["pen_down_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    """---------------------------"""

def segmento(parametri, tipo_funzione_muovi_motore, dict_da_usare):
    parametri = [round(float(i)) for i in parametri]

    lunghezza = parametri[0]
    inclinazione = math.radians(parametri[1])

    vai_incrementale([lunghezza*np.cos(inclinazione), lunghezza*np.sin(inclinazione), 0], tipo_funzione_muovi_motore, dict_da_usare)

def collegamento(parametri, tipo_funzione_muovi_motore, dict_da_usare):
    parametri = [round(float(i)) for i in parametri]

    if dict_da_usare == "stato_assi":
        coordx_centro = stato_assi["X"]["stato_asse"]
        coordy_centro = stato_assi["Y"]["stato_asse"]
    else:
        coordx_centro = stato_assi_simulazione["X"]["stato_asse"]
        coordy_centro = stato_assi_simulazione["Y"]["stato_asse"]

    lunghezza = parametri[0]
    larghezza = parametri[1]
    inclinazione = math.radians(parametri[2])
    angolo = np.degrees(np.arctan(-1/(np.tan(inclinazione))))

    vai_incrementale([0,0,settings["pen_up_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    segmento([larghezza/2,angolo], tipo_funzione_muovi_motore, dict_da_usare)

    vai_incrementale([0,0,settings["pen_down_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    segmento([lunghezza, parametri[2]], tipo_funzione_muovi_motore, dict_da_usare) #disegniamo il primo segmento

    vai_incrementale([0,0,settings["pen_up_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    segmento([-larghezza,angolo], tipo_funzione_muovi_motore, dict_da_usare)

    vai_incrementale([0,0,settings["pen_down_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    segmento([lunghezza, 180+parametri[2]], tipo_funzione_muovi_motore, dict_da_usare)


    if dict_da_usare == "stato_assi":
        vai_lineare([coordx_centro, coordy_centro, stato_assi["Z_SX"]["stato_asse"]+settings["pen_up_punta"]], tipo_funzione_muovi_motore, dict_da_usare)
    else:
        vai_lineare([coordx_centro, coordy_centro, stato_assi_simulazione["Z_SX"]["stato_asse"]+settings["pen_up_punta"]], tipo_funzione_muovi_motore, dict_da_usare)

    vai_incrementale([0, 0, settings["pen_down_punta"]], tipo_funzione_muovi_motore, dict_da_usare)


def foro(parametri, tipo_funzione_muovi_motore, dict_da_usare):
    parametri = [round(float(i)) for i in parametri]

    profondita = parametri[0]

    vai_incrementale([0,0,profondita], tipo_funzione_muovi_motore, dict_da_usare)
    




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



def finestra_avvia_simulazione(values_editor):
    global stato_assi_simulazione
    global window_simulazione
    global canvas_simulazione
    global a_turtle_simulazione
    global lock_pausa
    global lock_termina
    global lock_pausa_istruzione

    try:
        lock_termina.release()
    except:
        pass

    try:
        lock_pausa.release()
    except:
        pass

    try:
        lock_pausa_istruzione.release()
    except:
        pass

    stato_assi_simulazione["X"]["stato_asse"] = 0
    stato_assi_simulazione["Y"]["stato_asse"] = 0
    stato_assi_simulazione["Z_DX"]["stato_asse"] = 0
    stato_assi_simulazione["Z_SX"]["stato_asse"] = 0

    vista_blocchi_column = [
        [sg.Text("BLOCCHI")],
        [sg.Listbox(values=[], enable_events=True, size=(40, 40), key="-BLOCCHI-")]
    ]

    vista_movimenti_column = [
        [sg.Text("VISTA MOVIMENTI")],
        [sg.Canvas(size=(600, 600), key='-CANVAS_SIMULAZIONE-')]
    ]

    layout_avvia = [
        [sg.Button("AVVIA"), sg.Button("STOP"), sg.Button("STOP ISTRUZIONE"), sg.Button("RIPRENDI")],  
        [sg.T("")],
        [sg.Text("BLOCCO DI PARTENZA"), sg.InputText(default_text="0", key="BLOCCO_PARTENZA")],
        [sg.Text("BLOCCO IN ESECUZIONE: ", key="-NBLOCCO-")],
        [sg.T("")],
        [sg.Column(vista_blocchi_column), sg.VSeperator(), sg.Column(vista_movimenti_column)]
    ]


    window_simulazione = sg.Window("AVVIA SIMULAZIONE", layout_avvia, modal=True, finalize=True, enable_close_attempted_event=True)

    canvas_simulazione = window_simulazione['-CANVAS_SIMULAZIONE-'].TKCanvas

    a_turtle_simulazione = turtle.RawTurtle(canvas_simulazione)
    a_turtle_simulazione.pencolor("#ff0000")  # Red
    a_turtle_simulazione.pendown()
    a_turtle_simulazione.goto(0,0)
    a_turtle_simulazione.clear()


    cod = [f"{e}: {a}" for e, a in enumerate(values_editor.split("\n"))]
    window_simulazione["-BLOCCHI-"].Update(cod)

    esegui_codice = None
    while True:
        event, values = window_simulazione.read()
        if event == "Exit" or event == sg.WIN_CLOSED or event == "-WINDOW CLOSE ATTEMPTED-":
            lock_termina.acquire(blocking=False)

            try:
                esegui_codice.join()
            except:
                pass

            break
        elif event == "AVVIA":
            try:
                thread_attivo = esegui_codice.is_alive()
            except:
                thread_attivo = False
            if not lock_pausa.locked() and not lock_termina.locked() and not lock_pausa_istruzione.locked() and not thread_attivo:
                stato_assi_simulazione["X"]["stato_asse"] = 0
                stato_assi_simulazione["Y"]["stato_asse"] = 0
                stato_assi_simulazione["Z_SX"]["stato_asse"] = 0
                stato_assi_simulazione["Z_DX"]["stato_asse"] = 0
                a_turtle_simulazione.goto(0,0)
                a_turtle_simulazione.clear()

                blocco_partenza = 0
                if values["BLOCCO_PARTENZA"].isnumeric():
                    blocco_partenza = int(values["BLOCCO_PARTENZA"])

                window_simulazione["BLOCCO_PARTENZA"].Update(f"{blocco_partenza}")  

                esegui_codice = EseguiCodice("con_lock", values_editor, "stato_assi_simulazione", blocco_partenza)
                esegui_codice.start()

        elif event == "STOP":
            lock_pausa.acquire(blocking=False)

        elif event == "STOP ISTRUZIONE":
            lock_pausa_istruzione.acquire(blocking=False)

        elif event == "RIPRENDI":
            try:
                lock_pausa.release()
            except:
                pass

            try:
                lock_pausa_istruzione.release()
            except:
                pass


    window_simulazione.close()


def finestra_avvia_stampa(values_editor):
    global stato_assi
    global window_stampa
    global canvas_stampa
    global a_turtle_stampa
    global lock_pausa
    global lock_termina
    global esegui_incremento
    global lock_pausa_istruzione

    try:
        lock_termina.release()
    except:
        pass

    try:
        lock_pausa.release()
    except:
        pass

    try:
        lock_pausa_istruzione.release()
    except:
        pass

    vista_blocchi_column = [
        [sg.Text("BLOCCHI")],
        [sg.Listbox(values=[], enable_events=True, size=(40, 40), key="-BLOCCHI-")]
    ]

    vista_movimenti_column = [
        [sg.Text("VISTA MOVIMENTI")],
        [sg.Canvas(size=(600, 600), key='-CANVAS_STAMPA-')]
    ]

    layout_avvia = [
        [sg.Button("GESTIONE MANUALE"), sg.Button("GESTIONE CONNESSIONE"), sg.Button("SET ZERO", button_color="red")],
        [sg.Button("AVVIA"), sg.Button("STOP"), sg.Button("STOP ISTRUZIONE"), sg.Button("RIPRENDI")],
        [sg.T("")],
        [sg.Text("X: ", size =(16, 1), key="X"), sg.Text("Y: ", size =(16, 1), key="Y"), sg.Text("Z: ", size =(16, 1), key="Z")],
        [sg.Text("FC X 1: ", size =(16, 1), key="FC X 1"),sg.Text("FC X 2: ", size =(16, 1), key="FC X 2"),sg.Text("FC Y 1: ", size =(16, 1), key="FC Y 1"),sg.Text("FC Y 2: ", size =(16, 1), key="FC Y 2"),sg.Text("FC Z 1: ", size =(16, 1), key="FC Z 1"),sg.Text("FC Z 2: ", size =(16, 1), key="FC Z 2")],
        [sg.T("")],
        [sg.Text("BLOCCO DI PARTENZA"), sg.InputText(default_text="0", key="BLOCCO_PARTENZA")],
        [sg.Text("BLOCCO IN ESECUZIONE: ", key="-NBLOCCO-")],
        [sg.T("")],
        [sg.Column(vista_blocchi_column), sg.VSeperator(), sg.Column(vista_movimenti_column)]
    ]


    window_stampa = sg.Window("AVVIA STAMPA", layout_avvia, modal=True, finalize=True, enable_close_attempted_event=True)

    canvas_stampa = window_stampa['-CANVAS_STAMPA-'].TKCanvas

    a_turtle_stampa = turtle.RawTurtle(canvas_stampa)
    a_turtle_stampa.pencolor("#ff0000")  # Red
    a_turtle_stampa.pendown()
    a_turtle_stampa.clear()

    cod = [f"{e}: {a}" for e, a in enumerate(values_editor.split("\n"))]
    window_stampa["-BLOCCHI-"].Update(cod)

    if settings["stato_connessione"] == "CONNESSO":
        try:
            s.sendall("altro".encode())
            ms = s.recv(4096).decode()
            stato_assi = eval(ms.split("|")[0])
            if ms.split("|")[1] != "nessuno":
                save_log(ms.split("|")[1])
        except:
            settings["stato_connessione"] = "ERRORE"
            save_log("Errore con la connessione")

        aggiorna_text()

    esegui_codice = None
    while True:
        event, values = window_stampa.read()
        if event == "Exit" or event == sg.WIN_CLOSED or event == "-WINDOW CLOSE ATTEMPTED-":
            lock_termina.acquire(blocking=False)

            try:
                esegui_codice.join()
            except:
                pass

            break
        
        elif event == "GESTIONE CONNESSIONE":
            finestra_gestione_connessione()
        
        elif event == "GESTIONE MANUALE":
            try:
                thread_attivo = esegui_codice.is_alive()
            except:
                thread_attivo = False

            if lock_pausa.locked() or not thread_attivo or lock_pausa_istruzione.locked():
                finestra_gestione_manuale()

        elif event == "SET ZERO":

            try:
                thread_attivo = esegui_codice.is_alive()
            except:
                thread_attivo = False

            try:
                thread_attivo_incremento = esegui_incremento.is_alive()
            except:
                thread_attivo_incremento = False

            if not lock_pausa.locked() and not lock_termina.locked() and not lock_pausa_istruzione.locked() and not thread_attivo and not thread_attivo_incremento:
                try:
                    s.sendall("set_zero".encode())
                    ms = s.recv(4096).decode()
                    stato_assi = eval(ms.split("|")[0])
                    if ms.split("|")[1] != "nessuno":
                        save_log(ms.split("|")[1])
                except:
                    settings["stato_connessione"] = "ERRORE"
                    save_log("Errore con la connessione")

                aggiorna_text()
                a_turtle_stampa.goto(0,0)
                a_turtle_stampa.clear()

        elif event == "AVVIA":
            try:
                thread_attivo = esegui_codice.is_alive()
            except:
                thread_attivo = False

            try:
                thread_attivo_incremento = esegui_incremento.is_alive()
            except:
                thread_attivo_incremento = False

            if not lock_pausa.locked() and not lock_pausa_istruzione.locked() and not lock_termina.locked() and not thread_attivo and not thread_attivo_incremento:
                a_turtle_stampa.clear()
                if settings["stato_connessione"] == "CONNESSO":
                    blocco_partenza = 0
                    if values["BLOCCO_PARTENZA"].isnumeric():
                        blocco_partenza = int(values["BLOCCO_PARTENZA"])

                    window_stampa["BLOCCO_PARTENZA"].Update(f"{blocco_partenza}")           

                    esegui_codice = EseguiCodice("con_lock", values_editor, "stato_assi", blocco_partenza)
                    esegui_codice.start()
                else:
                    save_log("Esecuzione non riuscita per problemi di connessione")

        elif event == "STOP":
            lock_pausa.acquire(blocking=False)

        elif event == "STOP ISTRUZIONE":
            lock_pausa_istruzione.acquire(blocking=False)

        elif event == "RIPRENDI":
            try:
                lock_pausa.release()
            except:
                pass

            try:
                lock_pausa_istruzione.release()
            except:
                pass
                


    window_stampa.close()




def finestra_spcb():
    global window_spcb

    menu_layout = [
        ['File',['New','Open','Save','Save As']],
        ['Esegui',['Simulazione', 'Stampa']],
        ['Impostazioni',['Cambia']],
        ['Log',['Visualizza', "Elimina"]]
    ]


    elenco_blocchi_inseriti = [
        [sg.Text('BLOCCHI INSERITI')], 
        [sg.Multiline(key='EDITOR', size=(50,20))]
    ]

    elenco_blocchi_disponibili = [
        [sg.Text('BLOCCHI DISPONIBILI')], 
        [sg.Button("VAI LINEARE", key="blocco_comando-vai_lineare")],
        [sg.Button("VAI INCREMENTALE", key="blocco_comando-vai_incrementale")],
        [sg.Button("SEGMENTO", key="blocco_comando-segmento")],
        [sg.Button("ARCO", key="blocco_comando-arco")],
        [sg.Button("COLLEGAMENTO", key="blocco_comando-collegamento")],
        [sg.Button("FORO", key="blocco_comando-foro")]
    ]



    layout_spcb = [[sg.Menu(menu_layout)],[sg.T("")]] + [[sg.Column(elenco_blocchi_disponibili), sg.VSeperator(), sg.Column(elenco_blocchi_inseriti)]]
    window_spcb = sg.Window("SPCB", layout_spcb, enable_close_attempted_event=True, finalize=True)

    while True:
        event, values = window_spcb.read()

        #print(event)

        if event == "Exit" or event == sg.WIN_CLOSED or event == "-WINDOW CLOSE ATTEMPTED-":
            scelta = scelta_salvataggio()

            if scelta != "Nulla":
                if scelta == "Si":
                    save_file(window=window_spcb, values=values)

                break

        elif event == "Cambia":
            finestra_impostazioni()

        elif event == "Simulazione":
            finestra_avvia_simulazione(values["EDITOR"])

        elif event == "Stampa":
            finestra_avvia_stampa(values["EDITOR"])

        elif event == "Open":
            open_file(window=window_spcb, values=values)

        elif event == "Save":
            save_file(window=window_spcb, values=values)

        elif event == "Save As":
            save_file_as(window=window_spcb, values=values)
        
        elif event == "New":
            new_file(window=window_spcb, values=values)

        elif event == "Visualizza":
            finestra_debug()

        elif event == "Elimina":
            with open(f"{dir_path}debug.txt",'w') as f:
                f.write("")


        # BLOCCHI
        elif "blocco_comando" in event:
            blocco = event.split("-")[1]
            parametri = ""
            for par in comandi_parametri[blocco]:
                parametri += f"{par},"

            parametri = parametri[:-1]

            if values["EDITOR"] == "":
                contenuto = f"{blocco}({parametri})"
            else:
                contenuto = values["EDITOR"] + "\n" + f"{blocco}({parametri})"

            window_spcb['EDITOR'].Update(contenuto)

    window_spcb.close()



def finestra_gestione_connessione():
    global stato_assi
    global s

    layout_gestione_connessione = [
        [sg.Text('IP', size =(15, 1)), sg.InputText(settings["ip"])],
        [sg.Text('PORTA', size =(15, 1)), sg.InputText(settings["porta"])],
        [sg.Button("CONNETTI"), sg.Button("DISCONNETTI")],
        [sg.Text(f'STATO: {settings["stato_connessione"]}', size =(25, 1), key="STATO_CONNESSIONE")]
    ]

    window = sg.Window('GESTIONE CONNESSIONE', layout_gestione_connessione, modal=True)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event=="Exit":
            break
        elif event == "CONNETTI":
            if settings["stato_connessione"] != "CONNESSO":
                try:
                    s = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
                    s.connect((values[0], int(values[1]))) # tupla --> indirizzo ip, porta
                    ms = s.recv(4096).decode()
                    stato_assi = eval(ms.split("|")[0])
                    if ms.split("|")[1] != "nessuno":
                        save_log(ms.split("|")[1])
                    aggiorna_text()
                    settings["stato_connessione"] = "CONNESSO"
                    settings["ip"] = values[0]
                    settings["porta"] = int(values[1])
                except:
                    settings["stato_connessione"] = "ERRORE"

            window["STATO_CONNESSIONE"].Update(f'STATO: {settings["stato_connessione"]}')

        elif event == "DISCONNETTI":
            try:
                s.close()
                settings["stato_connessione"] = "NON CONNESSO"
            except:
                settings["stato_connessione"] = "ERRORE"

            window["STATO_CONNESSIONE"].Update(f'STATO: {settings["stato_connessione"]}')

    window.close()



def finestra_gestione_manuale():
    global window_gestione_manuale
    global stato_assi
    global incremento_x_step
    global incremento_y_step
    global incremento_z_step
    global esegui_incremento

    colonna_x = [
        [sg.Text('INCREMENTO TOTALE X: ', size =(35, 1), key="INCREMENTOX")],
        [sg.Button("-", key="-X"), sg.Button("+", key="+X")]
    ]

    colonna_y = [
        [sg.Text('INCREMENTO TOTALE Y: ', size =(35, 1), key="INCREMENTOY")],
        [sg.Button("-", key="-Y"), sg.Button("+", key="+Y")]
    ]

    colonna_z = [
        [sg.Text('INCREMENTO TOTALE Z: ', size =(35, 1), key="INCREMENTOZ")],
        [sg.Button("-", key="-Z"), sg.Button("+", key="+Z")]
    ]

    layout_gestione_manuale = [
        [sg.Text("X: ", size =(16, 1), key="X"), sg.Text("Y: ", size =(16, 1), key="Y"), sg.Text("Z: ", size =(16, 1), key="Z")],
        [sg.Text("FC X 1: ", size =(16, 1), key="FC X 1"),sg.Text("FC X 2: ", size =(16, 1), key="FC X 2"),sg.Text("FC Y 1: ", size =(16, 1), key="FC Y 1"),sg.Text("FC Y 2: ", size =(16, 1), key="FC Y 2"),sg.Text("FC Z 1: ", size =(16, 1), key="FC Z 1"),sg.Text("FC Z 2: ", size =(16, 1), key="FC Z 2")],
        [sg.T("")],
        [sg.Column(colonna_x), sg.VSeperator(), sg.Column(colonna_y), sg.VSeperator(), sg.Column(colonna_z)]
    ]


    window_gestione_manuale = sg.Window('GESTIONE MANUALE', layout_gestione_manuale, modal=True, finalize=True)

    incremento_x_step = 0
    incremento_y_step = 0
    incremento_z_step = 0

    esegui_incremento = EseguiStep()
    esegui_incremento.start()


    if settings["stato_connessione"] == "CONNESSO":
        try:
            s.sendall("altro".encode())
            ms = s.recv(4096).decode()
            stato_assi = eval(ms.split("|")[0])
            if ms.split("|")[1] != "nessuno":
                save_log(ms.split("|")[1])
        except:
            settings["stato_connessione"] = "ERRORE"
            save_log("Errore con la connessione")
            
        aggiorna_text()

    while True:
        event, values = window_gestione_manuale.read()

        #print(event)

        if event == sg.WIN_CLOSED or event=="Exit" or event == None:

            try:
                esegui_incremento.running = False
            except:
                pass
            
            try:
                esegui_incremento.join()
            except:
                pass


            break

        elif event == "+X":
            lista_step.append(f"vai_incrementale({settings['numero_step_singolo_movimento']},0,0)")
            aggiorna_totale_incrementi(f"vai_incrementale({settings['numero_step_singolo_movimento']},0,0)")

        elif event == "-X":
            lista_step.append(f"vai_incrementale({-settings['numero_step_singolo_movimento']},0,0)")
            aggiorna_totale_incrementi(f"vai_incrementale({-settings['numero_step_singolo_movimento']},0,0)")

        elif event == "+Y":
            lista_step.append(f"vai_incrementale(0,{settings['numero_step_singolo_movimento']},0)")
            aggiorna_totale_incrementi(f"vai_incrementale(0,{settings['numero_step_singolo_movimento']},0)")

        elif event == "-Y":
            lista_step.append(f"vai_incrementale(0,{-settings['numero_step_singolo_movimento']},0)")
            aggiorna_totale_incrementi(f"vai_incrementale(0,{-settings['numero_step_singolo_movimento']},0)")

        elif event == "+Z":
            lista_step.append(f"vai_incrementale(0,0,{settings['numero_step_singolo_movimento']})")
            aggiorna_totale_incrementi(f"vai_incrementale(0,0,{settings['numero_step_singolo_movimento']})")

        elif event == "-Z":
            lista_step.append(f"vai_incrementale(0,0,{-settings['numero_step_singolo_movimento']})")
            aggiorna_totale_incrementi(f"vai_incrementale(0,0,{-settings['numero_step_singolo_movimento']})")



    window_gestione_manuale.close()


def aggiorna_totale_incrementi(com):
    global incremento_x_step
    global incremento_y_step
    global incremento_z_step

    parametri = com.split("(")[1].replace(")", "").split(",")
    parametri = [round(float(i)) for i in parametri]

    incremento_x_step += parametri[0]
    incremento_y_step += parametri[1]
    incremento_z_step += parametri[2]

    window_gestione_manuale["INCREMENTOX"].Update(f"INCREMENTO TOTALE X: {incremento_x_step}")
    window_gestione_manuale["INCREMENTOY"].Update(f"INCREMENTO TOTALE Y: {incremento_y_step}")
    window_gestione_manuale["INCREMENTOZ"].Update(f"INCREMENTO TOTALE Z: {incremento_z_step}")


##----FILE MENU FUNCTIONS--------------------------------##

def new_file(window, values): # CTRL+N shortcut key

    scelta = scelta_salvataggio()

    if scelta != "Nulla":
        if scelta == "Si":
            save_file(window=window, values=values)


        settings["filename"] = None
        window['EDITOR'].update(value='')
        

def open_file(window, values): # CTRL+O shortcut key


    scelta = scelta_salvataggio()

    if scelta != "Nulla":
        if scelta == "Si":
            save_file(window=window, values=values)


        ''' Open a local file in the editor '''
        try: # 'OUT OF INDEX' error in trinket if 'CANCEL' button is pressed
            filename = sg.popup_get_file('File Name:', title='Open', no_window=True)
        except:
            return
        if filename not in (None,'', ()):
            settings["filename"] = filename
            with open(filename,'r') as f:
                file_text = f.read()
            window['EDITOR'].update(value=file_text)


def save_file(window, values): # CTRL+S shortcut key
    ''' Save active file. If new, then calls the `save_file_as` function '''
    filename = settings['filename']
    if filename not in (None,'', ()):
        with open(filename,'w') as f:
            f.write(values['EDITOR'])
    else:
        save_file_as(window, values)

def save_file_as(window, values):
    ''' Save the active file as another file, also called for new files '''
    try: # 'OUT OF INDEX' error in Trinket if 'CANCEL' button is clicked
        filename = sg.popup_get_file('Save File', save_as=True, no_window=True)
    except:
        return

    if filename not in (None,'', ()):
        settings["filename"] = filename
        with open(filename,'w') as f:
            f.write(values['EDITOR'])


def scelta_salvataggio():
    layout_gestione_manuale = [
        [sg.Text("Vuoi salvare il file attualmente aperto?")],
        [sg.Button("Si"),sg.Button("No")]
    ]


    window = sg.Window(title="",layout=layout_gestione_manuale, modal=True)

    scelta = "Nulla"
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event=="Exit":
            scelta = "Nulla"
            break
        
        elif event == "Si":
            scelta = "Si"
            break

        elif event == "No":
            scelta = "No"
            break

    window.close()

    return scelta

def finestra_impostazioni():
    layout_finestra_impostazioni = [
        [sg.Text('VELOCITÀ DISEGNO', size =(30, 1)), sg.InputText(default_text=settings["velocita_disegno"], key="velocita_disegno")], 
        [sg.Text('PROPORZIONE DISEGNO', size =(30, 1)), sg.InputText(default_text=settings["proporzione_disegno"], key="proporzione_disegno")],
        [sg.Text('UNITÀ DI MISURA', size =(30, 1)), sg.InputText(default_text=settings["unita_di_misura"], key="unita_di_misura")],
        [sg.Text('N. STEP SINGOLO MOVIMENTO', size =(30, 1)), sg.InputText(default_text=settings["numero_step_singolo_movimento"], key="numero_step_singolo_movimento")],
        [sg.Text('N. PUNTI PER ARCO', size =(30, 1)), sg.InputText(default_text=settings["numero_punti_arco"], key="numero_punti_arco")],
        [sg.Text('ALTEZZA PENUP PUNTA (-)', size =(30, 1)), sg.InputText(default_text=settings["pen_up_punta"], key="pen_up_punta")],
        [sg.Text('ALTEZZA PENDOWN PUNTA (+)', size =(30, 1)), sg.InputText(default_text=settings["pen_down_punta"], key="pen_down_punta")],
        [sg.Button("SALVA")]
    ]


    window = sg.Window(title="IMPOSTAZIONI",layout=layout_finestra_impostazioni, modal=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event=="Exit":
            break
        
        elif event == "SALVA":

            if isfloat(values["velocita_disegno"]):
                settings["velocita_disegno"] = float(values["velocita_disegno"])

            if isfloat(values["proporzione_disegno"]):
                settings["proporzione_disegno"] = float(values["proporzione_disegno"])
            
            if values["numero_step_singolo_movimento"].isnumeric():
                settings["numero_step_singolo_movimento"] = int(values["numero_step_singolo_movimento"])

            if values["numero_punti_arco"].isnumeric():
                settings["numero_punti_arco"] = int(values["numero_punti_arco"])

            if values["pen_up_punta"].isnumeric():
                settings["pen_up_punta"] = int(values["pen_up_punta"])

            if values["pen_down_punta"].isnumeric():
                settings["pen_down_punta"] = int(values["pen_down_punta"])

            if values["unita_di_misura"] in conversione_unita_di_misura:
                settings["unita_di_misura"] = values["unita_di_misura"]
            else:
                settings["unita_di_misura"] = "cmm"
                save_log("Unità di misura non valida")
                
            break
            

    window.close()


def isfloat(num):
    try:
        float(num)
        return True
    except:
        return False


def aggiorna_text():

    conversione = conversione_unita_di_misura[settings["unita_di_misura"]]

    try:
        x = stato_assi["X"]["stato_asse"]/conversione
        y = stato_assi["Y"]["stato_asse"]/conversione
        z = stato_assi["Z_SX"]["stato_asse"]/conversione
        window_stampa["X"].Update(f"X: {x}")
        window_stampa["Y"].Update(f"Y: {y}")
        window_stampa["Z"].Update(f"Z: {z}")


        x1 = stato_assi["X"]["stato_finecorsa"][0]
        x2 = stato_assi["X"]["stato_finecorsa"][1]
        window_stampa["FC X 1"].Update(f"FC X 1: {x1}")
        window_stampa["FC X 2"].Update(f"FC X 2: {x2}")
        
        y1 = stato_assi["Y"]["stato_finecorsa"][0]
        y2 = stato_assi["Y"]["stato_finecorsa"][1]
        window_stampa["FC Y 1"].Update(f"FC Y 1: {y1}")
        window_stampa["FC Y 2"].Update(f"FC Y 2: {y2}")

        z1 = stato_assi["Z_SX"]["stato_finecorsa"][0]
        z2 = stato_assi["Z_SX"]["stato_finecorsa"][1]
        window_stampa["FC Z 1"].Update(f"FC Z 1: {z1}")
        window_stampa["FC Z 2"].Update(f"FC Z 2: {z2}")

    except:
        pass

    try:
        x = stato_assi["X"]["stato_asse"]/conversione
        y = stato_assi["Y"]["stato_asse"]/conversione
        z = stato_assi["Z_SX"]["stato_asse"]/conversione
        window_gestione_manuale["X"].Update(f"X: {x}")
        window_gestione_manuale["Y"].Update(f"Y: {y}")
        window_gestione_manuale["Z"].Update(f"Z: {z}")


        x1 = stato_assi["X"]["stato_finecorsa"][0]
        x2 = stato_assi["X"]["stato_finecorsa"][1]
        window_gestione_manuale["FC X 1"].Update(f"FC X 1: {x1}")
        window_gestione_manuale["FC X 2"].Update(f"FC X 2: {x2}")
        
        y1 = stato_assi["Y"]["stato_finecorsa"][0]
        y2 = stato_assi["Y"]["stato_finecorsa"][1]
        window_gestione_manuale["FC Y 1"].Update(f"FC Y 1: {y1}")
        window_gestione_manuale["FC Y 2"].Update(f"FC Y 2: {y2}")

        z1 = stato_assi["Z_SX"]["stato_finecorsa"][0]
        z2 = stato_assi["Z_SX"]["stato_finecorsa"][1]
        window_gestione_manuale["FC Z 1"].Update(f"FC Z 1: {z1}")
        window_gestione_manuale["FC Z 2"].Update(f"FC Z 2: {z2}")
    except:
        pass



def finestra_debug():
    with open(f"{dir_path}debug.txt",'r') as f:
        file_text = f.readlines()

    layout_debug = [
        [sg.Listbox(values=file_text, enable_events=True, size=(80, 60), key="-DEGUB-")]
    ]

    window = sg.Window('DEGUB', layout_debug, modal=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event=="Exit":
            break

    window.close()



def save_log(errore):
    with open(f"{dir_path}debug.txt",'a') as f:
        f.write(f"{datetime.datetime.now()}: {errore}\n")




class EseguiCodice(thr.Thread):
    def __init__(self, tipo_funzione, codice, dict_da_usare, num_istruzione_partenza):
        thr.Thread.__init__(self)
        self.tipo_funzione = tipo_funzione
        self.codice = codice
        self.dict_da_usare = dict_da_usare
        self.num_istruzione_partenza = num_istruzione_partenza
    
    def run(self):

        for i, istruzione in enumerate(self.codice.split("\n")):

                if not lock_termina.locked():
                    if i >= self.num_istruzione_partenza:

                        while lock_pausa_istruzione.locked() and not lock_termina.locked(): pass

                        if self.dict_da_usare == "stato_assi":
                            window_stampa["-NBLOCCO-"].Update(f"BLOCCO IN ESECUZIONE: {i}")
                        else:
                            window_simulazione["-NBLOCCO-"].Update(f"BLOCCO IN ESECUZIONE: {i}")

                        istruzione = istruzione.replace(" ", "")

                        if "#" not in istruzione and istruzione != "":

                            try:
                                comando = istruzione.split("(")[0]
                                parametri = istruzione.split("(")[1].replace(")", "").split(",")
                            
                                conversione = conversione_unita_di_misura[settings["unita_di_misura"]]
                                parametri = [round(float(i)*conversione) for i in parametri]

                                comandi_funzioni[comando](parametri, self.tipo_funzione, self.dict_da_usare)
                            except:
                                save_log(f"Blocco n. {i} non corretto!")
                
                else:
                    break
        
        
    


class EseguiStep(thr.Thread):
    def __init__(self):
        thr.Thread.__init__(self)
        self.running = True
    
    def run(self):
        global lista_step

        while self.running:
            if settings["stato_connessione"] == "CONNESSO":
                if len(lista_step) > 0:
                    step = lista_step.pop(0)

                    comando = step.split("(")[0]
                    parametri = step.split("(")[1].replace(")", "").split(",")

                    conversione = conversione_unita_di_misura[settings["unita_di_misura"]]
                    parametri = [round(float(i)*conversione) for i in parametri]

                    comandi_funzioni[comando](parametri, "senza_lock", "stato_assi")

            else:
                lista_step = []
                save_log("Esecuzione non riuscita per problemi di connessione")




def main():
    finestra_spcb()


if __name__ == "__main__":
    main()