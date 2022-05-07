"""
Creazione oscilloscopio con arduino
"""


#inclusione librerie
import turtle
from turtle import Screen, Turtle
from PIL import Image
import serial
import time
#----------------------------------


#avvio comunicazione seriale con la porta a cui è collegato l'arduino uno
arduino = serial.Serial('/dev/ttyACM0',9600)     
time.sleep(1)
#----------------------------------

#inizializzazione finestra di turtle
screen = turtle.Screen()
screen.title("GRAFICO")
screen.setworldcoordinates(-50, -50, 50, 50)
screen.bgpic("/home/famiglia-bianco/Scrivania/Isa/oscilloscopio/sfondo_oscilloscopio.gif")
#screen.bgcolor('orange')
screen.cv._rootwindow.resizable(False, False)   #blocco la ridimensione della finestra
#----------------------------------


#definizione variabili
PUNTO_MASSIMO = 50
condizione_while=True
x = 0
y = 0
DELAY_SEGNALE = 1
#----------------------------------


#definizione funzione per settaggio parametri iniziali
def punto_iniziale():
    global x
    global y
    x=-48
    y=0
    screen.clearscreen()  #pulisco lo schermo
    screen.bgpic("/home/famiglia-bianco/Scrivania/Isa/oscilloscopio/sfondo_oscilloscopio.gif")
    #screen.bgcolor('orange')
    turtle.penup()  #alzo la penna
    turtle.goto(x,y)   #muovo la penna al punto desiderato
    turtle.pendown()   #abbasso la penna
    turtle.color("red")  #imposto la penna di colore rosso
#----------------------------------

"""
Proporzione:
valore:1023=x:MAX
x = MAX*valore/1023
"""

#definizione funzione per disegno grafico
def oscilloscopio(valore):
    global x
    global y
    valore=int(valore)

    print("x: "+ str(x) + ", y: "+ str(y) + ", valore: "+ str(valore))
    y = PUNTO_MASSIMO*valore/1023
    #turtle.goto(x,y)   #vado alle coordinate x e y indicate
    x+= DELAY_SEGNALE    #arrotondiamo il valore della x
    turtle.goto(x,y)   #vado alle coordinate x e y indicate
    if(x>50):   #se si va fuori dal grafico si resetta tutto
        punto_iniziale()
#----------------------------------

#definizione funzione per cambio valore della variabile f
def set_condizione_while():
    global condizione_while
    condizione_while=False
#----------------------------------


#definizione main
def main(): 
    valore = 0

    global condizione_while
    condizione_while=True
    
    punto_iniziale()   #inizializzazione schermata

    while(condizione_while==True):
        turtle.listen()   #impostiamo il monitor in ascolto della premuta di qualche tasto
        turtle.onkey(set_condizione_while, "space")   #se si preme il tasto space eseguo la funzione set_condizione_while
        stringa = arduino.readline()
        #valore = int(input("inserire il valore da 0 a 1023"))
        stringa = str(stringa)
        stringa = stringa.replace("b'", "")
        stringa = stringa.split('\\')[0]
        valore = int(stringa)
        print(valore)
        oscilloscopio(valore)   #eseguo la funzione per disegnare il grafico
       
    screen.mainloop()   #lascio il monitor aperto anche dopo l'esecuzione
#----------------------------------

main()    #esecuzione main






