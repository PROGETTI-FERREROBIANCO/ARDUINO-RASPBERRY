"""
INCLUSIONE LIBRERIE
"""

from os import read
import Lettere
import serial
import time
from RPi import GPIO
import datetime


"""
DEFINIZIONE LETTERE
"""

#------------------------------------------------------------

# ORs <-    orizzontale verso sinistra          --> ridefinito 'a'
# ORd ->    orizzontale verso destra            --> ridefinito 'b'

#    ^
# Va |      verticale verso alto                --> ridefinito 'c'

# Vb |      verticale verso basso               --> ridefinito 'd'  
#    v

# OBas  \   obliquo alto a sinistra             --> ridefinito 'e'

# OBbs  /   obliquo basso a sinistra            --> ridefinito 'f'

# OBad  /   obliquo alto a destra               --> ridefinito 'g'

# OBbd  \   obliquo basso a destra              --> ridefinito 'h'

#------------------------------------------------------------

# SORs <-    spazio orizzontale verso sinistra  --> ridefinito 'i'
# SORd ->    spazio orizzontale verso destra    --> ridefinito 'j'

#     ^
# SVa |      spazio verticale verso alto        --> ridefinito 'k'

# SVb |      spazio verticale verso basso       --> ridefinito 'l'
#     v

# SOBas  \   spazio obliquo alto a sinistra     --> ridefinito 'm'

# SOBbs  /   spazio obliquo basso a sinistra    --> ridefinito 'n'

# SOBad  /   spazio obliquo alto a destra       --> ridefinito 'o'

# SOBbd  \   spazio obliquo basso a destra      --> ridefinito 'p'

#------------------------------------------------------------


"""
SETTAGGIO VARIABILI E PARAMETRI
"""

# PIN DELL'ARDUINO DEI SENSORI DI FINE CORSA 
PIN_MAX_Z = b'22\r\n'
PIN_MIN_Z = b'23\r\n'
PIN_MAX_X = b'24\r\n'
PIN_MIN_X = b'25\r\n'
PIN_MAX_Y = b'26\r\n'
PIN_MIN_Y = b'27\r\n'

# PIN DEL RASPBERRY DI PRESENZA ERRORE
PIN_ERRORE = 21

# PIN DEL RASPBERRY DI MOVIMENTO MOTORI
PIN_STEP_MOTORE_ASSE_Y = 20
PIN_STEP_MOTORE_ASSE_X = 16
PIN_STEP_MOTORE_ASSE_Z1 = 12  # Z1 e' il motore di sinistra
PIN_STEP_MOTORE_ASSE_Z2 = 25  # Z2 e' il motore di destra

# PIN DEL RASPBERRY DI SENSO DI ROTAZIONE DEI MOTORI
PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y = 24
PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X = 23
PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1 = 18
PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2 = 26

# PIN DEL RASPBERRY DI ABILITAZIONE MOTORI
PIN_ABILITAZIONE_MOTORE_ASSE_Y = 19
PIN_ABILITAZIONE_MOTORE_ASSE_X = 13
PIN_ABILITAZIONE_MOTORE_ASSE_Z1 = 6
PIN_ABILITAZIONE_MOTORE_ASSE_Z2 = 5

# SETUP PIN
GPIO.setmode(GPIO.BCM)  #tipo di riferimento, numerazione della cpu
GPIO.setwarnings(False)
GPIO.setup(PIN_ERRORE, GPIO.IN)  #imposto il pin di rilevazione dell errore come ingresso
GPIO.setup(PIN_STEP_MOTORE_ASSE_Y, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_STEP_MOTORE_ASSE_X, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_STEP_MOTORE_ASSE_Z1, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_STEP_MOTORE_ASSE_Z2, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_ABILITAZIONE_MOTORE_ASSE_Y, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_ABILITAZIONE_MOTORE_ASSE_X, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_ABILITAZIONE_MOTORE_ASSE_Z1, GPIO.OUT)  #imposto pin come uscita
GPIO.setup(PIN_ABILITAZIONE_MOTORE_ASSE_Z2, GPIO.OUT)  #imposto pin come uscita

