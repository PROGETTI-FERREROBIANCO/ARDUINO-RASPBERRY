import time
from RPi import GPIO

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

# DEFINIZIONE VARIABILI SENSO DI ROTAZIONE 
SENSO_DI_ROTAZIONE_ORARIO = GPIO.LOW
SENSO_DI_ROTAZIONE_ANTIORARIO = GPIO.HIGH


# SETUP PIN
GPIO.setmode(GPIO.BCM)  #tipo di riferimento, numerazione della cpu
GPIO.setwarnings(False)
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

# DEFINIZIONE VARIABILE DI NUMERO DI IMPULSI PER CODIFICARE UNO SPOSTAMENTO
NUM_IMPULSI_PER_SPOSTAMENTO = 100

# DEFINIZIONE VARIABILE DI VELOCITA' DI SCRITTURA
TEMPO_DI_INTERVALLO_TRA_IMPULSI = 0.002

# DEFINIZIONE FUNZIONI DEL PROGRAMMA

def a():
    print("Vado avanti")
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ORARIO)
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1

def b():
    print("Vado indietro") 
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ANTIORARIO)
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1
    

def c():
    print("Vado avanti Y") 
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ANTIORARIO)
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1


def d():
    print("Vado inditero Y") 
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ORARIO)
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1


def e():
    print("obliquo alto sinistra")
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ANTIORARIO) # io metto antiorario perche' il piatto si deve spostare nel
#la direzione opposta di dove e' il motore
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        # in questo caso io devo andare in alto a sinistra
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1


def f():
    print("obliquo basso sinistra")
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ORARIO) # io metto orario perche' il piatto si deve spostare nella direz
#ione del motore
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        # in questo caso io devo andare in basso a sinistra
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1


def g():
    print("obliquo alto destra")
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ANTIORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ANTIORARIO) # io metto antiorario perche' il piatto si deve spostare nel
#la direzione opposta di dove e' il motore
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        # in questo caso io devo andare in alto a destra
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1


def h():
    print("obliquo basso destra")
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_X, SENSO_DI_ROTAZIONE_ANTIORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Y, SENSO_DI_ROTAZIONE_ORARIO) # io metto orario perche' il piatto si deve spostare nella direz
#ione del motore
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        # in questo caso io devo andare in basso a destra
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.HIGH)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_X, GPIO.LOW)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Y, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1

def i():
    spostamentoAlto()
    a()
    spostamentoBasso()


def j():
    spostamentoAlto()
    b()
    spostamentoBasso()


def k():
    spostamentoAlto()
    c()
    spostamentoBasso()


def l():
    spostamentoAlto()
    d()
    spostamentoBasso()


def m():
    spostamentoAlto()
    e()
    spostamentoBasso()


def n():
    spostamentoAlto()
    f()
    spostamentoBasso()


def o():
    spostamentoAlto()
    g()
    spostamentoBasso()


def p():
    spostamentoAlto()
    h()
    spostamentoBasso()


def spostamentoAlto():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, SENSO_DI_ROTAZIONE_ORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, SENSO_DI_ROTAZIONE_ORARIO)
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.HIGH)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.LOW)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1

def spostamentoBasso():
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z1, SENSO_DI_ROTAZIONE_ANTIORARIO)
    GPIO.output(PIN_SENSO_ROTAZIONE_MOTORE_ASSE_Z2, SENSO_DI_ROTAZIONE_ANTIORARIO)
    cont=0
    while(cont<NUM_IMPULSI_PER_SPOSTAMENTO):
        GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.HIGH)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.HIGH)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Z1, GPIO.LOW)
        GPIO.output(PIN_STEP_MOTORE_ASSE_Z2, GPIO.LOW)
        time.sleep(TEMPO_DI_INTERVALLO_TRA_IMPULSI)
        cont+=1



spostamentoAlto()