# SETUP PIN A LOW
GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.LOW)
GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.LOW)
GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, GPIO.LOW)
GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, GPIO.LOW)
GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, GPIO.LOW)
GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, GPIO.LOW)

# SETUP SERIALE ARDUINO
arduino = serial.Serial('/dev/ttyACM0',9600)

# SETUP PER CODIFCA LETTERA
codifica_lettere = Lettere.codificaLettere()

# CREAZIONE FILE DI ERRORE
file_errori = open("file_errori.txt", "w")  #file dove saranno salvati gli errori generati dalle istruzioni
file_input = open("input.txt", 'r')

# se il motore gira in senso orario il blocco sale
# se il motore gira in senso antiorario il blocco scende
# nel nostro caso salire vuol dire andare verso il motore

# DEFINIZIONE VARIABILI SENSO DI ROTAZIONE 
SENSO_DI_ROTAZIONE_ORARIO = GPIO.LOW
SENSO_DI_ROTAZIONE_ANTIORARIO = GPIO.HIGH

# DEFINIZIONE VARIABILE DI NUMERO DI IMPULSI PER CODIFICARE UNO SPOSTAMENTO
NUM_IMPULSI_PER_SPOSTAMENTO = 500

# DEFINIZIONE VARIABILE DI VELOCITA' DI SCRITTURA
TEMPO_DI_INTERVALLO_TRA_IMPULSI = 0.002

# DEFINIZIONE VARIABILI ABILITAZIONE LETTURA ERRORE
tempo_errore = datetime.datetime.now()

# DEFINIZIONE VARIABILE PER NON TOCCARE IL FINECORSA
DISTANZA_FINECORSA = 500


"""
DEFINIZIONE FUNZIONI DEL PROGRAMMA
"""

# FUNZIONE PER IL MOVIMENTO DELL'ASSE X
def movimentoAsseX():
    GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
    time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
    GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
    time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)

# FUNZIONE PER IL MOVIMENTO DELL'ASSE Y
def movimentoAsseY():
    GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
    time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
    time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)

# FUNZIONE PER IL MOVIMENTO DELL'ASSE Z
def movimentoAsseZ():
    GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.HIGH)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.HIGH)
    time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.LOW)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.LOW)
    time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)

# FUNZIONE PER IL MOVIMENTO DEGLI ASSI X E Y
def movimentoAsseXY():
    GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
    time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
    GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
    time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
# FUNZIONE PER MUOVERSI VERSO SINISTRA

def a():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ORARIO)
    for _ in range(NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseX()

# FUNZIONE PER MUOVERSI VERSO DESTRA
def b():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseX()
    
# FUNZIONE PER MUOVERSI VERSO L'ALTO
def c():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseY()

# FUNZIONE PER MUOVERSI VERSO IL BASSO
def d():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ORARIO)
    for _ in range(NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseY()

# FUNZIONE PER MUOVERSI VERSO L'ALTO E SINISTRA
def e():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseXY()

# FUNZIONE PER MUOVERSI VERSO IL BASSO E SINISTRA
def f():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ORARIO)
    for _ in range(NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseXY()

# FUNZIONE PER MUOVERSI VERSO L'ALTO E DESTRA
def g():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ANTIORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseXY()

# FUNZIONE PER MUOVERSI VERSO L'BASSO E DESTRA
def h():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ANTIORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ORARIO) # io metto orario perche' il piatto si deve spostare nella direzione del motore
    for _ in range(NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseXY()

# FUNZIONE PER SALTO VERSO SINISTRA
def i():
    spostamentoAlto()
    a()
    spostamentoBasso()

# FUNZIONE PER SALTO VERSO DESTRA
def j():
    spostamentoAlto()
    b()
    spostamentoBasso()

# FUNZIONE PER SALTO VERSO AVANTI
def k():
    spostamentoAlto()
    c()
    spostamentoBasso()

# FUNZIONE PER SALTO VERSO INDIETRO
def l():
    spostamentoAlto()
    d()
    spostamentoBasso()

# FUNZIONE PER SALTO VERSO ALTO SINISTRA
def m():
    spostamentoAlto()
    e()
    spostamentoBasso()

# FUNZIONE PER SALTO VERSO BASSO SINISTRA
def n():
    spostamentoAlto()
    f()
    spostamentoBasso()

# FUNZIONE PER SALTO VERSO ALTO DESTRA
def o():
    spostamentoAlto()
    g()
    spostamentoBasso()

# FUNZIONE PER SALTO VERSO BASSO DESTRA
def p():
    spostamentoAlto()
    h()
    spostamentoBasso()

# FUNZIONE PER ANDARE VERSO ALTO
def spostamentoAlto():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, SENSO_DI_ROTAZIONE_ORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, SENSO_DI_ROTAZIONE_ORARIO)
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseZ()
        cont+=1

# FUNZIONE PER ANDARE VERSO BASSO
def spostamentoBasso():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, SENSO_DI_ROTAZIONE_ANTIORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, SENSO_DI_ROTAZIONE_ANTIORARIO)
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        movimentoAsseZ()
        cont+=1

# FUNZIONE PER VEDERE SE IL BLOCCO HA TOCCATO UN FINECORSA
def trovaErrore():
    global tempo_errore
    errore = "nessuno"
    if(GPIO.input(PIN_ERRORE) == 1 and ((tempo_errore+ datetime.timedelta(hours = 0, minutes = 0, seconds = 1, microseconds=0)) < datetime.datetime.now())):
        tempo_errore = datetime.datetime.now()
        print("errore rilevato")
        pin_errore = arduino.readline()
        
        if(pin_errore==PIN_MAX_Z):
            errore = "max_z"
            file_errori.write("errore di fine corsa asse z max\n")
        elif(pin_errore==PIN_MIN_Z):
            errore = "min_z"
            file_errori.write("errore di fine corsa asse z min\n")
        elif(pin_errore==PIN_MAX_X):
            errore = "max_x"
            file_errori.write("errore di fine corsa asse x max\n")
        elif(pin_errore==PIN_MIN_X):
            errore = "min_x"
            file_errori.write("errore di fine corsa asse x min\n")
        elif(pin_errore==PIN_MAX_Y):
            errore = "max_y"
            file_errori.write("errore di fine corsa asse y max\n")
        elif(pin_errore==PIN_MIN_Y):
            errore = "min_y"
            file_errori.write("errore di fine corsa asse y min\n")
        else:
            file_errori.write("errore non identificato\n")
        print(errore)

    return errore

# FUNZIONE PER SPOSTARE IL BLOCCO DELL'ASSE DELLE X TUTTO VERSO IL PUNTO DI INIZIO
def inizializzazioneAsseX():

    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ORARIO)
    while(trovaErrore()!="max_x"):
        movimentoAsseX()

    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(DISTANZA_FINECORSA):
        movimentoAsseX()

# FUNZIONE PER SPOSTARE IL BLOCCO DELL'ASSE DELLE Y TUTTO VERSO IL PUNTO DI INIZIO
def inizializzazioneAsseY():

    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ORARIO)
    while(trovaErrore()!="max_y"):
        movimentoAsseY()

    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(DISTANZA_FINECORSA):
        movimentoAsseY()

# FUNZIONE PER SPOSTARE IL BLOCCO DELL'ASSE DELLE Z TUTTO VERSO IL PUNTO DI INIZIO
def inizializzazioneAsseZ():

    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, SENSO_DI_ROTAZIONE_ORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, SENSO_DI_ROTAZIONE_ORARIO)

    while(trovaErrore()!="max_z"):
        movimentoAsseZ()

    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, SENSO_DI_ROTAZIONE_ANTIORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(DISTANZA_FINECORSA):
        movimentoAsseZ()

# SETTAGGIO PUNTA RISPETTO ASSE X
def OfFsEt_x(offset_x):
    
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(offset_x):
        movimentoAsseX()

# SETTAGGIO PUNTA RISPETTO ASSE Y
def OfFsEt_y(offset_y):
     
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(offset_y):
        movimentoAsseY()

# SETTAGGIO PUNTA RISPETTO ASSE Z
def OfFsEt_z(offset_z):
 
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, SENSO_DI_ROTAZIONE_ANTIORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, SENSO_DI_ROTAZIONE_ANTIORARIO)
    for _ in range(offset_z):
        movimentoAsseZ()



# FUNZIONE PER INIZIALIZZARE LA PUNTA ALL'INIZIO DI OGNI ASSE
def calcolOffset_settaggioPunta():
    
    inizializzazioneAsseX()
    inizializzazioneAsseY()
    inizializzazioneAsseZ()



# FUNZIONE PER SETTARE LA PUNTA NELL'ANGOLO IN ALTO A SINISTRA DEL FOGLIO
def settaggioPuntaAngoloSinistraFoglio():
    #La coordinata X dell'angolo del foglio in alto a sinistra: 13619
    #La coordinata Y dell'angolo del foglio in alto a sinistra: 44663
    #La coordinata Z dell'angolo del foglio in alto a sinistra: 23138
    inizio_foglio_x = 13619   # ---> SI ANDRANNO A MODIFICARE QUESTI PARAMETRI
    inizio_foglio_y = 44663
    inizio_foglio_z = 31253

    OfFsEt_x(inizio_foglio_x)
    OfFsEt_y(inizio_foglio_y)
    OfFsEt_z(inizio_foglio_z)

# FUNZIONE PER ACQUISIRE LA SERIE DI LETTERE CHE CODIFICANO IL CARATTERE ED ESEGUIRE LE ADEGUATE FUNZIONI
def disegna_frase(carattere):
    conversione = codifica_lettere.getCodifica(carattere)
    print(conversione)
    for elemento in range(len(conversione)):
        print(conversione[elemento])
        eval(str(conversione[elemento])+ "()")

#FUNZIONE PER FAR ALZARE LA PENNA DAL FOGLIO A FINE SCRITTA
def alzaPenna():
    for _ in range(5):
       spostamentoAlto()
    
# FUNZIONE PER LA CHIUSURA DEI DIVERSI FILE
def chiusuraFile():
    file_input.close()
    file_errori.close()

# FUNZIONE PER FERMARE I MOTORI
def fermaTutto():
    GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.HIGH)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.HIGH)

    GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.LOW)
    GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.LOW)

    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, GPIO.LOW)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, GPIO.LOW)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, GPIO.LOW)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, GPIO.LOW)

# FUNZIONE MAIN CHE RICHIAMA TUTTE LE ALTRE FUNZIONI
def main():
    print("esecuzione funzione calcolOffset_settaggioPunta()")
    calcolOffset_settaggioPunta()
    print("esecuzione funzione settaggioPuntaAngoloSinistraFoglio()")
    settaggioPuntaAngoloSinistraFoglio()
    print("esecuzione funzione di scrittura lettere")
    time.sleep(10)
    testo = file_input.readlines()
    print(f"testo: {testo}")
    for indice in range(len(testo)):
        for elemento in testo[indice]:
            disegna_frase(elemento)
            if(trovaErrore()!="nessuno"):
                fermaTutto()
                break
    alzaPenna()
    chiusuraFile()
    fermaTutto()


if __name__ == "__main__":
    main()
    print("fine esecuzione programma")



